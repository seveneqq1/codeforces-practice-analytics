"""Submission-history analysis used by the dashboard and tests."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class SolveRecord:
    problem_id: str
    name: str
    rating: int | None
    tags: tuple[str, ...]
    solve_seconds: int
    solved_at: int
    attempts: int


def problem_id(problem: dict[str, Any]) -> str:
    return f"{problem.get('contestId', '')}{problem.get('index', '')}"


def build_solve_records(submissions: Iterable[dict[str, Any]]) -> list[SolveRecord]:
    """Estimate solve time from first attempt to first accepted submission.

    Codeforces does not expose time spent actively working, so this metric is a
    transparent proxy. Attempts made after the first accepted submission are
    ignored.
    """

    history: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for submission in submissions:
        pid = problem_id(submission.get("problem", {}))
        if pid:
            history[pid].append(submission)

    records: list[SolveRecord] = []
    for pid, attempts in history.items():
        ordered = sorted(attempts, key=lambda item: item.get("creationTimeSeconds", 0))
        accepted_index = next(
            (index for index, item in enumerate(ordered) if item.get("verdict") == "OK"),
            None,
        )
        if accepted_index is None:
            continue

        accepted = ordered[accepted_index]
        first = ordered[0]
        problem = accepted.get("problem", {})
        solve_seconds = max(
            0,
            accepted.get("creationTimeSeconds", 0) - first.get("creationTimeSeconds", 0),
        )
        records.append(
            SolveRecord(
                problem_id=pid,
                name=problem.get("name", pid),
                rating=problem.get("rating"),
                tags=tuple(problem.get("tags", [])),
                solve_seconds=solve_seconds,
                solved_at=accepted.get("creationTimeSeconds", 0),
                attempts=accepted_index + 1,
            )
        )
    return sorted(records, key=lambda record: record.solved_at, reverse=True)


def solved_problem_ids(submissions: Iterable[dict[str, Any]]) -> set[str]:
    return {
        problem_id(item.get("problem", {})) for item in submissions if item.get("verdict") == "OK"
    }


def attempted_problem_ids(submissions: Iterable[dict[str, Any]]) -> set[str]:
    return {problem_id(item.get("problem", {})) for item in submissions}


def tag_performance(submissions: Iterable[dict[str, Any]]) -> pd.DataFrame:
    """Return per-tag solved/attempted counts and an efficiency score."""

    by_problem: dict[str, dict[str, Any]] = {}
    for item in submissions:
        problem = item.get("problem", {})
        pid = problem_id(problem)
        row = by_problem.setdefault(
            pid,
            {"tags": set(problem.get("tags", [])), "attempts": 0, "solved": False},
        )
        row["attempts"] += 1
        row["solved"] = row["solved"] or item.get("verdict") == "OK"

    totals: dict[str, dict[str, float]] = defaultdict(
        lambda: {"attempted": 0, "solved": 0, "submissions": 0}
    )
    for row in by_problem.values():
        for tag in row["tags"]:
            totals[tag]["attempted"] += 1
            totals[tag]["solved"] += int(row["solved"])
            totals[tag]["submissions"] += row["attempts"]

    rows = []
    for tag, values in totals.items():
        attempted = int(values["attempted"])
        solved = int(values["solved"])
        rows.append(
            {
                "tag": tag,
                "attempted": attempted,
                "solved": solved,
                "success_rate": solved / attempted if attempted else 0.0,
                "attempts_per_solve": values["submissions"] / max(solved, 1),
            }
        )
    return (
        pd.DataFrame(rows).sort_values(["success_rate", "attempted"], ascending=[True, False])
        if rows
        else pd.DataFrame(
            columns=["tag", "attempted", "solved", "success_rate", "attempts_per_solve"]
        )
    )


def heatmap_frame(records: Iterable[SolveRecord]) -> pd.DataFrame:
    rows = []
    for record in records:
        if record.rating is None:
            continue
        minutes = record.solve_seconds / 60
        rating_floor = (record.rating // 100) * 100
        rows.append(
            {
                "rating": record.rating,
                "rating_band": f"{rating_floor}-{rating_floor + 99}",
                "minutes": minutes,
                "time_band": _time_band(minutes),
                "problem": record.name,
            }
        )
    return pd.DataFrame(rows)


def _time_band(minutes: float) -> str:
    if minutes < 15:
        return "<15m"
    if minutes < 30:
        return "15-30m"
    if minutes < 60:
        return "30-60m"
    if minutes < 120:
        return "1-2h"
    return "2h+"
