# Hackathon Report and Presentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce and publish a submission-ready PDF report, three-slide PPTX and PDF deck, and a 4-minute-30-second Korean demo script for MJC AI Campus Agent.

**Architecture:** Repository documents, source code, data files, and test structure are the evidence layer. A deterministic document builder and an Artifact Tool presentation builder generate editable sources; PDF renderers produce submission copies. Every final page and slide is rendered to images for visual inspection before committing and pushing only the new deliverables.

**Tech Stack:** Python, python-docx, reportlab/LibreOffice/Poppler, JavaScript ES modules, @oai/artifact-tool, PowerPoint, Markdown, Git.

## Global Constraints

- The total presentation and demonstration must fit within five minutes; target duration is 4 minutes 30 seconds.
- The report must be a PDF and include the public GitHub URL and both members' departments and names on the cover.
- Describe the data as 246 unique sections and 516 preserved class sessions, not as indiscriminate duplicate deletion.
- Separate real course data, demo-only student state, and swappable JSON/PostgreSQL storage explicitly.
- Do not claim real enrollment execution, school authentication, or completed pgvector RAG.
- Use navy and blue consistently across the report and deck.
- Inspect every final PDF page and every final slide for clipping, overlap, wrapping, and Korean glyph errors.

---

### Task 1: Evidence Ledger and Final Copy

**Files:**
- Create: `docs/hackathon/evidence-ledger.txt`
- Create: `docs/hackathon/report-content.txt`

**Interfaces:**
- Consumes: `README.md`, `API_CONTRACT.md`, `AI_AGENT_RULES.md`, `DEMO_SETUP.md`, `data/raw/README.md`, application source and tests.
- Produces: verified facts and final Korean prose used by both builders.

- [ ] Extract team, repository, feature, data, architecture, safety, testing, limitation, and roadmap facts with source paths.
- [ ] Verify counts for courses, sessions, APIs, screens, and tests with read-only scripts.
- [ ] Write the complete Korean report copy with no placeholders or unsupported claims.
- [ ] Scan for the terms `더미`, `중복 제거`, `실제 수강신청 완료`, and `RAG 구현 완료`; replace misleading uses with the approved precise wording.

### Task 2: PDF Report

**Files:**
- Create: `docs/hackathon/build_report.py`
- Create: `docs/hackathon/MJC_AI_Campus_Agent_해커톤_보고서.docx`
- Create: `docs/hackathon/MJC_AI_Campus_Agent_해커톤_보고서.pdf`
- Create during QA: `docs/hackathon/.build/report-render/`

**Interfaces:**
- Consumes: `docs/hackathon/report-content.txt` and verified repository facts.
- Produces: editable DOCX source and submission-ready PDF.

- [ ] Apply one resolved document design preset with exact A4 margins, fonts, spacing, heading hierarchy, table styles, and footer/page-number rules.
- [ ] Build the 10–12 page report with cover, executive summary, problem, service, functions, data, architecture, AI safety, implementation evidence, benefits, limitations, roadmap, and conclusion.
- [ ] Convert the DOCX to PDF using the bundled document renderer.
- [ ] Render every PDF page to PNG and inspect each image at full size.
- [ ] Correct all clipping, overlap, widows/orphans, broken tables, and Korean glyph issues, then re-render until clean.

### Task 3: Three-Slide Presentation

**Files:**
- Create: `docs/hackathon/.build/deck/build_deck.mjs`
- Create: `docs/hackathon/MJC_AI_Campus_Agent_5분_발표자료.pptx`
- Create: `docs/hackathon/MJC_AI_Campus_Agent_5분_발표자료.pdf`
- Create during QA: `docs/hackathon/.build/deck-render/`

**Interfaces:**
- Consumes: report copy, verified metrics, navy/blue visual tokens.
- Produces: editable PPTX and PDF presentation copies.

- [ ] Read the presentation style guide and Artifact Tool API documentation.
- [ ] Build slide 1 as a minimal title and one-sentence value proposition.
- [ ] Build slide 2 around the demonstration journey and student value with concise labels.
- [ ] Build slide 3 around `246 sections`, `516 sessions`, `14 service endpoints`, swappable storage, and AI non-hallucination safeguards.
- [ ] Add source-note blocks for repository-derived claims.
- [ ] Render every slide, run overflow tests, inspect each slide at full size, and correct unintended overlap or wrapping.
- [ ] Export and visually inspect the presentation PDF.

### Task 4: 4-Minute-30-Second Demonstration Script

**Files:**
- Create: `docs/hackathon/MJC_AI_Campus_Agent_5분_발표대본.md`

**Interfaces:**
- Consumes: the three-slide sequence and implemented application routes.
- Produces: timestamped Korean narration, click actions, fallback lines, and closing statement.

- [ ] Write a timestamped script for 0:00–4:30 covering introduction, dashboard, course search, AI chat, schedule preview, classroom/counseling, technical trust, and closing.
- [ ] Mark presenter actions separately from spoken lines.
- [ ] Include a short contingency route when the AI provider or network is unavailable.
- [ ] Read the script aloud approximately and shorten sentences that jeopardize the 4:30 target.

### Task 5: Cross-Artifact Verification

**Files:**
- Modify if needed: all Task 2–4 final artifacts.

**Interfaces:**
- Consumes: final report, deck, and script.
- Produces: consistent submission set.

- [ ] Verify identical team names, repository URL, course/session/API counts, feature status, and limitations across all artifacts.
- [ ] Confirm the report cover meets the photographed submission notice.
- [ ] Confirm no artifact calls real course data “dummy data.”
- [ ] Confirm all final files open and are non-empty.

### Task 6: Commit and Push

**Files:**
- Add only: `docs/hackathon/` final sources and deliverables plus this plan.

**Interfaces:**
- Consumes: verified final artifacts.
- Produces: a Git commit pushed to the configured GitHub remote.

- [ ] Review `git status --short` and exclude unrelated pre-existing changes.
- [ ] Stage only the plan and `docs/hackathon/` deliverables, excluding `.build/` QA intermediates.
- [ ] Commit with message `docs: add hackathon report and presentation materials`.
- [ ] Push the current branch to `origin` and verify the remote branch update succeeds.
