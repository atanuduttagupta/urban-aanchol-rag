# ISSUE-003 — Multiple PostgreSQL pg_config Installations

## Metadata

- Status: Resolved
- Severity: Medium
- Category: Database
- Related Day: Day 6
- Date: 2026-09-15

## Problem

The Windows environment contained more than one `pg_config.exe`, and the normal PATH resolved an executable associated with Anaconda rather than the PostgreSQL 18 installation used by the Urban Aanchol database.

## Context

While preparing to build pgvector, the PostgreSQL build configuration needed to match the PostgreSQL server actually running the Urban Aanchol database.

## Symptoms

The normal `pg_config` resolution pointed to:

```text
C:\ProgramData\anaconda3\Library\bin\pg_config.exe
```

while the actual PostgreSQL server was PostgreSQL 18.6 installed at:

```text
C:\Program Files\PostgreSQL\18
```

This created a risk of building or installing pgvector against the wrong PostgreSQL environment.

## Investigation

The available PostgreSQL tooling was located and compared.

The correct executable was explicitly tested:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\pg_config.exe" --version
```

Result:

```text
PostgreSQL 18.6
```

Its paths were also checked:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\pg_config.exe" --bindir
& "C:\Program Files\PostgreSQL\18\bin\pg_config.exe" --pkglibdir
```

The database itself was verified separately as PostgreSQL 18.6.

## Root Cause

The machine had multiple PostgreSQL-related installations, and the first executable available through PATH was not the installation used by the application database.

## Solution

The project explicitly used:

```text
C:\Program Files\PostgreSQL\18\bin\pg_config.exe
```

for PostgreSQL 18-specific build configuration.

The pgvector build was performed using the x64 Native Tools environment and the PostgreSQL 18 installation.

## Verification

pgvector was successfully installed into the PostgreSQL 18 installation.

The Urban Aanchol database successfully executed:

```sql
CREATE EXTENSION vector;
```

and reported:

```text
vector | 0.8.6
```

## Lessons Learned

On a development machine with multiple database environments:

- Never assume the first executable on PATH belongs to the active database.
- Verify server version and build-tool version independently.
- Prefer explicit paths when building native database extensions.
- Avoid mixing Conda-managed PostgreSQL tooling with installer-based PostgreSQL unless the environments are intentionally integrated.

## Follow-up / Technical Debt

The system PATH was not treated as the project's source of truth for PostgreSQL extension builds.

Future development documentation should continue to identify the PostgreSQL 18 installation explicitly where native extension compilation is involved.

## Related Files

```text
database/schema/015_create_embedding_tables.sql
```

## Related Commits

Not recorded as a dedicated issue commit.

## Related Issues

- ISSUE-002 — pgvector unavailable in local PostgreSQL installation
- ISSUE-004 — Windows PostgreSQL extension build toolchain
