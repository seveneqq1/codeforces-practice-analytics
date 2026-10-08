"""Personalized practice-set generation."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from .analytics import problem_id


def weak_tags(tag_stats: pd.DataFrame, limit: int = 5) -> list[str]:
    if tag_stats.empty:
        return []
    eligible = tag_stats[tag_stats["attempted"] >= 2]
    if eligible.empty:
        eligible = tag_stats
    return (
        eligible.sort_values(
            ["success_rate", "attempts_per_solve", "attempted"],
            ascending=[True, False, False],
        )["tag"]
        .head(limit)
        .tolist()
    )


def recommend_problems(
    problems: Iterable[dict[str, Any]],
    solved_ids: set[str],
    target_rating: int,
    target_tags: list[str],
    limit: int = 10,
    rating_window: int = 100,
) -> list[dict[str, Any]]:
    """Rank unsolved problems by weak-tag overlap and rating proximity."""

    ranked: list[tuple[tuple[int, int, int], dict[str, Any]]] = []
    wanted = set(target_tags)
    for problem in problems:
        pid = problem_id(problem)
        rating = problem.get("rating")
        if not pid or pid in solved_ids or rating is None:
            continue
        if abs(rating - target_rating) > rating_window:
            continue
        overlap = wanted.intersection(problem.get("tags", []))
        if wanted and not overlap:
            continue
        score = (-len(overlap), abs(rating - target_rating), -rating)
        ranked.append((score, problem))

    ranked.sort(key=lambda item: item[0])
    return [problem for _, problem in ranked[:limit]]
