# Day 1 — Foundation & Architecture: Step-by-Step Guide

This document records the complete steps followed during **Day 1** of the Urban Aanchol website and RAG chatbot project.

The goal is that another developer can reproduce the Day 1 setup by following this document from start to finish.

---

## Day 1 Objective

Establish the initial development foundation for the Urban Aanchol project:

- Create the GitHub repository
- Verify the development tools
- Install and select Python 3.11
- Create the Python virtual environment
- Configure VS Code
- Create the initial project structure
- Create architecture and MVP documentation
- Create the development journey documentation
- Create a common issue-resolution structure
- Configure Git to ignore the virtual environment
- Create and push the first project commit

---

# Step 1 — Create the GitHub Repository

Create a new repository on GitHub.

### Repository Name

```text
urban-aanchol-rag
```

### Repository Description

```text
AI-powered saree boutique website with a RAG-based recommendation chatbot for Urban Aanchol.
```

### Repository Settings

Use:

- Visibility: Public
- Initialize with README: Yes
- `.gitignore`: Python
- License: None initially

The repository can later be transferred to an Urban Aanchol GitHub Organization if the business grows.

---

# Step 2 — Verify the Development Environment

The project is being developed on Windows using VS Code.

Verify Git:

```powershell
git --version
```

Verify the default Python:

```powershell
python --version
```

Also verify that Python 3.11 is installed:

```powershell
py -3.11 --version
```

Expected result:

```text
Python 3.11.9
```

### Important

Python 3.13 may also remain installed on the computer.

That is not a problem.

For this project, Python 3.11 is the selected runtime because it provides broad compatibility with the AI/ML ecosystem.

---

# Step 3 — Clone the Repository Locally

Open a terminal and navigate to the folder where the project should be stored.

Clone the GitHub repository:

```powershell
git clone https://github.com/atanuduttagupta/urban-aanchol-rag.git
```

Enter the repository:

```powershell
cd urban-aanchol-rag
```

Verify the repository:

```powershell
git status
```

Expected:

```text
On branch main
Your branch is up to date with 'origin/main'.
```

---

# Step 4 — Create the Python Virtual Environment

From the project root:

```powershell
py -3.11 -m venv .venv
```

This creates:

```text
.venv/
```

The virtual environment is local to the project and must not be committed to Git.

---

# Step 5 — Activate the Virtual Environment

In Command Prompt:

```cmd
.venv\Scripts\activate
```

After activation, the terminal should show something similar to:

```text
(.venv)
```

Verify the Python version:

```powershell
python --version
```

Expected:

```text
Python 3.11.9
```

---

# Step 6 — Configure Python in VS Code

Open the project folder in VS Code.

Use:

```text
Ctrl + Shift + P
```

Search for:

```text
Python: Select Interpreter
```

Select the project's Python 3.11 interpreter / `.venv` environment.

Then open:

```text
Terminal → New Terminal
```

Verify:

```powershell
python --version
```

Expected:

```text
Python 3.11.9
```

### Why this step matters

The Python interpreter used by the operating system and the interpreter selected by VS Code can be different.

VS Code must use the project's Python 3.11 environment.

See:

`../../issues/python/vscode-python-interpreter.md`

for the issue encountered during Day 1.

---

# Step 7 — Create the Initial Application Folders

From the project root:

```powershell
mkdir backend
```

```powershell
mkdir frontend
```

```powershell
mkdir docs
```

```powershell
mkdir data
```

These folders provide the initial separation between:

- Backend application
- Frontend website
- Permanent project documentation
- Catalogue/data files

---

# Step 8 — Create the Documentation Structure

Create the development journey folder:

```powershell
mkdir journey
```

Create the Day 1 folder:

```powershell
mkdir journey\day-01-foundation
```

Create the common issue folder:

```powershell
mkdir issues
```

The project structure now begins to look like:

```text
urban-aanchol-rag/
│
├── backend/
├── frontend/
├── data/
├── docs/
├── journey/
│   └── day-01-foundation/
│
├── issues/
│
├── .gitignore
└── README.md
```

---

# Step 9 — Create the Permanent Architecture Documents

Create:

```powershell
New-Item docs\architecture.md
```

```powershell
New-Item docs\mvp.md
```

```powershell
New-Item docs\technology-principles.md
```

These documents describe:

### `architecture.md`

The planned system architecture, business workflow and retrieval evolution.

### `mvp.md`

The scope of the first useful website + RAG chatbot.

### `technology-principles.md`

The project's core principles:

- Zero-cost first
- No vendor lock-in
- Open-source first
- Replaceable components
- Grounded RAG
- Product availability awareness
- Security and privacy
- Production-quality presentation

---

# Step 10 — Create the Development Journey Documents

Create the main journey README:

```powershell
New-Item journey\README.md
```

Create the Day 1 documentation:

```powershell
New-Item journey\day-01-foundation\README.md
```

```powershell
New-Item journey\day-01-foundation\steps.md
```

```powershell
New-Item journey\day-01-foundation\decisions.md
```

The purpose of these files is:

| File | Purpose |
|---|---|
| `journey/README.md` | Overall project development journey |
| `day-01-foundation/README.md` | Day 1 summary and outcome |
| `day-01-foundation/steps.md` | Reproducible Day 1 instructions |
| `day-01-foundation/decisions.md` | Important technical decisions |

---

# Step 11 — Create the Common Issue Structure

Issues are intentionally stored **outside individual Day folders**.

This allows an issue to be referenced from multiple days if necessary.

Create the issue categories:

```powershell
mkdir issues\python
```

```powershell
mkdir issues\vscode
```

```powershell
mkdir issues\git-github
```

```powershell
mkdir issues\frontend
```

```powershell
mkdir issues\backend
```

```powershell
mkdir issues\database
```

```powershell
mkdir issues\rag
```

```powershell
mkdir issues\deployment
```

Create the issue index:

```powershell
New-Item issues\README.md
```

The structure becomes:

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

---

# Step 12 — Configure `.gitignore`

Open:

```text
.gitignore
```

Make sure it contains:

```text
.venv/
```

The Python virtual environment should never be uploaded to GitHub.

Other secrets and local environment files should also be excluded as the project evolves.

---

# Step 13 — Document the Python / VS Code Issue

During Day 1, Python 3.11.9 was installed, but VS Code initially used Python 3.13.9.

Document the issue in:

```text
issues/python/vscode-python-interpreter.md
```

The issue documentation should explain:

```text
Problem
↓
Expected version
↓
Actual version
↓
Cause
↓
Resolution
↓
Verification
↓
Lesson learned
```

This turns an individual troubleshooting experience into reusable project documentation.

---

# Step 14 — Review the Project Structure

Before committing, verify the structure.

Expected:

```text
urban-aanchol-rag/
│
├── backend/
├── frontend/
├── data/
│
├── docs/
│   ├── architecture.md
│   ├── mvp.md
│   └── technology-principles.md
│
├── journey/
│   ├── README.md
│   └── day-01-foundation/
│       ├── README.md
│       ├── steps.md
│       └── decisions.md
│
├── issues/
│   ├── README.md
│   ├── python/
│   ├── vscode/
│   ├── git-github/
│   ├── frontend/
│   ├── backend/
│   ├── database/
│   ├── rag/
│   └── deployment/
│
├── .gitignore
└── README.md
```

---

# Step 15 — Review Git Status

From the project root:

```powershell
git status
```

Review the list carefully.

Make sure:

- `.venv/` is not listed
- Expected documentation files are present
- Expected folders are present
- No secrets are present

---

# Step 16 — Stage the Changes

Run:

```powershell
git add .
```

Then review:

```powershell
git status
```

All intended changes should appear under:

```text
Changes to be committed
```

---

# Step 17 — Create the First Project Commit

Create the initial foundation commit:

```powershell
git commit -m "docs: establish project architecture and Day 1 foundation"
```

The commit records the initial project foundation.

---

# Step 18 — Push to GitHub

Push the commit:

```powershell
git push origin main
```

This backs up the project foundation on GitHub.

---

# Step 19 — Verify the Repository

Run:

```powershell
git status
```

Expected result:

```text
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

This confirms that the local project and GitHub repository are synchronized.

---

# Day 1 Completion Checklist

- [x] GitHub repository created
- [x] Git verified
- [x] Python 3.11.9 installed
- [x] Python 3.11 project environment created
- [x] Virtual environment activated
- [x] VS Code configured to use Python 3.11
- [x] Backend folder created
- [x] Frontend folder created
- [x] Data folder created
- [x] Documentation folder created
- [x] Development journey folder created
- [x] Day 1 folder created
- [x] Common issue folder created
- [x] Architecture documentation created
- [x] MVP documentation created
- [x] Technology principles documented
- [x] Git configured to ignore `.venv`
- [x] Python / VS Code issue documented
- [x] Initial commit created
- [x] Changes pushed to GitHub
- [x] Working tree verified clean

---

# Day 1 Result

The Urban Aanchol project now has a clean, documented and version-controlled foundation.

The repository is ready for Day 2 development.

**Next:** Day 2 — Project Setup
