# /brian review <case code>

Goal: the case is in the Brian library, ready for debriefs and for Brian Ask: a `Brian/open_questions.txt` listing what only the case team can still explain, a first case card, and digests of the files that matter.

## 1. Check the setup

1. Normalise the case code: trim, uppercase, spaces to `-`. Allowed characters: letters, digits and `_ - . ~ : @ +`. Ask again if it doesn't fit.
2. Confirm the working directory is the case's synced SharePoint folder (it holds the case's top-level folders, such as `01_Kickoff`, `02_SteerCos`). If it looks like a home directory, Desktop or a parent of many cases, stop and ask the user to start Claude Code in the case folder.
3. Do the client-approval check from SKILL.md.
4. If `Brian/brian.json` exists, read it. If its `caseCode` differs from the one given, stop and ask. Its `artifactUrl` is the library; this is a re-review.
5. If there is no `brian.json`, ask the user for the Brian library link (a `claude.ai/artifact/...` URL). Read it once with the `Artifact` tool to check it opens. Only if the team has no library yet, create one as in step 7.

## 2. Inventory the file tree

1. List every file, skipping `Brian/`, Office lock files (`~$*`), `*.tmp` and `desktop.ini`. Note path, type, size and modified date. Keep the inventory in your scratchpad, not in SharePoint.
2. Report the totals to the user (files, folders, types, date range) before reading in depth.

## 3. Read the files

1. Start with the documents that carry decisions: final reports, steering committee decks and minutes, trackers, handover documents, the newest version of each model. Then meeting notes, emails saved as `.msg`, and the rest.
2. For a large tree, give each top-level folder to a subagent. Each returns gaps in the format below and digests of its important files, with paths. Merge and de-duplicate the results yourself.
3. Read Office files with the `docx`, `pptx` and `xlsx` skills, or with python-docx, python-pptx and openpyxl, read only. Don't run macros. Read PDFs directly.
4. For each gap, note what the files show and which files they are.

## 4. Decide what to ask

The debrief covers four linked blocks: project context, outcomes, procurement know-how and key documents. The open questions are a map of material gaps for it, not a questionnaire. Ask only what a team member can answer and the files can't. Look for:

- **Project context**: scope changes without a recorded decision, targets without a derivation.
- **Outcomes**: results without a definition, stage (identified, negotiated, implemented, realized), baseline, currency or period; competing figures; what stayed open at handover.
- **Know-how**: changes of direction, paused or cancelled work, choices between options, with no "why" in the files; what to repeat or avoid.
- **Key documents**: competing versions of a baseline, model or report; which file is authoritative; reusable models and templates and any restrictions on them.
- **People**: key client stakeholders, their roles and influence (roles, not personal details).

Aim for 10 to 25 questions, ordered by theme and importance. Phrase each so it can be answered in a few sentences. Don't ask what a file already answers clearly.

On a re-review:
- Keep every existing question, with the same ID and wording. Never renumber or delete a question; the case context refers to the IDs.
- Add new questions at the end of their theme, with the next free ID.
- Read `Brian/context.md` if it exists, and don't add questions it already settles.

## 5. Write the files

1. Create `Brian/`, `Brian/files/` and `Brian/raw_transcripts/` if they don't exist.
2. Write `Brian/open_questions.txt` in the format in [formats.md](formats.md). Show the user the question list and let them edit it before you load it.

## 6. Write the first case card and the file digests

1. **Case card** (format in [formats.md](formats.md)): fill it from the files: client, industry (shown as the practice area), functional area, geography, period, case type, a 2-4 sentence summary, and key results, lessons and documents only where the files state them, with their stage and evidence basis ("per final report"). The functional area matters most, since Brian Ask matches new cases on it first: use one short name, such as "Procurement", "PMO & value capture" or "Pricing", and reuse the names other cases in the library already use. Keep industry names short and reused too ("Logistics", "Chemicals"), since Brian Ask filters the case cards by functional area and by industry. Set `completeness` to 0 settled of the number of questions.
2. **File digests**: for the 10 to 40 files that matter most (final report, steering committee decks, baselines and models, trackers, handover, reusable templates), write a digest: what the file is, the facts and figures it holds (exactly as written), which version it is, and what part is reusable. Up to about 15,000 characters each. Skip drafts superseded by a later version unless the difference matters, and say so in the later file's digest.
   Each digest is also the guide for opening the original from Brian Ask, so add a short map of the file: for a deck, which slides cover what ("12 IT levers; 13 Facility management levers"); for a workbook, its worksheets in order ("1 Summary, 2 By site, ..."); for a long document, its sections with page numbers. Say what detail is only in the original.
3. **SharePoint location**: find the case folder in SharePoint with the Microsoft 365 connector: `sharepoint_folder_search` with the case folder's name, then `read_resource` on the result to confirm the listing matches the local folder. Record the drive id and the folder's path relative to the drive root (without the document-library segment such as "Shared Documents"). Brian Ask opens originals at `file:///<driveId>/<folderPath>/<path in digest>`, with the asking person's own SharePoint permissions. If the connector isn't available, leave the location out; Brian Ask then answers from contexts and digests only.

## 7. Load everything into the library

1. Write JSON files in your scratchpad for the documents below, so long text doesn't need to be typed inline. On Windows, pass full paths (`C:\Users\<user name>\...`), not the shortened `~1` form.
2. New case: `ArtifactData` `set` on collection `cases`, `doc_id` `<CODE>`, with `caseCode`, `caseName`, `questions` (the full text of `Brian/open_questions.txt`), `questionsUpdatedAt` (now, epoch ms), `card`, `context` (`""`), `mergedChats` (`[]`), `sharepointFolder` (the case folder's name only, never a local path), and `sharepoint` (`{driveId, folderPath, name}` from step 6.3, if found).
3. Existing case: `get` the document first, then `update` only `questions`, `questionsUpdatedAt`, `caseName` and `sharepoint` (and `card` only if it has no interviews merged yet), with `if_version`. Never overwrite `context` or `mergedChats` here.
4. File digests: one document per file in collection `cases/<CODE>/docs`, with `doc_id` made from the path (letters, digits, `-` and `_` only, at most 200 characters) and fields `path` (relative to the case folder), `title`, `type`, `summary` (one or two sentences), `text` (the digest), `modifiedAt`. Use `batch` (up to 50 writes each). On a re-review, update digests of changed files and add new ones.
5. Read the case document back once and check that `questions` and `card` arrived.

**Creating the library (only if the team has none):** copy everything in `template/` to a new scratchpad folder and publish the copied `brian.html` with the `Artifact` tool: `files` maps each of `interview_prompt.txt`, `context_prompt.txt`, `card_prompt.txt` and `ask_prompt.txt` to its copy; `capabilities` `{"sample": {"images": true}, "db": {}, "user": {}, "downloads": true, "assets": {"upload": "interact"}, "mcp": {"servers": [{"server": "Microsoft 365", "tools": ["read_resource"]}]}}`; `icon` `"chat"`; `description` "Brian: ask past cases, or get asked about yours." Tell the user to share it with the case teams that should use it, at Contributor level.

**Updating the library page:** if the template changed, read the library with the `Artifact` tool, then republish the copied files to its `url`.

## 8. Record and report

1. Write `Brian/brian.json` (format in [formats.md](formats.md)), keeping `createdAt` on a re-review and setting `lastReview` to now.
2. Tell the user:
   - the library link, the number of questions (new ones, on a re-review) and the number of file digests;
   - that team members open the library, switch to "Get asked", enter the case code and click "Start a new interview";
   - that the case now appears in Brian Ask, and its card fills in as debriefs are merged;
   - to run `/brian sync <CODE>` after debriefs.
