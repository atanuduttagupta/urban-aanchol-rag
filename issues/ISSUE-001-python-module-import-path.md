# ISSUE-001 — Python Module Import Path

## Metadata

- Status: Resolved
- Severity: Low
- Category: Python
- Related Day: Day 4
- Date: 2026-09-15

## Problem

A test script could not import the project's `backend` package when executed directly from the project root.

## Context

The catalogue validation work included executable test scripts under:

```text
backend/tests/
```

The test needed to import project modules such as:

```python
from backend.app.catalogue.pipeline import load_default_catalogue
```

## Symptoms

Running:

```powershell
python backend/tests/test_embedding_text.py
```

produced:

```text
ModuleNotFoundError: No module named 'backend'
```

## Investigation

The command executed the file directly.

The project root package was therefore not being resolved as expected for the import:

```python
from backend.app...
```

The same project code had already been designed to use the `backend` package structure.

## Root Cause

The test was being executed as a standalone script rather than as a Python module from the project root.

## Solution

Execute the test using Python's module form:

```powershell
python -m backend.tests.test_embedding_text
```

This correctly resolves `backend` from the project root package context.

## Verification

The module command was executed successfully and produced the expected embedding-text output for `UA-0001`.

The same module execution approach was subsequently used for other project test scripts.

## Lessons Learned

For this repository's package structure, executable tests under `backend/tests/` should be run from the project root using:

```powershell
python -m backend.tests.<test_module>
```

rather than directly executing the `.py` file.

## Follow-up / Technical Debt

As the project matures, these verification scripts should gradually become proper pytest tests.

## Related Files

```text
backend/tests/test_embedding_text.py
backend/app/catalogue/pipeline.py
```

## Related Commits

Not recorded as a dedicated issue commit.

## Related Issues

None.
