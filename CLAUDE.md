# CLAUDE.md — Developer A

## Project
MJC AI Campus Agent

You are working as Developer A.

## Before Coding
Read these files first:
- `TECH_STACK.md`
- `PROJECT_REQUIREMENTS.md`
- `API_CONTRACT.md`
- `DEVELOPER_A_BACKEND_TASKS.md`
- `BACKEND_IMPLEMENTATION_PLAN.md`
- `AI_AGENT_RULES.md`

Inspect the existing repository before creating, deleting, moving, or rewriting files.

## Ownership
You own:
- `backend/`
- `ai/`
- `data/`

Shared with Developer B:
- `shared/`
- `docs/`

Do not modify `frontend/` unless explicitly requested.

## Current Priority
Build a working vertical slice before advanced infrastructure.

Order:
1. FastAPI skeleton
2. Mock data
3. Course API
4. Student/Schedule API
5. Enrollment validation
6. Chat API
7. OpenAI-compatible AI client
8. Integration test
9. PostgreSQL
10. Crawler/RAG

Do not begin with PostgreSQL or RAG unless the earlier phases are working.

## API Contract
`API_CONTRACT.md` is the interface contract with Developer B.

Do not rename endpoints, fields, enums, request bodies, or response structures without explicit approval.

If implementation requires a contract change:
1. Explain why.
2. Update the contract first after approval.
3. Then update code.

## Architecture Rules
- FastAPI
- Pydantic
- SQLAlchemy when database phase begins
- REST API
- Keep business rules outside route handlers.
- Keep AI provider access behind a dedicated client/service.
- Prefer simple code over premature abstraction.
- Mock data must be replaceable with database repositories later.

## AI Safety / Correctness
Never let the LLM invent authoritative school facts.

Course availability, cancellation, enrollment capacity, schedules, classrooms, class modality, and eligibility must come from code/API/database results.

The LLM handles intent, tool selection, summarization, and natural-language presentation.

## Secrets
Never hardcode secrets.
Use environment variables.
Never commit `.env`.
Never expose AI API keys to frontend code.
Do not print secrets in logs.

## Quality
After each meaningful implementation:
- run relevant tests
- verify FastAPI starts
- verify endpoint response matches `API_CONTRACT.md`
- check imports
- check errors
- summarize changed files

Do not silently ignore failing tests.

## Collaboration
Developer B is implementing Frontend simultaneously.
Avoid unnecessary shared-file edits.
Make backend behavior predictable so B can develop against Mock responses.

## First Task
If the backend has not been initialized:
1. Analyze repository.
2. Present a short implementation plan.
3. Create the FastAPI skeleton.
4. Add CORS for local Next.js development.
5. Add `/health`.
6. Create Mock course data.
7. Implement `GET /api/courses`.
8. Implement `GET /api/courses/{courseId}`.
9. Test both endpoints.
10. Report what was created and the next recommended task.
