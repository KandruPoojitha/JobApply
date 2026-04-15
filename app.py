from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from jobapply.config import MASTER_RESUME_PATH, OPENAI_API_KEY, ensure_dirs
from jobapply.db import (
    delete_application,
    insert_application,
    list_applications,
    update_application,
)
from jobapply.discovery import google_custom_search, indeed_search_placeholder
from jobapply.config import GOOGLE_API_KEY, GOOGLE_CX
from jobapply.matcher import score_match
from jobapply.tailor import tailor_resume, write_tailored_file

STATUSES = ["Saved", "Applied", "Interviewing", "Rejected", "Offer", "Withdrawn"]


def load_master_text() -> str:
    ensure_dirs()
    if not MASTER_RESUME_PATH.is_file():
        return ""
    return MASTER_RESUME_PATH.read_text(encoding="utf-8", errors="replace")


def main() -> None:
    st.set_page_config(page_title="JobApply Tracker", layout="wide")
    st.title("JobApply — tracker & resume tailoring")

    ensure_dirs()
    master = load_master_text()

    with st.sidebar:
        st.subheader("Master resume")
        st.caption(f"Expected path: `{MASTER_RESUME_PATH}`")
        if not master.strip():
            st.warning(
                "Copy `profiles/master_resume.example.md` to `profiles/master_resume.md` "
                "and add your real content."
            )
        else:
            st.success(f"Loaded ({len(master)} chars)")
        st.divider()
        st.subheader("OpenAI")
        if OPENAI_API_KEY:
            st.success("API key set")
        else:
            st.error("Set OPENAI_API_KEY in `.env`")
        st.divider()
        st.subheader("Google Custom Search (optional)")
        if GOOGLE_API_KEY and GOOGLE_CX:
            st.success("GOOGLE_API_KEY + GOOGLE_CX set")
        else:
            st.info("Optional: set for web job discovery in the Discovery tab.")

    tab_track, tab_add, tab_disc = st.tabs(
        ["Tracker", "Add / analyze job", "Discovery (Google)"]
    )

    with tab_track:
        apps = list_applications()
        if not apps:
            st.info("No applications yet. Use **Add / analyze job**.")
        else:
            for a in apps:
                with st.expander(f"**{a.title or 'Untitled'}** — {a.company or 'Unknown'}", expanded=False):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        if a.job_url:
                            st.markdown(f"[Open job link]({a.job_url})")
                        if a.match_category:
                            st.write(f"**Match:** {a.match_category}")
                        if a.match_reason:
                            try:
                                data = json.loads(a.match_reason)
                                st.json(data)
                            except json.JSONDecodeError:
                                st.text(a.match_reason)
                        if a.tailored_resume_path:
                            p = Path(a.tailored_resume_path)
                            if p.is_file():
                                st.download_button(
                                    label="Download tailored resume (.md)",
                                    data=p.read_text(encoding="utf-8"),
                                    file_name=p.name,
                                    key=f"dl_{a.id}",
                                )
                    with c2:
                        new_status = st.selectbox(
                            "Status",
                            STATUSES,
                            index=STATUSES.index(a.status)
                            if a.status in STATUSES
                            else 0,
                            key=f"st_{a.id}",
                        )
                        if new_status != a.status:
                            update_application(a.id, {"status": new_status})
                            st.rerun()
                        if st.button("Delete", key=f"del_{a.id}"):
                            delete_application(a.id)
                            st.rerun()

    with tab_add:
        st.markdown("Paste a job posting, score fit, generate a tailored resume, then save to the tracker.")
        company = st.text_input("Company")
        title = st.text_input("Job title")
        job_url = st.text_input("Job URL")
        source = st.text_input("Source (e.g. Indeed, LinkedIn, Company site)", "")
        jd = st.text_area("Job description (paste)", height=220)

        b1, b2, b3 = st.columns(3)
        scored: dict | None = st.session_state.get("last_score")
        tailored: str | None = st.session_state.get("last_tailored")

        with b1:
            if st.button("Score match", type="primary"):
                if not master.strip():
                    st.error("Add master_resume.md first.")
                elif not jd.strip():
                    st.error("Paste a job description.")
                else:
                    with st.spinner("Scoring…"):
                        try:
                            scored = score_match(
                                master_resume=master, job_description=jd
                            )
                            st.session_state["last_score"] = scored
                            st.session_state["last_tailored"] = None
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        with b2:
            if st.button("Generate tailored resume"):
                if not master.strip():
                    st.error("Add master_resume.md first.")
                elif not jd.strip():
                    st.error("Paste a job description.")
                else:
                    with st.spinner("Tailoring…"):
                        try:
                            text = tailor_resume(
                                master_resume=master, job_description=jd
                            )
                            st.session_state["last_tailored"] = text
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))

        with b3:
            if st.button("Save to tracker"):
                if not job_url.strip():
                    st.error("Job URL is required for the tracker.")
                elif not jd.strip():
                    st.error("Job description is required.")
                else:
                    match_reason = None
                    match_cat = None
                    sc = st.session_state.get("last_score")
                    if isinstance(sc, dict):
                        match_cat = sc.get("category")
                        match_reason = json.dumps(sc, ensure_ascii=False)
                    tailored_path = None
                    tail = st.session_state.get("last_tailored")
                    if isinstance(tail, str) and tail.strip():
                        slug = f"{company}_{title}".strip() or "tailored_resume"
                        path = write_tailored_file(slug, tail)
                        tailored_path = str(path)
                    insert_application(
                        company=company,
                        title=title,
                        job_url=job_url.strip(),
                        source=source,
                        status="Saved",
                        jd_text=jd,
                        match_category=match_cat,
                        match_reason=match_reason,
                        tailored_resume_path=tailored_path,
                    )
                    st.session_state["last_score"] = None
                    st.session_state["last_tailored"] = None
                    st.success("Saved.")
                    st.rerun()

        if scored:
            st.subheader("Last match result")
            st.json(scored)
        if tailored:
            st.subheader("Last tailored resume (preview)")
            st.markdown(tailored)

    with tab_disc:
        st.markdown(
            "Search the web for job pages using **Google Programmable Search** (optional). "
            "You still review and add rows manually or paste URLs into **Add / analyze job**."
        )
        st.code(indeed_search_placeholder(), language="json")
        q = st.text_input(
            "Query",
            value='data engineer job (remote OR hybrid) site:indeed.com',
        )
        if st.button("Run Google search"):
            if not (GOOGLE_API_KEY and GOOGLE_CX):
                st.error("Set GOOGLE_API_KEY and GOOGLE_CX in .env")
            else:
                with st.spinner("Searching…"):
                    try:
                        results = google_custom_search(q)
                        for r in results:
                            st.markdown(f"**[{r.get('title')}]({r.get('link')})**")
                            st.caption(r.get("snippet") or "")
                    except Exception as e:
                        st.error(str(e))


if __name__ == "__main__":
    main()
