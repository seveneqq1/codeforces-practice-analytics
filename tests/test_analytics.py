from codeforces_dashboard.analytics import build_solve_records, heatmap_frame, tag_performance


def submission(timestamp, verdict, contest=100, index="A", rating=1200, tags=None):
    return {
        "creationTimeSeconds": timestamp,
        "verdict": verdict,
        "problem": {
            "contestId": contest,
            "index": index,
            "name": f"Problem {index}",
            "rating": rating,
            "tags": tags or ["dp"],
        },
    }


def test_solve_time_uses_first_attempt_to_first_acceptance():
    records = build_solve_records(
        [submission(160, "OK"), submission(100, "WRONG_ANSWER"), submission(220, "OK")]
    )
    assert len(records) == 1
    assert records[0].solve_seconds == 60
    assert records[0].attempts == 2


def test_tag_performance_counts_unique_problems():
    history = [
        submission(100, "WRONG_ANSWER"),
        submission(120, "OK"),
        submission(150, "WRONG_ANSWER", index="B", tags=["dp", "graphs"]),
    ]
    stats = tag_performance(history).set_index("tag")
    assert stats.loc["dp", "attempted"] == 2
    assert stats.loc["dp", "solved"] == 1
    assert stats.loc["graphs", "success_rate"] == 0


def test_heatmap_bands_rating_and_time():
    records = build_solve_records([submission(100, "WRONG_ANSWER"), submission(1899, "OK")])
    frame = heatmap_frame(records)
    assert frame.iloc[0]["rating_band"] == "1200-1299"
    assert frame.iloc[0]["time_band"] == "15-30m"
