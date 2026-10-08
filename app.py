from __future__ import annotations

import html
import time

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

st.set_page_config(
    page_title="Codeforces Practice Lab",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE = {
    "ink": "#172033",
    "muted": "#62708A",
    "blue": "#2457D6",
    "red": "#E0444E",
    "paper": "#F4F7FC",
    "line": "#DCE3EE",
}

st.markdown(
    """
    <style>
    :root {
        --ink: #172033;
        --muted: #62708A;
        --blue: #2457D6;
        --red: #E0444E;
        --paper: #F4F7FC;
        --line: #DCE3EE;
        --white: #FFFFFF;
    }

    .stApp {
        background-color: var(--paper);
        background-image:
            linear-gradient(rgba(36, 87, 214, 0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(36, 87, 214, 0.035) 1px, transparent 1px);
        background-size: 28px 28px;
        color: var(--ink);
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { right: 1rem; }
    [data-testid="stMainBlockContainer"] {
        max-width: 1180px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--muted);
    }

    h1, h2, h3, p, label, div { font-family: "Avenir Next", "Segoe UI", sans-serif; }
    h2 { color: var(--ink); letter-spacing: -0.025em; }
    h3 { color: var(--ink); }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin: 0.25rem 0 1.6rem;
        color: var(--ink);
        font-weight: 750;
        letter-spacing: -0.03em;
        font-size: 1.1rem;
    }

    .brand-mark {
        display: grid;
        place-items: center;
        width: 2rem;
        height: 2rem;
        border-radius: 0.45rem;
        background: var(--blue);
        color: white;
        box-shadow: 4px 4px 0 var(--red);
    }

    .contest-hero {
        position: relative;
        overflow: hidden;
        margin-bottom: 2rem;
        padding: 2.15rem 2.35rem 2.25rem;
        border: 1px solid #1D2B47;
        border-radius: 1rem;
        background: #172033;
        color: white;
        box-shadow: 0 18px 45px rgba(23, 32, 51, 0.12);
    }

    .contest-hero::after {
        content: "";
        position: absolute;
        width: 15rem;
        height: 15rem;
        right: -4rem;
        top: -6rem;
        border: 2.8rem solid rgba(36, 87, 214, 0.75);
        border-radius: 50%;
    }

    .hero-status {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 1.25rem;
        color: #B9C5DC;
        font-size: 0.8rem;
        font-weight: 650;
    }

    .status-dot {
        width: 0.55rem;
        height: 0.55rem;
        border-radius: 50%;
        background: #59D499;
        box-shadow: 0 0 0 0.25rem rgba(89, 212, 153, 0.14);
    }

    .contest-hero h1 {
        position: relative;
        z-index: 1;
        max-width: 720px;
        margin: 0;
        color: white;
        font-size: clamp(2.35rem, 5vw, 4.1rem);
        line-height: 0.98;
        letter-spacing: -0.055em;
    }

    .contest-hero p {
        position: relative;
        z-index: 1;
        max-width: 630px;
        margin: 1.2rem 0 0;
        color: #C8D2E4;
        font-size: 1rem;
        line-height: 1.6;
    }

    [data-testid="stMetric"] {
        min-height: 8rem;
        padding: 1.15rem 1.2rem;
        border: 1px solid var(--line);
        border-top: 3px solid var(--blue);
        border-radius: 0.7rem;
        background: white;
        box-shadow: 0 7px 20px rgba(23, 32, 51, 0.045);
    }

    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-family: "SFMono-Regular", Consolas, monospace;
        letter-spacing: -0.04em;
    }

    [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 0.8rem;
        background: white;
    }

    .section-heading {
        margin: 2.1rem 0 0.35rem;
        color: var(--ink);
        font-size: 1.45rem;
        font-weight: 750;
        letter-spacing: -0.035em;
    }

    .section-copy {
        max-width: 720px;
        margin: 0 0 1rem;
        color: var(--muted);
        line-height: 1.55;
    }

    .topic-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0.7rem 0 1.4rem;
    }

    .topic-chip {
        padding: 0.32rem 0.66rem;
        border: 1px solid #F2BBC0;
        border-radius: 999px;
        background: #FFF5F5;
        color: #A72F38;
        font-size: 0.78rem;
        font-weight: 650;
    }

    .empty-state {
        padding: 2rem;
        border: 1px dashed #AEBBD0;
        border-radius: 0.8rem;
        background: rgba(255, 255, 255, 0.72);
        color: var(--muted);
        text-align: center;
    }

    .timer-face {
        margin: 1.2rem 0;
        padding: 2.2rem 1rem;
        border: 1px solid #1D2B47;
        border-radius: 0.9rem;
        background: #172033;
        color: white;
        font-family: "SFMono-Regular", Consolas, monospace;
        font-size: clamp(3rem, 9vw, 6.2rem);
        font-variant-numeric: tabular-nums;
        font-weight: 700;
        letter-spacing: -0.07em;
        line-height: 1;
        text-align: center;
    }

    .stButton > button {
        min-height: 2.7rem;
        border: 1px solid #BFCBE0;
        border-radius: 0.55rem;
        font-weight: 700;
    }

    .stButton > button[kind="primary"] {
        border-color: var(--blue);
        background: var(--blue);
        color: white;
    }

    .stButton > button[kind="primary"] p { color: white; }

    .stTextInput input, .stNumberInput input {
        border-color: #C9D3E3;
        border-radius: 0.5rem;
        background: #FAFCFF;
    }

    a { color: var(--blue); }
    *:focus-visible { outline: 3px solid rgba(36, 87, 214, 0.35) !important; }

    @media (max-width: 720px) {
        [data-testid="stMainBlockContainer"] { padding-top: 1.25rem; }
        .contest-hero { padding: 1.6rem 1.35rem; }
        .contest-hero::after { opacity: 0.35; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=300, show_spinner=False)
def load_user_data(handle: str):
    api = CodeforcesAPI()
    return api.user(handle), api.submissions(handle)


@st.cache_data(ttl=3600, show_spinner=False)
def load_problemset():
    return CodeforcesAPI().problemset()


def section_intro(title: str, copy: str) -> None:
    st.markdown(
        f'<h2 class="section-heading">{title}</h2><p class="section-copy">{copy}</p>',
        unsafe_allow_html=True,
    )


def format_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def style_figure(figure) -> None:
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font={"family": "Avenir Next, Segoe UI, sans-serif", "color": PALETTE["ink"]},
        margin={"l": 12, "r": 12, "t": 24, "b": 12},
        coloraxis_colorbar={"outlinewidth": 0},
    )


def render_overview(user: dict, submissions: list[dict]) -> None:
    records = build_solve_records(submissions)
    stats = tag_performance(submissions)
    solved = solved_problem_ids(submissions)

    section_intro(
        "Your scoreboard",
        "A compact read on rating, output, and how quickly accepted solutions arrive.",
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current rating", user.get("rating", "Unrated"))
    col2.metric("Peak rating", user.get("maxRating", "Unrated"))
    col3.metric("Problems solved", len(solved))
    median_minutes = pd.Series([r.solve_seconds / 60 for r in records]).median()
    col4.metric("Median solve time", f"{median_minutes:.0f} min" if records else "—")

    section_intro(
        "Difficulty × solve time",
        "Find the rating bands where speed drops. Darker cells contain more accepted problems.",
    )
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
            labels={"x": "Problem rating", "y": "Estimated solve time", "color": "Solved"},
            text_auto=True,
            color_continuous_scale=[
                [0, "#F1F5FD"],
                [0.45, "#91AFE9"],
                [1, PALETTE["blue"]],
            ],
            aspect="auto",
        )
        style_figure(figure)
        st.plotly_chart(figure, use_container_width=True)
        st.caption(
            "Estimate: elapsed time from the first submission to the first accepted submission."
        )

    section_intro(
        "Topic pressure points",
        "Lower success rates reveal the tags most likely to benefit from deliberate practice.",
    )
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
            color="success_percent",
            color_continuous_scale=[
                [0, PALETTE["red"]],
                [0.55, "#F2B763"],
                [1, PALETTE["blue"]],
            ],
            labels={"success_percent": "Success rate (%)", "tag": "Topic"},
        )
        figure.update_layout(coloraxis_showscale=False)
        style_figure(figure)
        st.plotly_chart(figure, use_container_width=True)


def render_recommendations(user: dict, submissions: list[dict]) -> None:
    section_intro(
        "Build the next practice set",
        "Target the topics costing you the most attempts without jumping outside your rating band.",
    )
    current_rating = int(user.get("rating", 1200))
    stats = tag_performance(submissions)
    detected = weak_tags(stats)

    if detected:
        chips = "".join(f'<span class="topic-chip">{html.escape(tag)}</span>' for tag in detected)
        focus_markup = (
            '<p class="section-copy">Detected focus areas</p>'
            f'<div class="topic-strip">{chips}</div>'
        )
        st.markdown(
            focus_markup,
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns([1, 2])
    target = col1.number_input(
        "Target rating", min_value=800, max_value=3500, value=current_rating, step=100
    )
    all_tags = sorted(stats["tag"].tolist()) if not stats.empty else []
    selected_tags = col2.multiselect("Focus topics", all_tags, default=detected[:3])
    amount = st.slider("Set size", 3, 20, 10)

    st.caption(f"Searching unsolved problems rated {target - 100}–{target + 100}.")
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
                "Open": f"https://codeforces.com/problemset/problem/{contest_id}/{index}",
            }
        )
    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
        column_config={"Open": st.column_config.LinkColumn(display_text="Solve problem")},
    )


def render_timer() -> None:
    section_intro(
        "Mock contest clock",
        "Choose a block, start the clock, and stay inside the problem set until time expires.",
    )
    duration_minutes = st.select_slider(
        "Contest length", options=[30, 45, 60, 90, 120, 150, 180], value=120
    )

    if "timer_end" not in st.session_state:
        st.session_state.timer_end = None
    if "timer_remaining" not in st.session_state:
        st.session_state.timer_remaining = duration_minutes * 60

    start, pause, reset = st.columns(3)
    if start.button("Start / resume", type="primary", use_container_width=True):
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
            f'<div class="timer-face">{format_duration(remaining)}</div>',
            unsafe_allow_html=True,
        )
        if remaining <= 0:
            st.success("Time. Review your submissions and note what slowed you down.")

    clock()


with st.sidebar:
    st.markdown(
        '<div class="brand-lockup"><span class="brand-mark">CF</span> Practice Lab</div>',
        unsafe_allow_html=True,
    )
    st.markdown("**Competitor profile**")
    handle = st.text_input(
        "Codeforces handle", placeholder="Enter a handle", label_visibility="collapsed"
    ).strip()
    st.button("Analyze handle", type="primary", use_container_width=True)
    page = st.radio(
        "Workspace",
        ["Analytics", "Recommendations", "Timer"],
        captions=["Read your history", "Build a problem set", "Run a mock contest"],
    )
    st.divider()
    st.caption("Uses public Codeforces data. No login or API key required.")

page_copy = {
    "Analytics": (
        "Turn submission history into a clear picture of speed, difficulty, and weak topics."
    ),
    "Recommendations": "Build a focused set of unsolved problems around the skills that need work.",
    "Timer": "Create a quiet practice block and train under contest pressure.",
}
st.markdown(
    f"""
    <section class="contest-hero">
        <div class="hero-status"><span class="status-dot"></span> Codeforces API ready</div>
        <h1>Practice with intent.</h1>
        <p>{page_copy[page]}</p>
    </section>
    """,
    unsafe_allow_html=True,
)

if page == "Timer":
    render_timer()
elif not handle:
    st.markdown(
        """
        <div class="empty-state">
            Enter a Codeforces handle in the sidebar to load a performance report.
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    try:
        with st.spinner("Loading submission history…"):
            profile, history = load_user_data(handle)
    except CodeforcesAPIError as exc:
        st.error(f"Could not load that profile. {exc}")
    else:
        resolved_handle = profile.get("handle", handle)
        st.caption(f"Latest {len(history):,} submissions for **{resolved_handle}**")
        if page == "Analytics":
            render_overview(profile, history)
        else:
            render_recommendations(profile, history)
