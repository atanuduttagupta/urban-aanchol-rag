# Day 2 — Steps

## 1. Backend setup

Created the backend folder structure:

```text
backend/
├── requirements.txt
└── app/
    ├── __init__.py
    └── main.py
```

### Commands used

From the project root:

```powershell
mkdir backend
mkdir backend\app
New-Item backend\requirements.txt -ItemType File
New-Item backend\app\__init__.py -ItemType File
New-Item backend\app\main.py -ItemType File
```

> If the folders/files already exist, these commands do not need to be repeated.

---

## 2. Python environment

The project uses Python 3.11.9.

### Verify Python version

```powershell
py -3.11 --version
```

Expected result:

```text
Python 3.11.9
```

### Activate the project virtual environment

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Verify the active Python version

```powershell
python --version
```

Expected result:

```text
Python 3.11.9
```

---

## 3. Install FastAPI and Uvicorn

Installed the initial backend dependencies:

- fastapi==0.141.1
- uvicorn==0.52.4

### Commands used

```powershell
python -m pip install fastapi==0.141.1 uvicorn==0.52.4
```

### Verify installed packages

```powershell
python -m pip show fastapi
python -m pip show uvicorn
```

---

## 4. Create requirements.txt

The direct project dependencies were recorded in:

```text
backend/requirements.txt
```

Content:

```text
fastapi==0.141.1
uvicorn==0.52.4
```

### Command used to view the file

```powershell
Get-Content backend\requirements.txt
```

---

## 5. Create dependency lock file

A complete list of packages installed in the current virtual environment was saved to:

```text
backend/requirements-lock.txt
```

### Full command used

```powershell
python -m pip freeze > backend\requirements-lock.txt
```

### Verify the lock file

```powershell
Get-Content backend\requirements-lock.txt
```

This lock file records the exact installed package versions for reproducibility.

---

## 6. Create the FastAPI application

Created:

```text
backend/app/main.py
```

The application contains:

- FastAPI application object
- Root endpoint: `/`
- Health endpoint: `/health`

Current application:

```python
from fastapi import FastAPI

app = FastAPI(title="Urban Aanchol API")


@app.get("/")
def root():
    return {"message": "Urban Aanchol API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
```

---

## 7. Start the FastAPI development server

### Command used

From the project root:

```powershell
uvicorn backend.app.main:app --reload
```

Expected result includes:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Keep this terminal running while testing the API.

---

## 8. Test the API

### Test the root endpoint

Open in a browser:

```text
http://127.0.0.1:8000/
```

Expected response:

```json
{
  "message": "Urban Aanchol API is running"
}
```

### Test the health endpoint

Open:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

---

## 9. Test FastAPI Swagger UI

Open:

```text
http://127.0.0.1:8000/docs
```

Verified that the Swagger UI displays:

- `GET /`
- `GET /health`

Both endpoints were available for testing.

---

## 10. Frontend setup

Created the frontend structure:

```text
frontend/
├── index.html
├── style.css
├── script.js
└── assets/
```

### Commands used

From the project root:

```powershell
mkdir frontend
mkdir frontend\assets
New-Item frontend\index.html -ItemType File
New-Item frontend\style.css -ItemType File
New-Item frontend\script.js -ItemType File
```

> If the folders/files already exist, these commands do not need to be repeated.

---

## 11. Create the initial website

Added the initial Urban Aanchol website to:

```text
frontend/index.html
```

The page includes:

- Header
- Urban Aanchol branding
- Home navigation
- Collection navigation
- Saree Guide navigation
- About navigation
- Contact navigation
- Hero section
- Collection section
- Saree Guide section
- About section
- Contact section
- Footer

---

## 12. Add website styling

Added the initial styling to:

```text
frontend/style.css
```

The design uses the initial Urban Aanchol visual direction:

- Cream background
- Maroon primary colour
- Gold accent
- Serif typography
- Responsive navigation
- Responsive layout

---

## 13. Add Saree Guide

Added a flexible navigation section for future helpful saree-related content.

Navigation link:

```html
<a href="#guide">Saree Guide</a>
```

Section:

```html
<section id="guide" class="section">
    <h2>Saree Guide</h2>
    <p>
        Helpful guides about saree fabrics, care, styling,
        making, storage and more.
    </p>
</section>
```

The section is intentionally simple at this stage.

Future topics may include:

- How sarees are made
- Saree fabric guides
- Saree washing and care
- Saree storage
- Draping tips
- Occasion/style guides
- Other useful saree-related educational content

These articles can later become part of the RAG knowledge base.

---

## 14. Test the frontend

Opened:

```text
frontend/index.html
```

directly in the browser.

### Browser testing

The following were verified:

- Page loads correctly
- CSS is applied
- Urban Aanchol branding is visible
- Maroon header is displayed
- Cream background is displayed
- Hero section is displayed
- Explore Collection button is displayed
- Navigation is displayed
- Saree Guide is displayed
- Collection section is reachable
- Saree Guide section is reachable
- About section is reachable
- Contact section is reachable

---

## 15. Test navigation

Clicked each navigation item:

```text
Home
Collection
Saree Guide
About
Contact
```

Verified that the links scroll to their corresponding sections.

---

## 16. Final Day 2 verification

Before committing the work, check Git status from the project root:

```powershell
git status
```

Review the changed and untracked files.

The expected Day 2 changes include:

```text
backend/
frontend/
```

and the Day 2 journey documentation:

```text
journey/day-02-project-setup/
```

---

## Result

Day 2 completed successfully.

The project now has:

- Python 3.11 project foundation
- FastAPI backend
- Uvicorn development server
- API root endpoint
- API health endpoint
- Swagger API documentation
- Dependency requirements file
- Dependency lock file
- Initial responsive website
- Urban Aanchol visual foundation
- Collection section
- Saree Guide section
- About section
- Contact section
- Working website navigation

Next step:

Document the Day 2 technical decisions and commit the completed Day 2 work to Git.

# Step 17 — Stage the Changes

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

# Step 18 — Create the Project Commit

Create the initial foundation commit:

```powershell
git commit -m "feat: complete Day 2 project setup"
```

The commit records the initial project foundation.

---

# Step 19 — Push to GitHub

Push the commit:

```powershell
git push origin main
```

This backs up the project foundation on GitHub.

---

# Step 20 — Verify the Repository

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