# ISSUE-002 — pgvector Unavailable in Local PostgreSQL Installation

## Metadata

- Status: Resolved
- Severity: High
- Category: Database
- Related Day: Day 6
- Date: 2026-09-15

## Problem

The local PostgreSQL installation did not initially have the `vector` extension available.

## Context

Day 6 required persistent semantic retrieval using PostgreSQL + pgvector.

The first check showed that the PostgreSQL installation did not report `vector` as an available extension.

## Symptoms

The `vector` extension was not available in the PostgreSQL extension list.

This meant the planned schema using:

```sql
VECTOR(384)
```

could not yet be used.

## Investigation

The environment was inspected to determine which PostgreSQL installation was being used.

Two `pg_config.exe` executables were found:

```text
C:\ProgramData\anaconda3\Library\bin\pg_config.exe
C:\Program Files\PostgreSQL\18\bin\pg_config.exe
```

The normal PATH resolved the Anaconda executable, while the actual application database was PostgreSQL 18.

The correct PostgreSQL installation was verified with:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\pg_config.exe" --version
```

which reported PostgreSQL 18.6.

StackBuilder was checked, but a standard pgvector package was not identified.

The Anaconda environment was also checked and did not provide a suitable pgvector installation for the existing PostgreSQL 18 database.

## Root Cause

The existing PostgreSQL 18 installation did not have pgvector installed, and the machine also contained unrelated PostgreSQL tooling from Anaconda.

## Solution

Visual Studio Community 2026 was installed with the required:

```text
Desktop development with C++
```

workload.

The x64 Native Tools Command Prompt for Visual Studio was used.

The pgvector `v0.8.6` source was cloned and built:

```powershell
git clone --branch v0.8.6 https://github.com/pgvector/pgvector.git
cd C:\pgvector
nmake /F Makefile.win
nmake /F Makefile.win install
```

The extension was then enabled in the Urban Aanchol database:

```sql
CREATE EXTENSION vector;
```

## Verification

The installed extension was verified with PostgreSQL and returned:

```text
vector | 0.8.6
```

The local database stack was therefore confirmed as:

```text
PostgreSQL 18.6
+
pgvector 0.8.6
```

Subsequent Day 6 vector tables, embedding persistence, and similarity searches all worked successfully.

## Lessons Learned

When building PostgreSQL extensions on Windows:

1. Identify the PostgreSQL installation actually used by the database.
2. Do not assume the first `pg_config` found on PATH belongs to that database.
3. Keep unrelated Conda PostgreSQL environments separate from an installer-based PostgreSQL installation.
4. A C++ build toolchain may be required when a compatible prebuilt extension package is unavailable.

## Follow-up / Technical Debt

The production deployment platform and its pgvector support will be evaluated later. The project should retain standard PostgreSQL/pgvector interfaces to avoid unnecessary vendor lock-in.

## Related Files

```text
database/schema/015_create_embedding_tables.sql
backend/app/database/connection.py
backend/app/database/embedding_generator.py
```

## Related Commits

Not recorded as a dedicated issue commit.

## Related Issues

- ISSUE-003 — Multiple PostgreSQL `pg_config` installations
- ISSUE-004 — Windows PostgreSQL extension build toolchain
