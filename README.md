# JobApply

Local tracker for job applications: **job link**, **status**, **match notes**, and **grounded tailored resumes** (Markdown) using your **master resume** as the only source of facts.

## Setup

1. **Python 3.10+** recommended.

2. Create a virtual environment and install dependencies:

```powershell
cd "c:\Users\poojithaa\Documents\My files\JobApply"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (required for match + tailor). Optionally set `OPENAI_MODEL`.

4. Copy `profiles/master_resume.example.md` to `profiles/master_resume.md` and replace the placeholder with your real resume (Markdown).

5. Run the app:

```powershell
streamlit run app.py
```

## Git

This folder is its **own** repository (not your Windows user home directory).

**Create a new empty repo** on GitHub (or GitLab, etc.), then:

```powershell
cd "c:\Users\poojithaa\Documents\My files\JobApply"
git init
git add .
git commit -m "Initial JobApply tracker and LLM tailoring"
git branch -M main
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```

Replace `YOUR_USER/YOUR_REPO` with your repository URL. `master_resume.md`, `.env`, and the SQLite DB are ignored by default so they are not pushed; use a **private** repo if you choose to track your resume.

## Optional: Google Custom Search

For the **Discovery** tab, create a [Programmable Search Engine](https://programmablesearchengine.google.com/) and enable the **Custom Search JSON API** in Google Cloud. Put `GOOGLE_API_KEY` and `GOOGLE_CX` in `.env`.

## Indeed

There is no simple public Indeed search API for personal scripts; use Google queries like `site:indeed.com` or paste jobs manually.



