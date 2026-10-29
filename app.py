"""Brian: a minimal chatbot backed by the Anthropic Claude API.

Run locally with:  uvicorn app:app --host 127.0.0.1 --port 8000
The API key is read only from the ANTHROPIC_API_KEY environment variable.
Login is enabled when BRIAN_LOGIN_PASSWORD is set (see 20261029_README.md).
"""

import hmac
import html
import json
import logging
import os
import secrets
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Literal
from urllib.parse import parse_qs

import anthropic
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

MODEL = os.environ.get("BRIAN_MODEL", "claude-sonnet-5-5")
MAX_TOKENS = 1024
SYSTEM_PROMPT = "You are Brian, a helpful assistant."
STATIC_DIR = Path(__file__).parent / "static"

ON_RENDER = bool(os.environ.get("RENDER"))
LOGIN_EMAIL = os.environ.get("BRIAN_LOGIN_EMAIL", "").strip().lower()
LOGIN_PASSWORD = os.environ.get("BRIAN_LOGIN_PASSWORD", "")
LOGIN_ENABLED = bool(LOGIN_EMAIL and LOGIN_PASSWORD)
SESSION_SECRET = os.environ.get("BRIAN_SESSION_SECRET") or secrets.token_urlsafe(32)
MAX_FAILED_LOGINS = 5
LOCKOUT_SECONDS = 15 * 60
OPEN_PATHS = {"/login", "/logout", "/healthz"}

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("brian")

_client: anthropic.AsyncAnthropic | None = None
_failed_logins: dict[str, list[float]] = {}


def get_client() -> anthropic.AsyncAnthropic | None:
    """Return a shared client, or None if ANTHROPIC_API_KEY is not set."""
    global _client
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return None
    if _client is None:
        _client = anthropic.AsyncAnthropic(api_key=api_key)
    return _client


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        log.error(
            "ANTHROPIC_API_KEY is not set. Brian will start, but chat requests "
            "will fail until you set it and restart. See 20261029_README.md."
        )
    else:
        log.info("Brian ready. Model: %s", MODEL)
    if LOGIN_ENABLED:
        log.info("Login is enabled.")
    elif ON_RENDER:
        log.error("BRIAN_LOGIN_EMAIL / BRIAN_LOGIN_PASSWORD are not set. Brian stays locked until you set them.")
    else:
        log.info("Login is disabled (BRIAN_LOGIN_PASSWORD not set). Fine for local use only.")
    yield


app = FastAPI(title="Brian", lifespan=lifespan)


# ---------- Login ----------

@app.middleware("http")
async def require_login(request: Request, call_next):
    path = request.url.path
    if path in OPEN_PATHS:
        return await call_next(request)
    if ON_RENDER and not LOGIN_ENABLED:
        return PlainTextResponse("Brian is locked: set BRIAN_LOGIN_EMAIL and BRIAN_LOGIN_PASSWORD "
                                 "in the host's environment settings.", status_code=503)
    if LOGIN_ENABLED and not request.session.get("user"):
        if path.startswith("/api/"):
            return JSONResponse({"error": "login required"}, status_code=401)
        return RedirectResponse("/login", status_code=303)
    return await call_next(request)


# Added after the auth middleware so it wraps it and request.session is available there.
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie="brian_session",
    max_age=7 * 24 * 3600,
    same_site="lax",
    https_only=ON_RENDER,
)


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def is_locked_out(ip: str) -> bool:
    now = time.monotonic()
    recent = [t for t in _failed_logins.get(ip, []) if now - t < LOCKOUT_SECONDS]
    _failed_logins[ip] = recent
    return len(recent) >= MAX_FAILED_LOGINS


def login_page(error: str = "", status_code: int = 200) -> HTMLResponse:
    page = (STATIC_DIR / "login.html").read_text(encoding="utf-8")
    error_html = f'<p class="error" role="alert">{html.escape(error)}</p>' if error else ""
    return HTMLResponse(page.replace("<!--ERROR-->", error_html), status_code=status_code)


@app.get("/login")
async def login_form(request: Request):
    if not LOGIN_ENABLED or request.session.get("user"):
        return RedirectResponse("/", status_code=303)
    return login_page()


@app.post("/login")
async def login_submit(request: Request):
    if not LOGIN_ENABLED:
        return RedirectResponse("/", status_code=303)
    ip = client_ip(request)
    if is_locked_out(ip):
        return login_page("Too many failed attempts. Try again in 15 minutes.", 429)

    form = parse_qs((await request.body()).decode("utf-8", errors="replace"))
    email = form.get("email", [""])[0].strip().lower()
    password = form.get("password", [""])[0]
    email_ok = hmac.compare_digest(email.encode(), LOGIN_EMAIL.encode())
    password_ok = hmac.compare_digest(password.encode(), LOGIN_PASSWORD.encode())
    if email_ok and password_ok:
        _failed_logins.pop(ip, None)
        request.session["user"] = LOGIN_EMAIL
        return RedirectResponse("/", status_code=303)

    _failed_logins.setdefault(ip, []).append(time.monotonic())
    log.warning("Failed login attempt from %s", ip)
    return login_page("Wrong email or password.", 401)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login" if LOGIN_ENABLED else "/", status_code=303)


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.get("/api/config")
async def config():
    return {"login": LOGIN_ENABLED}


# ---------- Chat ----------

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=100_000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=500)


def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def normalise(messages: list[ChatMessage]) -> list[dict]:
    """Merge consecutive same-role turns and drop a leading assistant turn."""
    merged: list[dict] = []
    for m in messages:
        if merged and merged[-1]["role"] == m.role:
            merged[-1]["content"] += "\n\n" + m.content
        else:
            merged.append({"role": m.role, "content": m.content})
    while merged and merged[0]["role"] != "user":
        merged.pop(0)
    return merged


async def stream_reply(messages: list[dict]) -> AsyncIterator[str]:
    client = get_client()
    if client is None:
        yield sse("error", {"message": "Brian isn't connected yet: the ANTHROPIC_API_KEY "
                            "environment variable is not set on the server. Set it and restart."})
        return
    if not messages or messages[-1]["role"] != "user":
        yield sse("error", {"message": "The last message must come from you."})
        return

    try:
        async with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=messages,
            output_config={"effort": "low"},
        ) as stream:
            async for text in stream.text_stream:
                yield sse("delta", {"text": text})
            final = await stream.get_final_message()
        if final.stop_reason == "refusal":
            yield sse("error", {"message": "Brian can't help with that request."})
            return
        yield sse("done", {"stop_reason": final.stop_reason})
    except anthropic.AuthenticationError:
        log.error("Anthropic API rejected the API key (401).")
        yield sse("error", {"message": "The API key was rejected (401). Check that "
                            "ANTHROPIC_API_KEY is a valid, active key and restart the server."})
    except anthropic.PermissionDeniedError:
        log.error("Anthropic API denied permission (403).")
        yield sse("error", {"message": "This API key doesn't have permission to use that model (403)."})
    except anthropic.NotFoundError:
        log.error("Model not found: %s", MODEL)
        yield sse("error", {"message": f"The model '{MODEL}' wasn't found. Check BRIAN_MODEL."})
    except anthropic.RateLimitError:
        log.warning("Rate limited by Anthropic API (429).")
        yield sse("error", {"message": "Brian is being rate limited (429). Wait a moment and try again."})
    except anthropic.APIConnectionError:
        log.warning("Could not reach the Anthropic API.")
        yield sse("error", {"message": "Couldn't reach the Anthropic API. Check your internet connection."})
    except anthropic.APIStatusError as e:
        log.error("Anthropic API error %s: %s", e.status_code, getattr(e, "type", ""))
        yield sse("error", {"message": f"The Anthropic API returned an error ({e.status_code}). Please try again."})
    except Exception:
        log.exception("Unexpected error while streaming a reply")
        yield sse("error", {"message": "Something went wrong on the server. Please try again."})


@app.post("/api/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        stream_reply(normalise(req.messages)),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
