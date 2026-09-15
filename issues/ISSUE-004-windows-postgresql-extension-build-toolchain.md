# ISSUE-004 — Windows PostgreSQL Extension Build Toolchain

## Metadata

- Status: Resolved
- Severity: Medium
- Category: Database
- Related Day: Day 6
- Date: 2026-09-15

## Problem

Building pgvector for the local Windows PostgreSQL installation required a suitable native C/C++ build environment.

## Context

The Urban Aanchol project needed pgvector for persistent vector retrieval.

A compatible prebuilt package was not identified through the existing PostgreSQL installation tools, so pgvector was built from source.

## Symptoms

The project could not proceed with the intended PostgreSQL vector schema until pgvector was compiled and installed for the correct PostgreSQL 18 environment.

## Investigation

The PostgreSQL installation and `pg_config` paths were first identified.

The required build environment was then prepared using Visual Studio Community 2026.

The selected workload was:

```text
Desktop development with C++
```

Optional components were minimized to keep the installation focused on the required build capability.

The x64 Native Tools Command Prompt for Visual Studio was then opened.

The compiler and build utility were verified:

```powershell
cl
nmake
```

The environment reported working x64 Microsoft C/C++ compiler and `nmake` versions.

## Root Cause

The local environment did not already contain the native build toolchain required to compile the pgvector source for PostgreSQL 18.

## Solution

Visual Studio Community 2026 was installed with the C++ desktop development workload.

The x64 Native Tools Command Prompt was used to build pgvector.

The pgvector source release `v0.8.6` was cloned to:

```text
C:\pgvector
```

The build was performed with:

```powershell
nmake /F Makefile.win
```

and installed with:

```powershell
nmake /F Makefile.win install
```

## Verification

The build completed successfully.

The installation placed the pgvector extension files into the PostgreSQL 18 installation.

The Urban Aanchol database then successfully executed:

```sql
CREATE EXTENSION vector;
```

and reported:

```text
vector | 0.8.6
```

Afterward, Day 6 successfully created vector columns, stored 384-dimensional embeddings, and executed pgvector similarity searches.

## Lessons Learned

For native PostgreSQL extensions on Windows:

- Use the correct PostgreSQL installation.
- Use a compatible native build environment.
- Verify `cl` and `nmake` before attempting the build.
- Use the x64 build environment for the x64 PostgreSQL installation.
- Verify the extension from inside the target database after installation.

## Follow-up / Technical Debt

The production environment will be selected later.

The project should prefer deployment environments that support PostgreSQL + pgvector without requiring this local Windows build process in production.

The application should remain portable by keeping vector access behind repository/search interfaces.

## Related Files

```text
database/schema/015_create_embedding_tables.sql
backend/app/database/vector_search.py
backend/app/database/knowledge_vector_search.py
```

## Related Commits

Not recorded as a dedicated issue commit.

## Related Issues

- ISSUE-002 — pgvector unavailable in local PostgreSQL installation
- ISSUE-003 — Multiple PostgreSQL `pg_config` installations
