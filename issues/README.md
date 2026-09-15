# Urban Aanchol — Issues & Solutions Knowledge Base

## Purpose

The `issues/` directory is the project's version-controlled troubleshooting and engineering knowledge base.

It records problems encountered while building Urban Aanchol, how they were investigated, the root cause, the solution, verification, and lessons learned.

The objective is not only to track defects. It is to preserve reusable engineering knowledge so that a problem solved once does not need to be rediscovered later.

---

## Why Markdown Instead of Excel

This project uses Markdown files as the primary detailed issue-and-solution record.

Reasons:

- The project itself is maintained in Git/GitHub.
- Markdown is version-controlled alongside the code it describes.
- Issue records can be reviewed in GitHub without another application.
- Technical commands and code snippets can be stored naturally.
- Changes to issue knowledge have a Git history.
- Individual issue records can be linked from Day documentation, commits, pull requests, and other technical documents.
- Markdown remains portable and vendor-independent.

A spreadsheet may be useful later for a high-level issue dashboard, but it is not the source of truth for detailed troubleshooting knowledge.

---

## Directory Structure

```text
issues/
├── README.md
├── python/
├── vscode/
├── git-github/
├── frontend/
├── backend/
├── database/
├── rag/
└── deployment/
```

The category folders organize issues by the primary technical area involved.

If a problem crosses multiple areas, place it in the category representing its primary root cause or main engineering concern.

---

## Issue ID Convention

Use sequential identifiers:

```text
ISSUE-001
ISSUE-002
ISSUE-003
...
```

The ID is a unique identifier only.

It does **not** imply:

- project phase,
- technical priority,
- chronological importance,
- severity,
- category,
- implementation order.

This follows the project's existing principle that identifiers are identifiers, not classifications.

---

## File Naming Convention

Use:

```text
ISSUE-001-short-descriptive-title.md
```

Examples:

```text
ISSUE-001-python-module-import-path.md
ISSUE-002-pgvector-not-installed.md
ISSUE-003-multiple-pg-config-installations.md
```

Use lowercase words separated by hyphens after the issue ID.

Keep the title concise but descriptive.

---

## Issue Status

Use one of:

| Status | Meaning |
|---|---|
| `Open` | Problem is identified but not resolved. |
| `Investigating` | Root cause is still being investigated. |
| `Blocked` | Progress requires an external dependency or decision. |
| `Resolved` | A solution has been implemented and verified. |
| `Deferred` | Known issue intentionally postponed. |
| `Closed` | No further action is required. |
| `Won't Fix` | Intentionally not going to be addressed. |

For most solved development problems, the normal lifecycle is:

```text
Open
  ↓
Investigating
  ↓
Resolved
  ↓
Closed
```

---

## Severity

Use:

| Severity | Meaning |
|---|---|
| `Critical` | Prevents the application or essential development workflow from functioning. |
| `High` | Major functionality is blocked or seriously incorrect. |
| `Medium` | Important problem, but a practical workaround exists. |
| `Low` | Minor problem, inconvenience, warning, or cleanup item. |
| `Informational` | Useful technical observation or lesson rather than a defect. |

Severity describes impact. It does not describe how difficult the problem was to solve.

---

## Standard Issue Template

Every detailed issue should use the following structure where applicable.

```markdown
# ISSUE-XXX — Short Title

## Metadata

- Status: Open
- Severity: Medium
- Category: Database
- Related Day: Day X
- Date: YYYY-MM-DD

## Problem

Describe what went wrong.

## Context

Explain what the project was trying to accomplish when the problem occurred.

## Symptoms

Record the observable error, unexpected behavior, warning, or failed command.

## Investigation

Record the troubleshooting steps in chronological order.

Include:

- commands executed,
- relevant outputs,
- files inspected,
- hypotheses considered,
- tests performed.

Do not rewrite history after the fact. Preserve useful investigative information.

## Root Cause

State the confirmed cause.

If the cause is not confirmed, explicitly say so.

## Solution

Describe the implemented fix.

Include relevant commands or code snippets when useful.

## Verification

Explain how the fix was tested.

Include the successful command/output or other objective evidence.

## Lessons Learned

Capture reusable technical knowledge.

## Follow-up / Technical Debt

Record improvements that are intentionally deferred.

## Related Files

List important files changed or inspected.

## Related Commits

Record relevant Git commit hashes when available.

## Related Issues

Link or reference related issue IDs when applicable.
```

---

## What Makes a Good Issue Record

A useful issue record should allow another developer to understand:

```text
What happened?
     ↓
Why did it happen?
     ↓
How did we investigate it?
     ↓
What fixed it?
     ↓
How do we know it is fixed?
     ↓
What should we remember next time?
```

The record should be factual and evidence-based.

Avoid writing only:

> "It didn't work, so we changed X."

Instead capture the reasoning and verification that led to the solution.

---

## Record the Actual Error

When an issue produces an error message, preserve the important error text.

Example:

```text
ModuleNotFoundError: No module named 'backend'
```

Then document:

- the command that produced it,
- why it happened,
- the corrected command,
- the verification result.

This creates a reusable troubleshooting reference.

---

## Commands and Code

Commands should be stored in fenced code blocks:

```powershell
python -m backend.tests.test_embedding_text
```

Code should be stored in the appropriate language block:

```python
from backend.app.database.embedding_generator import EmbeddingGenerator
```

Do not store secrets, passwords, API keys, tokens, personal credentials, or other sensitive information in issue files.

---

## Verification Is Mandatory for Resolved Issues

An issue should not normally be marked `Resolved` based only on the implementation of a fix.

There should be objective verification whenever practical.

Examples:

```text
pytest
```

```text
psql ... SELECT ...
```

```text
API endpoint returns HTTP 200
```

```text
Git status is clean
```

Record the relevant result.

---

## Relationship With the Learning Journey

The `journey/` directory explains what was intentionally built during each project day.

The `issues/` directory explains problems encountered while building it.

They serve different purposes.

```text
journey/
    What we planned and built

issues/
    What went wrong and how we solved it
```

A Day document may reference an issue:

```text
Day 6
  ↓
ISSUE-002 — pgvector unavailable
  ↓
Solution
  ↓
Verified PostgreSQL + pgvector
```

An issue should record the related Day when the connection is known.

---

## Relationship With Git

When an issue leads to a code change, record the relevant commit once the change is committed.

Example:

```text
Related Commit:
006fff2 — feat: complete Day 5 database and retrieval foundation
```

Do not invent commit hashes.

If the fix has not yet been committed, leave the commit field empty or state:

```text
Pending commit
```

---

## When to Create a New Issue

Create a new issue when:

- a distinct technical problem occurs,
- a different root cause is involved,
- an existing issue does not adequately describe the problem,
- the solution is likely to be useful as a separate troubleshooting reference.

Examples:

```text
Python import failure
```

and

```text
PostgreSQL extension installation failure
```

should normally be separate issues.

---

## When to Update an Existing Issue

Update an existing issue when:

- additional investigation clarifies the same problem,
- the same root cause produces another symptom,
- verification information is missing,
- the solution needs refinement,
- a related follow-up has been completed.

Avoid creating multiple issue files for the same root cause unless there is a clear reason.

---

## Issue vs Technical Debt

Not every technical observation needs to become a defect.

For example:

```text
Current embedding schema uses VECTOR(384)
and future models may use other dimensions.
```

This may be recorded as technical debt or a design limitation in the relevant Day documentation rather than creating an issue immediately.

Create a separate issue when the deferred item becomes an actionable engineering task.

---

## Issue vs Day Documentation

Use Day documentation for decisions that were intentionally made.

Use an issue record for unexpected problems.

Example:

### Decision

> We chose PostgreSQL + pgvector for persistent vector retrieval.

This belongs in:

```text
journey/day-06-database-design/decisions.md
```

### Problem

> pgvector was not available in the existing PostgreSQL installation and had to be built from source.

This belongs in an issue record.

The same problem may also be briefly referenced from Day 6 documentation.

---

## Issue Categories

### `python/`

Use for:

- Python runtime problems
- virtual environments
- imports
- package installation
- dependency conflicts
- Python execution behavior

### `vscode/`

Use for:

- VS Code configuration
- extensions
- terminal behavior
- editor-specific problems

### `git-github/`

Use for:

- Git
- branches
- commits
- merges
- remotes
- GitHub repository problems

### `frontend/`

Use for:

- HTML
- CSS
- JavaScript
- browser behavior
- responsive UI problems

### `backend/`

Use for:

- FastAPI
- backend application logic
- API behavior
- backend integration problems

### `database/`

Use for:

- PostgreSQL
- pgvector
- SQL
- schema
- indexes
- database connectivity
- migrations

### `rag/`

Use for:

- embeddings
- retrieval
- reranking
- chunking
- RAG pipeline
- prompt/context problems
- semantic search behavior

### `deployment/`

Use for:

- hosting
- deployment
- environment configuration
- production infrastructure
- domain configuration

---

## Current Known Day 6 Examples

The following problems were encountered during the project and are good candidates for detailed issue records:

### Python module execution

Symptom:

```text
ModuleNotFoundError: No module named 'backend'
```

The direct script execution form did not resolve the project package correctly.

The verified solution was:

```powershell
python -m backend.tests.test_embedding_text
```

Category:

```text
python/
```

### pgvector unavailable

The PostgreSQL installation initially did not report the `vector` extension.

Investigation eventually led to building pgvector from source against PostgreSQL 18.

Category:

```text
database/
```

### Multiple pg_config installations

The normal PATH resolved Anaconda's PostgreSQL tooling while the application database was PostgreSQL 18.

The correct executable was:

```text
C:\Program Files\PostgreSQL\18\bin\pg_config.exe
```

Category:

```text
database/
```

These examples should only become individual issue files when we decide to preserve the detailed troubleshooting history for them.

---

## Do Not Store Secrets

Never commit:

- passwords
- database credentials
- API keys
- access tokens
- HF tokens
- private keys
- customer personal information
- payment information

Use environment variables and local configuration files that are excluded by `.gitignore`.

---

## Issue Quality Checklist

Before committing a new issue record, check:

- [ ] Issue ID is unique.
- [ ] Title clearly describes the problem.
- [ ] Status is correct.
- [ ] Severity is appropriate.
- [ ] Related Day is recorded.
- [ ] Problem is clearly described.
- [ ] Important error/output is preserved.
- [ ] Investigation is documented.
- [ ] Root cause is distinguished from hypothesis.
- [ ] Solution is documented.
- [ ] Verification is documented.
- [ ] No secrets or sensitive information are included.
- [ ] Related files are listed.
- [ ] Related commit is added when available.
- [ ] Related issues are referenced when useful.

---

## Recommended Workflow

When a new problem occurs:

```text
Problem occurs
     ↓
Capture error/output
     ↓
Create issue record if distinct/useful
     ↓
Investigate
     ↓
Confirm root cause
     ↓
Implement solution
     ↓
Verify objectively
     ↓
Record lessons learned
     ↓
Commit code + issue documentation
     ↓
Mark Resolved
```

For recurring problems, update the existing issue rather than starting from zero.

---

## Philosophy

The issue knowledge base is part of the Urban Aanchol learning project.

The objective is not to make the repository look like a list of failures.

The objective is to preserve the engineering reasoning behind the project:

```text
Problem
  →
Investigation
  →
Understanding
  →
Solution
  →
Verification
  →
Reusable knowledge
```

This makes the project more maintainable, easier to debug, easier to explain in technical discussions/interviews, and more valuable as a long-term AI/ML learning artifact.
