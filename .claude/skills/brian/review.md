# /brian review <case code>

Goal: a `Brian/open_questions.txt` that lists what only the case team can still explain, loaded into the case's Brian artifact so interviews can start.

## 1. Check the setup

1. Normalise the case code: trim, uppercase, spaces to `-`. Allowed characters: letters, digits and `_ - . ~ : @ +`. Ask again if it doesn't fit.
2. Confirm the working directory is the case's synced SharePoint folder (it holds the case's top-level folders, such as `01_Kickoff`, `02_SteerCos`). If it looks like a home directory, Desktop or a parent of many cases, stop and ask the user to start Claude Code in the case folder.
3. Do the client-approval check from SKILL.md.
4. If `Brian/brian.json` exists, read it. If its `caseCode` differs from the one given, stop and ask. If it has an `artifactUrl`, this is a re-review: you'll update that artifact instead of creating one.

## 2. Inventory the file tree

1. List every file, skipping `Brian/`, Office lock files (`~$*`), `*.tmp` and `desktop.ini`. Note path, type, size and modified date. Keep the inventory in your scratchpad, not in SharePoint.
2. Report the totals to the user (files, folders, types, date range) before reading in depth.

## 3. Read the files

1. Start with the documents that carry decisions: final reports, steering committee decks and minutes, trackers, handover documents, the newest version of each model. Then meeting notes, emails saved as `.msg`, and the rest.
2. For a large tree, give each top-level folder to a subagent. Each returns a list of gaps in the format below, with the file paths that show them. Merge and de-duplicate the results yourself.
3. Read Office files with the `docx`, `pptx` and `xlsx` skills, or with python-docx, python-pptx and openpyxl, read only. Don't run macros. Read PDFs directly.
4. For each gap, note what the files show and which files they are.

## 4. Decide what to ask

Ask only what a team member can answer and the files can't. Look for:

- **Scope and objectives**: scope changes without a recorded decision, targets without a derivation.
- **Decisions**: changes of direction, paused or cancelled work, choices between options, with no "why" in the files.
- **Data and versions**: competing versions of a baseline, model or report; unexplained exclusions or adjustments; which file is authoritative.
- **People**: key client stakeholders and their roles and influence (ask about roles, not personal details).
- **Results and handover**: what was delivered, what was handed over, open owners.
- **Reuse and learnings**: reusable models and templates and any restrictions on them; what worked and what didn't.
- **Follow-ons**: next steps or opportunities mentioned but not described.

Aim for 10 to 25 questions. Order themes by importance, and questions within a theme likewise. Phrase each so it can be answered in a few sentences. Don't ask what a file already answers clearly.

On a re-review:
- Keep every existing question, with the same ID and wording. Never renumber or delete a question; the case context refers to the IDs.
- Add new questions at the end of their theme, with the next free ID (Q13, Q14, ...).
- Read `Brian/context.md` if it exists, and don't add questions it already settles.

## 5. Write the files

1. Create `Brian/`, `Brian/files/` and `Brian/raw_transcripts/` if they don't exist.
2. Write `Brian/open_questions.txt` in the format in [formats.md](formats.md). Show the user the question list and let them edit it before you load it into the artifact.

## 6. Create or update the artifact

**New case (no `artifactUrl`):**
1. Copy `template/brian.html`, `template/system_prompt.txt` and `template/context_prompt.txt` into a new folder in your scratchpad. In the copy of `brian.html`, change `<title>Brian</title>` to `<title>Brian <CASE CODE></title>`.
2. Publish the copied `brian.html` with the `Artifact` tool:
   - `files`: `{"system_prompt.txt": <copied path>, "context_prompt.txt": <copied path>}`
   - `capabilities`: `{"sample": {"images": true}, "db": {}, "user": {}, "downloads": true, "assets": {"upload": "interact"}}`
   - `icon`: `"chat"`
   - `description`: "Case context interviews for <CASE CODE>."
3. Note the artifact URL from the result.

**Existing case:** keep the URL. If the template changed since the artifact was created, republish the copied files to that `url` (read it first with the `Artifact` tool, as it requires).

## 7. Load the questions into the artifact

1. Write a JSON file in your scratchpad with the fields below, so the long text doesn't need to be typed inline.
2. New case: `ArtifactData` `set` on collection `cases`, `doc_id` `<CODE>`, `file_path` that JSON, with: `caseCode`, `caseName`, `questions` (the full text of `Brian/open_questions.txt`), `questionsUpdatedAt` (now, epoch ms), `context` (`""`), `mergedChats` (`[]`), `sharepointFolder` (the case folder's name only, never a local path).
3. Existing case: `get` the document first, then `update` only `questions`, `questionsUpdatedAt` and `caseName`, with `if_version`. Never overwrite `context` or `mergedChats` here.
4. Read the document back once and check that `questions` matches the file.

## 8. Record and report

1. Write `Brian/brian.json` (format in [formats.md](formats.md)), keeping `createdAt` on a re-review and setting `lastReview` to now.
2. Tell the user:
   - the artifact link and the number of questions (new ones, on a re-review);
   - to share the artifact only with the case team, through its Share menu, at Contributor level so they can run interviews and upload files;
   - that team members open it, enter the case code and click "Start a new interview";
   - to run `/brian sync <CODE>` after interviews.
