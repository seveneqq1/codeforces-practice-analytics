import pandas as pd

from codeforces_dashboard.recommendations import recommend_problems, weak_tags


def test_weak_tags_prioritize_low_success_rate():
    stats = pd.DataFrame(
        [
            {
                "tag": "dp",
                "attempted": 5,
                "solved": 1,
                "success_rate": 0.2,
                "attempts_per_solve": 8,
            },
            {
                "tag": "math",
                "attempted": 8,
                "solved": 7,
                "success_rate": 0.875,
                "attempts_per_solve": 1.2,
            },
        ]
    )
    assert weak_tags(stats, 1) == ["dp"]


def test_recommendations_filter_solved_rating_and_tags():
    problems = [
        {"contestId": 1, "index": "A", "name": "Solved", "rating": 1200, "tags": ["dp"]},
        {"contestId": 1, "index": "B", "name": "Target", "rating": 1250, "tags": ["dp", "graphs"]},
        {"contestId": 1, "index": "C", "name": "Too hard", "rating": 1500, "tags": ["dp"]},
        {"contestId": 1, "index": "D", "name": "Wrong tag", "rating": 1200, "tags": ["math"]},
    ]
    picks = recommend_problems(problems, {"1A"}, 1200, ["dp"], 10)
    assert [problem["name"] for problem in picks] == ["Target"]
