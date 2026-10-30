"""Write one Brian interview as a raw transcript in the format of formats.md.

Usage:
  python write_transcript.py <chat.json> <transcripts dir> --case-code CODE --case-name NAME
                             [--interviewee NAME]

<chat.json> is one interview document as ArtifactData saves it with `out_dir`
(the document body; the file name is the interview id). The transcript is written to
<transcripts dir>/<YYYY-MM-DD>_<CODE>_<id8>.txt, replacing an existing file of that name,
and the path is printed. Message text is written exactly as stored.
"""
import argparse
import json
from datetime import datetime
from pathlib import Path


def stamp(ms):
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M") if ms else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("chat_json", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--case-code", required=True)
    ap.add_argument("--case-name", required=True)
    ap.add_argument("--interviewee", default="Team member")
    args = ap.parse_args()

    chat = json.loads(args.chat_json.read_text(encoding="utf-8"))
    chat_id = args.chat_json.stem
    id8 = chat_id.replace("-", "")[:8]
    messages = chat.get("messages") or []
    created = chat.get("createdAt") or 0
    merged_at = chat.get("contextMergedAt") if chat.get("contextMerged") else None

    lines = [
        "BRIAN CASE CONTEXT INTERVIEW - TRANSCRIPT",
        f"Case code: {args.case_code}",
        f"Case: {args.case_name}",
        f"Interview: {id8}",
        f"Interviewee: {args.interviewee or 'Team member'}",
        f"Interview started: {stamp(created)}",
        f"Transcript saved: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Messages: {len(messages)}",
        f"Merged into case context: {'yes, on ' + stamp(merged_at)[:10] if merged_at else 'no'}",
        "",
        'Speakers: "Brian" is the AI interviewer; "Interviewee" is the case team member.',
        'The interview closes with a "# Project knowledge record"; settled open questions have a "Recorded for Qnn:" line.',
        "",
        "=" * 60,
        "",
    ]
    for m in messages:
        speaker = "Interviewee" if m.get("role") == "user" else "Brian"
        when = stamp(m.get("at") or 0)
        lines.append(f"[{speaker}]" + (f" {when}" if when else ""))
        lines.append(m.get("content") or "(no text)")
        for f in m.get("files") or []:
            lines.append(f"Attached: {f.get('name', 'file')} (asset {f.get('assetId', '')})")
        lines.append("")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    day = datetime.fromtimestamp(created / 1000).strftime("%Y-%m-%d") if created else "undated"
    out = args.out_dir / f"{day}_{args.case_code}_{id8}.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
