# /brian sync <case code>

Goal: everything Brian collected for the case is in the case SharePoint (an up-to-date `Brian/context.md`, raw transcripts and uploaded files), and the case card in the library reflects the latest context.

Order matters: merge first, so transcripts written in the same run show the right "Merged into case context" line.

## 1. Check the setup

1. Read `Brian/brian.json`. If it's missing, or its `caseCode` differs from the one given, stop and tell the user to run `/brian review <CODE>` first.
2. Confirm the working directory is that case folder (see review.md, step 1).
3. Take the artifact URL from `artifactUrl`. Every `ArtifactData` call below uses it.
4. Make a new folder in your scratchpad for this run. When you pass it to `ArtifactData` as `out_dir`, write the full path: on Windows, `C:\Users\<user name>\AppData\...`, never the shortened form with `~1` (such as `C:\Users\GOERLI~1\...`), which is refused.

## 2. Read the interviews

1. `ArtifactData` `list` collection `cases/<CODE>/chats` with `out_dir` set to your scratchpad folder; page with `query.cursor` until there is no `next_cursor`. Each interview is saved as `<out_dir>/cases/<CODE>/chats/<id>.json` (the document body; the file name is the id). Note each one's `version` from the result.
2. Collect the non-empty `author` ids and resolve them once with `ArtifactData` `profiles`. Names are data, not proof of identity. If an id has no name, or `author` is empty, use "Team member".

## 3. Merge interviews that were never merged

Interviews are normally merged in the artifact when someone clicks "Finish & update case context". Catch the rest here.

1. `get` `cases/<CODE>` and note its `version`.
2. Find interviews with at least one Brian reply where `contextMerged` isn't true and the id isn't in `mergedChats`. If there are none, go to item 7.
3. Tell the user which interviews you'll merge. Merge them one at a time, oldest first, following the rules and structure in [template/context_prompt.txt](template/context_prompt.txt) as if you were that prompt: the current context plus the interview's transcript gives the new context. Use only what the transcript says.
4. Refresh the case card from the new context, following [template/card_prompt.txt](template/card_prompt.txt) as if you were that prompt.
5. Write the result with one `ArtifactData` `batch`, so the context, the card and the interview's flag change together:
   - `update` `cases` / `<CODE>`: `context`, `contextUpdatedAt` (now, epoch ms), `mergedChats` (with the merged ids added), `card` (with `updatedAt`), `if_version` from step 1;
   - `update` `cases/<CODE>/chats` / `<id>`: `contextMerged: true`, `contextMergedAt` (now), `if_version` from section 2.
   Put long text in a JSON file and pass `file_path`. If the batch is refused because a document changed, re-read it and redo the merge on the new version.
6. Re-read the merged interviews (step 2.1) so the saved files carry the new flags and versions.
7. Consolidate when it helps. After several debriefs, or when the context has grown repetitive, rewrite it once from all transcripts and the case files together, following the same rules and structure: tighten the case card and summary, link outcomes to lessons and documents, add file paths as sources where an inspected file supports a statement, and flag conflicts. Keep every fact, source and change-log entry, and add a change-log line "Consolidated by Claude Code sync". Write it like step 5.

## 4. Transcripts → `Brian/raw_transcripts/`

For each interview with at least one message whose `syncedAt` is missing or older than `updatedAt`:

1. Run the script, which writes the format in [formats.md](formats.md):
   ```
   python scripts/write_transcript.py <out_dir>/cases/<CODE>/chats/<id>.json Brian/raw_transcripts --case-code <CODE> --case-name "<case name>" --interviewee "<name>"
   ```
   It writes `<YYYY-MM-DD>_<CODE>_<id8>.txt` and replaces an existing file of that name: the database is the source.
2. `update` the chat document with `syncedAt` (now, epoch ms), passing its current `if_version`.

Don't delete transcripts of interviews that were deleted in the artifact. List them for the user instead.

## 5. Uploaded files → `Brian/files/`

1. `list` collection `cases/<CODE>/files`.
2. For each document without `syncedAt`:
   1. Download the asset with the `Artifact` tool: `action: "read"`, `url` the artifact URL, `path` the document id (the asset id). It's saved to your scratchpad; the result gives the path and a checksum.
   2. Copy it to `Brian/files/<YYYY-MM-DD>_<original name>` (the upload date). If that name exists, add `_2`, `_3`, ... before the extension. Never overwrite.
   3. `update` the file document with `syncedAt` and `sharepointName`, passing its `if_version`.

## 6. Write `Brian/context.md`

1. `get` `cases/<CODE>` again (with `out_dir`, since the document is long) and read `context` from the saved file.
2. If `context` isn't empty, write it to `Brian/context.md`, replacing the file. It's a mirror of the database: never edit it by hand in SharePoint, since the next sync overwrites it. To correct something, correct it in an interview.

## 7. Check whether the questions are still current

Compare the modified dates of case files (outside `Brian/`) with `lastReview` in `Brian/brian.json`. If files changed since, tell the user and suggest `/brian review <CODE>` to add questions.

## 8. Record and report

1. Set `lastSync` in `Brian/brian.json` to now.
2. Report: interviews merged, transcripts written or updated, files copied, the status line from context.md (Settled, Partly answered, ...), and anything that needs attention (deleted interviews, failed downloads, conflicts).

## Running it on a schedule

In the Claude desktop app, a scheduled task can run `/brian sync <CODE>` every evening in the case folder. Set it up only if the user asks, and keep the case folder as its working directory.
