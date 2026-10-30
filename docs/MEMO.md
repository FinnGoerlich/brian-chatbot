# Procurement knowledge capture
## A time-first interview that produces a reusable handover, and a way to reuse it

**To:** Hackathon and implementation team  
**Date:** 29 October 2026  
**Version:** 2.1 (version 2.0 by the knowledge-capture team, in `docs/team/MEMO_v2.0.md`; this version adds how it is implemented in Brian)

**Recommendation:** Use the debrief skill, now built into Brian's "Get asked" mode, to turn a short project debrief into a structured knowledge record, a selective document request and explicit follow-up gaps. Use Brian's "Ask" mode to put those records to work for the next case team. Test both in the Brian demo before deciding on rollout.

### 1. Product promise and output

"Talk through your project once. Leave with a structured handover, the lessons worth reusing and a clear list of supporting files." And for the next team: "Ask what past cases learned before you start yours."

- **Knowledge record:** Link project context, personal contribution, reported outcomes, practical lessons and supporting assets. Preserve the interviewee's knowledge boundary.
- **Document request:** Identify the exact slide, tab, model, report or guide worth providing, why it matters, and where to find it or whom to ask.
- **Visible gaps:** Record unknowns, evidence limitations, unresolved questions and agreed actions. Do not manufacture completeness.
- **Living case context:** Every finished debrief is merged into one context file per case, with a case card that Brian Ask uses for overviews and matching.

Keep the product curated rather than exhaustive, consistent with the original brief. [1]

### 2. Interview design

- **Ask about time first.** "How many minutes do you have? I'll help you quickly log your project contribution and identify the files worth handing over." Wait for the answer before asking about the project. Brian passes the real elapsed time (from message timestamps) to the interviewer, so it can keep to the budget.
- **Set a short agenda.** Cover the person's contribution, key outcome, reusable lesson and useful files. Proposed formats to test: 2-3 minutes for quick capture or 5-7 minutes for a focused debrief; these are not established benchmarks.
- **Follow the useful contribution.** Ask one focused question at a time. Extract information across all blocks from each answer. Do not restart generic context questions after the person has offered a valuable lesson.
- **Offer a faster format.** At the start, the person can choose "all questions at once" instead of step by step: Brian sends the whole numbered list, the person answers in one go (dictating works well), and follow-ups come back as one list, usually for one or two rounds, before the usual recap and record. The time question is skipped in this format; the list is the agenda.
- **Use what is already known.** The case is known from its case code, so Brian doesn't ask which project it is. The open questions from the SharePoint review and earlier debriefs of the same case act as a map of material gaps, not a questionnaire.
- **Condense, clarify and connect.** Organize unstructured answers without strengthening claims. Clarify material ambiguities and separate reported outcomes from supporting evidence.
- **Identify documents early, then close.** Ask which file would substantiate or transfer the contribution; the person can attach it in the chat. When time is short, reduce coverage, recap what is known and ask what should be corrected.

### 3. Four linked content blocks

| Block | Capture | Potential document, only if useful |
|---|---|---|
| Project context | Mandate, relevant scope, personal role and knowledge boundary. | Project charter or scope summary. |
| Outcomes | What changed, what remains open, result definition and evidence. Keep savings stages and working capital effects separate. | Savings report, tool export or value-capture plan. |
| Procurement know-how | What to repeat or avoid, why it worked, prerequisites and limits. | Governance pack, worked example or tool guide. |
| Selected assets | Reuse purpose, specific component, location, owner and required adaptations. | The relevant slide, tab, model, tracker, prompt or dataset. |

The blocks are a coverage map, not four mandatory questionnaires. No asset quota, field weighting or mandatory-field list has been agreed. [1] The case context file uses the same four blocks, so a record and the context it feeds line up.

### 4. Changes prompted by the test interview

- **Time control:** Establish the budget at the start. A late time warning must change the next question, not merely trigger a promise to speed up.
- **Value capture:** Explore how the PMO kept initiatives moving during reporting-line uncertainty before returning to broad project questions. Using a client tool does not imply that the tool was created by the consultant or is reusable.
- **Precision:** Ask what "27" means before recording a year or amount. Distinguish achieving a result from identifying enough pipeline to cover a target. Do not silently convert a reported contribution into a proven causal effect.
- **Document focus:** Consider the relevant savings report, governance pack, tool guide or value-capture plan. Request only the material with a clear evidence or reuse purpose. [2]

### 5. How it is implemented in Brian

| Part | Where | What it does |
|---|---|---|
| Debrief ("Get asked") | Brian library artifact, `interview_prompt.txt` | The skill's interview, adapted: case code instead of "which project", open questions and earlier debriefs as the gap map, real elapsed time, file attachments, a "# Project knowledge record" at the close |
| Living case context | `context_prompt.txt`, `card_prompt.txt` | "Finish & update case context" merges the record into the case's context.md (four blocks, open questions, gaps, change log) and refreshes its case card |
| Brian Ask | Same artifact, `ask_prompt.txt` | A large question field above the case cards, which filter by functional area and practice area (industry); overview of all cases, matching a new case to past ones (functional area first), one case in depth, lessons across cases; reads case contexts and file digests on demand, and opens original SharePoint files (specific slides, sheets or pages, guided by the context) through the asker's Microsoft 365 connector |
| SharePoint review and sync | Claude Code `brian` skill | Reads the case SharePoint into open questions, a first case card and file digests; copies transcripts, attached files and context.md back into the case's `Brian/` folder |

### 6. Demo scope and expansion potential

| Status | What to show or build |
|---|---|
| Working in the demo | Time-first debrief with adaptive follow-ups and the capture template; file attachments in the chat (text and images read, PDFs stored); merging into the living case context and card; Brian Ask with case cards, overview, matching, file digests and live reads of original SharePoint files with the asker's own permissions; SharePoint review and sync through Claude Code. Behavior still needs testing with real users and real cases. |
| Prototype candidates | A live view of the record being populated during the interview; reading Word, Excel and PowerPoint files inside the chat; per-case access control in Brian Ask. |
| Future roadmap | Storing straight into SharePoint without a sync step, scheduled follow-ups, reusable starter packs, search across hundreds of cases. Each requires implementation and appropriate access. |

Label a demonstration as working, simulated or planned. The demo cases in the library are fictional (marked MOCK). Keep permission checks in the background of the conversation, but do not bypass them. A supplied link is not proof that a file has been read, approved for reuse or stored.

### 7. Pilot and rollout decisions

- **Decided for the demo:** Brian Ask is open to every case team that might want context; client names may show; matching starts with functional area (Procurement, Pricing, ...); case cards can be filtered by functional area and by practice area (the client's industry); Brian Ask may open case file digests when a context isn't enough; any case team member can run a debrief and the record needs no approval before it reaches Brian Ask.
- **Still to confirm:** mandatory versus optional fields, block priorities, target duration, follow-up depth and default project versus workstream coverage. Keep current navigation defaults provisional.
- **Set up the deployment:** confirm with project leadership that AI tool use is approved per client; identify the skill owner, the case teams the library is shared with, retention rules and the final record format.
- **Test the actual behavior:** run acceptance scenarios, including an ambiguous metric, a late time warning, a restricted asset and an unavailable integration. Record pass, fail or not tested.
- **Measure usefulness before scaling:** track duration, corrections required, repeated questions, ambiguities caught, useful assets located, reviewer-rated handover usefulness, and for Brian Ask whether teams found a relevant case. Agree success thresholds and compare with the current handover process before claiming savings or return on investment.

### 8. SharePoint handoff

- **Per case:** Claude Code's `/brian review <case code>` creates the case's `Brian/` folder; `/brian sync <case code>` fills `Brian/raw_transcripts/`, `Brian/files/` and `Brian/context.md`.
- **For the team:** the skill and this memo live in the Brian repository. Saving them in SharePoint does not activate a chatbot; the Brian library artifact is the running version.

**References**  
[1] Procurement hackathon brief supplied by the user, sections 1-5: objective, four linked blocks, adaptive behavior, open prioritization decisions and information quality.  
[2] Project wrap-up test interview and subsequent design feedback in the knowledge-capture team's conversation.
