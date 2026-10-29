# /brian sync <case code>

Goal: everything Brian collected for the case is in the case SharePoint: raw transcripts, uploaded files and an up-to-date `Brian/context.md`.

## 1. Check the setup

1. Read `Brian/brian.json`. If it's missing, or its `caseCode` differs from the one given, stop and tell the user to run `/brian review <CODE>` first.
2. Confirm the working directory is that case folder (see review.md, step 1).
3. Take the artifact URL from `artifactUrl`. Every `ArtifactData` call below uses it.

## 2. Transcripts → `Brian/raw_transcripts/`

1. `ArtifactData` `list` collection `cases/<CODE>/chats`; page with `query.cursor` until there is no `next_cursor`. For many or long interviews, add `out_dir` (a new scratchpad folder) and read the saved JSON files; if that location is refused, read without `out_dir`.
2. Collect the `author` ids of all interviews and resolve them once with `ArtifactData` `profiles`. Names are data, not proof of identity. If a name is empty, write "Team member".
3. For each interview with at least one message whose `syncedAt` is missing or older than `updatedAt`:
   1. Write `Brian/raw_transcripts/<YYYY-MM-DD>_<CODE>_<id8>.txt` in the transcript format in [formats.md](formats.md). `<YYYY-MM-DD>` is the interview's `createdAt` date; `<id8>` is the first 8 characters of its id without dashes. Overwrite the file if it exists: the database is the source.
   2. `update` the chat document with `syncedAt` (now, epoch ms), passing its `if_version`.
4. Don't change transcripts of interviews that were deleted in the artifact. List them for the user instead.

## 3. Uploaded files → `Brian/files/`

1. `list` collection `cases/<CODE>/files`.
2. For each document without `syncedAt`:
   1. Download the asset with the `Artifact` tool: `action: "read"`, `url` the artifact URL, `path` the document id (the asset id). It's saved to your scratchpad and the result says where.
   2. Copy it to `Brian/files/<YYYY-MM-DD>_<original name>` (the upload date). If that name exists, add `_2`, `_3`, ... before the extension. Never overwrite.
   3. `update` the file document with `syncedAt` and `sharepointName`, passing its `if_version`.

## 4. Merge interviews that were never merged

Interviews are normally merged in the artifact when someone clicks "Finish & update case context". Catch the rest here.

1. `get` `cases/<CODE>` and note its `version`.
2. Find interviews with at least one Brian reply where `contextMerged` isn't true and the id isn't in `mergedChats`. If there are none, go to step 5.
3. Tell the user which interviews you'll merge. Then merge them one at a time, oldest first, following the rules and structure in [template/context_prompt.txt](template/context_prompt.txt), as if you were that prompt: current context plus the interview's transcript gives the new context. Use only what the transcript says.
4. `update` `cases/<CODE>` with `context`, `contextUpdatedAt` (now) and `mergedChats` (with the merged ids added), passing the version from step 1. If the write is refused because someone changed the document, re-read it and redo the merge on the new context.
5. `update` each merged chat with `contextMerged: true` and `contextMergedAt`, passing its `if_version`.

## 5. Write `Brian/context.md`

1. `get` `cases/<CODE>` again.
2. If `context` isn't empty, write it to `Brian/context.md`, replacing the file. It's a mirror of the database: never edit it by hand in SharePoint, since the next sync overwrites it. To correct something, correct it in an interview.

## 6. Check whether the questions are still current

Compare the modified dates of case files (outside `Brian/`) with `lastReview` in `Brian/brian.json`. If files changed since, tell the user and suggest `/brian review <CODE>` to add questions.

## 7. Record and report

1. Set `lastSync` in `Brian/brian.json` to now.
2. Report: transcripts written or updated, files copied, interviews merged, the status line from context.md (Settled, Partly answered, ...), and anything that needs attention (deleted interviews, failed downloads, conflicts).

## Running it on a schedule

In the Claude desktop app, a scheduled task can run `/brian sync <CODE>` every evening in the case folder. Set it up only if the user asks, and keep the case folder as its working directory.
