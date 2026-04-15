from __future__ import annotations

from jobapply.llm import chat_json


SYSTEM = """You are an expert technical recruiter assistant.
You compare a candidate's resume (facts only) to a job description.
You must output valid JSON only, with keys:
- "category": one of "Strong match" | "Good match" | "Stretch" | "Poor match"
- "score": integer 0-100 (overall fit)
- "reasons": array of 3-6 short strings explaining the decision
- "missing_must_haves": array of strings: important JD requirements not clearly supported by the resume (empty if none)
- "seniority_note": one short string about whether experience level seems aligned (e.g. "~3 years vs JD")

Rules:
- Base everything ONLY on the resume text. Do not invent candidate skills.
- If the JD is vague, say so in reasons and be conservative.
"""


def score_match(*, master_resume: str, job_description: str) -> dict:
    user = f"""MASTER RESUME (source of truth for candidate facts):
---
{master_resume}
---

JOB DESCRIPTION:
---
{job_description}
---
"""
    return chat_json(SYSTEM, user, temperature=0.2)
