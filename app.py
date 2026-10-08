from __future__ import annotations

import time
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st

from codeforces_dashboard.analytics import (
    build_solve_records,
    heatmap_frame,
    solved_problem_ids,
    tag_performance,
)
from codeforces_dashboard.api import CodeforcesAPI, CodeforcesAPIError
from codeforces_dashboard.recommendations import recommend_problems, weak_tags

st.set_page_config(page_title="CF Practice Lab", page_icon="⚡", layout="wide")


@st.cache_data(ttl=300, show_spinner=False)
def load_user_data(handle: str):
    api = CodeforcesAPI()
    return api.user(handle), api.submissions(handle)


@st.cache_data(ttl=3600, show_spinner=False)
def load_problemset():
    return CodeforcesAPI().problemset()


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def render_overview(user: dict, submissions: list[dict]) -> None:
    records = build_solve_records(submissions)
    stats = tag_performance(submissions)
    solved = solved_problem_ids(submissions)

    st.subheader("Performance snapshot")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current rating", user.get("rating", "Unrated"))
    col2.metric("Max rating", user.get("maxRating", "Unrated"))
    col3.metric("Problems solved", len(solved))
    median_minutes = pd.Series([r.solve_seconds / 60 for r in records]).median()
    col4.metric("Median solve time", f"{median_minutes:.0f} min" if records else "—")

    frame = heatmap_frame(records)
    if frame.empty:
        st.info("No rated accepted problems were found in the loaded history.")
    else:
        rating_order = sorted(
            frame["rating_band"].unique(), key=lambda value: int(value.split("-")[0])
        )
        time_order = ["<15m", "15-30m", "30-60m", "1-2h", "2h+"]
        matrix = (
            frame.groupby(["time_band", "rating_band"], observed=False)
            .size()
            .unstack(fill_value=0)
            .reindex(index=time_order, columns=rating_order, fill_value=0)
        )
        figure = px.imshow(
            matrix,
            labels={"x": "Problem rating", "y": "Estimated time to solve", "color": "Solved"},
            text_auto=True,
            color_continuous_scale="Blues",
            aspect="auto",
        )
        figure.update_layout(margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(figure, use_container_width=True)
        st.caption(
            "Solve time is estimated from the first submission to the first accepted submission."
        )

    st.subheader("Tag strengths and weaknesses")
    if stats.empty:
        st.info("Not enough tagged submissions to calculate topic performance.")
    else:
        chart_data = stats.sort_values("success_rate").head(15).copy()
        chart_data["success_percent"] = chart_data["success_rate"] * 100
        figure = px.bar(
            chart_data,
            x="success_percent",
            y="tag",
            orientation="h",
            color="attempted",
            labels={
                "success_percent": "Success rate (%)",
                "tag": "Topic",
                "attempted": "Attempted",
            },
        )
        st.plotly_chart(figure, use_container_width=True)


def render_recommendations(user: dict, submissions: list[dict]) -> None:
    st.subheader("Personalized practice set")
    current_rating = int(user.get("rating", 1200))
    stats = tag_performance(submissions)
    detected = weak_tags(stats)

    col1, col2 = st.columns([1, 2])
    target = col1.number_input(
        "Target rating", min_value=800, max_value=3500, value=current_rating, step=100
    )
    all_tags = sorted(stats["tag"].tolist()) if not stats.empty else []
    selected_tags = col2.multiselect("Focus topics", all_tags, default=detected[:3])
    amount = st.slider("Problems", 3, 20, 10)

    st.caption(f"The search uses a rating window of {target - 100}–{target + 100}.")
    if not selected_tags:
        st.info("Choose at least one focus topic to generate a targeted set.")
        return

    try:
        problems = load_problemset()
    except CodeforcesAPIError as exc:
        st.error(str(exc))
        return

    picks = recommend_problems(
        problems,
        solved_problem_ids(submissions),
        int(target),
        selected_tags,
        amount,
    )
    if not picks:
        st.warning(
            "No matching unsolved problems were found. "
            "Try a wider topic selection or another rating."
        )
        return

    rows = []
    for problem in picks:
        contest_id = problem["contestId"]
        index = problem["index"]
        rows.append(
            {
                "Problem": problem["name"],
                "Rating": problem.get("rating"),
                "Matching topics": ", ".join(
                    sorted(set(problem.get("tags", [])) & set(selected_tags))
                ),
                "Link": f"https://codeforces.com/problemset/problem/{contest_id}/{index}",
            }
        )
    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
        column_config={"Link": st.column_config.LinkColumn()},
    )


def render_timer() -> None:
    st.subheader("Mock contest timer")
    st.caption("A distraction-free countdown that stays in your browser session.")
    duration_minutes = st.select_slider(
        "Contest length", options=[30, 45, 60, 90, 120, 150, 180], value=120
    )

    if "timer_end" not in st.session_state:
        st.session_state.timer_end = None
    if "timer_remaining" not in st.session_state:
        st.session_state.timer_remaining = duration_minutes * 60

    start, pause, reset = st.columns(3)
    if start.button("Start / resume", use_container_width=True):
        st.session_state.timer_end = time.time() + st.session_state.timer_remaining
        st.rerun()
    if pause.button("Pause", use_container_width=True):
        if st.session_state.timer_end:
            st.session_state.timer_remaining = max(0, st.session_state.timer_end - time.time())
            st.session_state.timer_end = None
        st.rerun()
    if reset.button("Reset", use_container_width=True):
        st.session_state.timer_end = None
        st.session_state.timer_remaining = duration_minutes * 60
        st.rerun()

    @st.fragment(run_every=1)
    def clock() -> None:
        remaining = st.session_state.timer_remaining
        if st.session_state.timer_end:
            remaining = max(0, st.session_state.timer_end - time.time())
            if remaining <= 0:
                st.session_state.timer_end = None
                st.session_state.timer_remaining = 0
        st.markdown(
            f"<h1 style='text-align:center;font-size:5rem'>{format_duration(remaining)}</h1>",
            unsafe_allow_html=True,
        )
        if remaining <= 0:
            st.success("Time! Review your submissions and note what slowed you down.")

    clock()


st.title("⚡ Codeforces Practice Lab")
st.write("Turn submission history into focused, measurable practice.")

with st.sidebar:
    st.header("Profile")
    handle = st.text_input("Codeforces handle", placeholder="tourist").strip()
    page = st.radio("Mode", ["Analytics", "Recommendations", "Timer"])
    st.divider()
    st.caption(f"Data refreshed {datetime.now(timezone.utc).strftime('%H:%M UTC')}")

if page == "Timer":
    render_timer()
elif not handle:
    st.info("Enter a Codeforces handle in the sidebar to begin.")
else:
    try:
        with st.spinner("Loading Codeforces history…"):
            profile, history = load_user_data(handle)
    except CodeforcesAPIError as exc:
        st.error(str(exc))
    else:
        resolved_handle = profile.get("handle", handle)
        st.caption(
            f"Analyzing the latest {len(history):,} submissions for **{resolved_handle}**"
        )
        if page == "Analytics":
            render_overview(profile, history)
        else:
            render_recommendations(profile, history)
