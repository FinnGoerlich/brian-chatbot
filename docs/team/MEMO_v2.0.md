# Procurement knowledge capture
## A time-first interview that produces a reusable handover

**To:** Hackathon and implementation team  
**Date:** 29 October 2026  
**Version:** 2.0

**Recommendation:** Use the accompanying skill to turn a short project debrief into a structured knowledge record, a selective document request and explicit follow-up gaps. Test the experience in the intended chatbot before deciding on rollout.

### 1. Product promise and output

"Talk through your project once. Leave with a structured handover, the lessons worth reusing and a clear list of supporting files."

- **Knowledge record:** Link project context, personal contribution, reported outcomes, practical lessons and supporting assets. Preserve the interviewee's knowledge boundary.
- **Document request:** Identify the exact slide, tab, model, report or guide worth providing, why it matters, and where to find it or whom to ask.
- **Visible gaps:** Record unknowns, evidence limitations, unresolved questions and agreed actions. Do not manufacture completeness.

Keep the product curated rather than exhaustive, consistent with the original brief. [1]

### 2. Interview design

- **Ask about time first.** "How many minutes do you have? I'll help you quickly log your project contribution and identify the files worth handing over." Wait for the answer before asking about the project.
- **Set a short agenda.** Cover the person's contribution, key outcome, reusable lesson and useful files. Proposed formats to test: 2-3 minutes for quick capture or 5-7 minutes for a focused debrief; these are not established benchmarks.
- **Follow the useful contribution.** Ask one focused question at a time. Extract information across all blocks from each answer. Do not restart generic context questions after the person has offered a valuable lesson.
- **Condense, clarify and connect.** Organize unstructured answers without strengthening claims. Clarify material ambiguities and separate reported outcomes from supporting evidence.
- **Identify documents early, then close.** Ask which file would substantiate or transfer the contribution. When time is short, reduce coverage, recap what is known and ask what should be corrected.

### 3. Four linked content blocks

| Block | Capture | Potential document, only if useful |
|---|---|---|
| Project context | Mandate, relevant scope, personal role and knowledge boundary. | Project charter or scope summary. |
| Outcomes | What changed, what remains open, result definition and evidence. Keep savings stages and working capital effects separate. | Savings report, tool export or value-capture plan. |
| Procurement know-how | What to repeat or avoid, why it worked, prerequisites and limits. | Governance pack, worked example or tool guide. |
| Selected assets | Reuse purpose, specific component, location, owner and required adaptations. | The relevant slide, tab, model, tracker, prompt or dataset. |

The blocks are a coverage map, not four mandatory questionnaires. No asset quota, field weighting or mandatory-field list has been agreed. [1]

<!-- PAGE BREAK -->

### 4. Changes prompted by the test interview

- **Time control:** Establish the budget at the start. A late time warning must change the next question, not merely trigger a promise to speed up.
- **Value capture:** Explore how the PMO kept initiatives moving during reporting-line uncertainty before returning to broad project questions. Using a client tool does not imply that the tool was created by the consultant or is reusable.
- **Precision:** Ask what "27" means before recording a year or amount. Distinguish achieving a result from identifying enough pipeline to cover a target. Do not silently convert a reported contribution into a proven causal effect.
- **Document focus:** Consider the relevant savings report, governance pack, tool guide or value-capture plan. Request only the material with a clear evidence or reuse purpose. [2]

### 5. Demo scope and expansion potential

| Status | What to show or build |
|---|---|
| Delivered in the files | Interview instructions, adaptive follow-up rules, capture template, document-request logic and manual acceptance scenarios. Runtime behavior still requires testing in the chosen chatbot. |
| Prototype candidates | A live view of the record being populated and an interface to collect document links or uploads. These interfaces are not provided by the skill. |
| Future roadmap | Document-grounded extraction, authorized SharePoint retrieval and storage, cross-project search, reusable starter packs and scheduled follow-ups. Each requires implementation and appropriate access. |

Label a demonstration as working, simulated or planned. Keep permission checks in the background of the conversation, but do not bypass them. A supplied link is not proof that a file has been read, approved for reuse or stored.

### 6. Pilot and rollout decisions

- **Confirm the remaining design choices:** Mandatory versus optional fields, block priorities, target duration, follow-up depth and default project versus workstream coverage. Keep current navigation defaults provisional.
- **Set up the deployment:** Select the chatbot environment and loading method; identify the skill owner, approved SharePoint library, access policy, retention rules and final record format.
- **Test the actual behavior:** Run the packaged acceptance scenarios, including an ambiguous metric, a late time warning, a restricted asset and an unavailable integration. Record pass, fail or not tested.
- **Measure usefulness before scaling:** Track duration where reliable timestamps exist, corrections required, repeated questions, ambiguities caught, useful assets located and reviewer-rated handover usefulness. Agree success thresholds and compare with the current handover process before claiming savings or return on investment.

### 7. SharePoint handoff

- **Publish for the team:** Store `SKILL.md` and this memo in the selected library. `MEMO.md` is the editable text counterpart; `skill.zip` contains the skill, optional interface metadata and manual acceptance scenarios.
- **Activate separately:** The implementation team must load or adapt the instructions in its target AI solution. Saving these files in SharePoint does not activate a chatbot or establish a working SharePoint integration.

**References**  
[1] Procurement hackathon brief supplied by the user, sections 1-5: objective, four linked blocks, adaptive behavior, open prioritization decisions and information quality.  
[2] Project wrap-up test interview and subsequent design feedback in this conversation.
