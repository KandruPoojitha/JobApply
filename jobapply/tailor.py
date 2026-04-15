from __future__ import annotations

from pathlib import Path

from jobapply.llm import chat_text


SYSTEM = """You tailor a resume for a specific job using ONLY facts present in the master resume.
Output Markdown suitable for a professional resume.

Hard rules:
- Do NOT add employers, dates, degrees, tools, certifications, or achievements that are not in the master resume.
- You MAY reorder sections, rename section titles slightly, merge bullets, and rephrase for clarity.
- You MAY mirror terminology from the job description when it accurately describes work the candidate already did.
- Keep a natural, human tone; avoid hype and empty buzzwords.
- If the JD asks for something not in the resume, do not imply the candidate has it; omit or keep generic.
- Start with the candidate's name and contact line if present in the master resume.
"""


def tailor_resume(*, master_resume: str, job_description: str) -> str:
    user = f"""MASTER RESUME:
---
{master_resume}
---

JOB DESCRIPTION:
---
{job_description}
---

Produce the full tailored resume in Markdown."""
    return chat_text(SYSTEM, user, temperature=0.35)


def write_tailored_file(slug: str, content: str) -> Path:
    from jobapply.config import TAILORED_DIR, ensure_dirs

    ensure_dirs()
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in slug)[:120]
    path = TAILORED_DIR / f"{safe}.md"
    path.write_text(content, encoding="utf-8")
    return path
