# ISSUE-005 — Windows Application Control Blocked scikit-learn Native Extension

- **ID:** ISSUE-005
- **Category:** Python / Environment
- **Severity:** Medium
- **Status:** Resolved
- **Date:** 2026-09-19

## Problem

The Urban Aanchol RAG project could not import part of scikit-learn
required by sentence-transformers.

The following error occurred:

```text
ImportError: DLL load failed while importing _radius_neighbors:
An Application Control policy has blocked this file.

The blocked native extension was:

_radius_neighbors.cp311-win_amd64.pyd

The issue occurred with:

Python: 3.11
scikit-learn: 1.9.1
sentence-transformers: 5.7.0
numpy: 2.4.6
scipy: 1.17.1

Investigation
1. Reinstalled the same scikit-learn version

scikit-learn 1.9.1 was uninstalled and reinstalled without using
the pip cache.

The problem remained.

2. Tested individual native extensions

Most scikit-learn native extensions loaded successfully, but:

_radius_neighbors.cp311-win_amd64.pyd

remained blocked by the Windows Application Control policy.

Resolution

Downgraded scikit-learn from:

1.9.1

to:

1.7.2

Verification:

scikit-learn: 1.7.2
sklearn.metrics import OK
sentence-transformers import OK

The semantic vector search was then successfully executed against
PostgreSQL + pgvector.

Validation

The following semantic search completed successfully:

Query:
Something elegant for a family function

Three vector-search results were returned.

This confirmed that:

scikit-learn imports correctly
sentence-transformers imports correctly
the embedding model loads correctly
embeddings can be generated
PostgreSQL + pgvector vector search works
Impact

The project environment now uses:

scikit-learn==1.7.2

This version should remain pinned unless a future dependency upgrade
is deliberately tested.

Lessons Learned

1. A package installation can succeed while a native extension is
still blocked by Windows security policy.

2. Reinstalling the same package version did not resolve the issue.

3. A tested compatible package version can be a practical resolution
when the failure is isolated to a native extension.

4. Dependency versions should be recorded in the project requirements
and lock file after resolving an environment issue.

Follow-up
Keep scikit-learn pinned to 1.7.2.
Re-test the environment when major ML dependency upgrades are introduced.
Avoid unnecessary dependency upgrades during the MVP phase.