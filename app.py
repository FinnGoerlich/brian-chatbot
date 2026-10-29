"""Brian: a minimal local chatbot backed by the Anthropic Claude API.

Run with:  uvicorn app:app --host 127.0.0.1 --port 8000
The API key is read only from the ANTHROPIC_API_KEY environment variable.
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Literal

import anthropic
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

MODEL = os.environ.get("BRIAN_MODEL", "claude-sonnet-5-5")
MAX_TOKENS = 1024
SYSTEM_PROMPT = "You are Brian, a helpful assistant."
STATIC_DIR = Path(__file__).parent / "static"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("brian")

_client: anthropic.AsyncAnthropic | None = None


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
    yield


app = FastAPI(title="Brian", lifespan=lifespan)


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
