from perf.run_ui_benchmark_matrix import summarize_runs


def test_summarize_runs_aggregates_medians_worst_cases_and_missed_intervals():
    records = [
        {
            "page": "activity",
            "items": 50,
            "data_source": "synthetic",
            "source_counts": {"activity_events": 50},
            "data_loading_ms": 1,
            "widget_construction_ms": 10,
            "initial_paint_and_snapshot_ms": 12,
            "wheel_to_processed_snapshot": {
                "median_ms": 5,
                "p95_ms": 10,
                "max_ms": 15,
            },
            "event_loop_timer_samples": {"max_ms": 2},
            "event_loop_missed_intervals": 1,
        },
        {
            "page": "activity",
            "items": 50,
            "data_source": "synthetic",
            "source_counts": {"activity_events": 50},
            "data_loading_ms": 2,
            "widget_construction_ms": 20,
            "initial_paint_and_snapshot_ms": 14,
            "wheel_to_processed_snapshot": {
                "median_ms": 7,
                "p95_ms": 12,
                "max_ms": 30,
            },
            "event_loop_timer_samples": {"max_ms": 4},
            "event_loop_missed_intervals": 2,
        },
        {
            "page": "activity",
            "items": 50,
            "data_source": "synthetic",
            "source_counts": {"activity_events": 50},
            "data_loading_ms": 3,
            "widget_construction_ms": 30,
            "initial_paint_and_snapshot_ms": 16,
            "wheel_to_processed_snapshot": {
                "median_ms": 6,
                "p95_ms": 11,
                "max_ms": 20,
            },
            "event_loop_timer_samples": {"max_ms": 3},
            "event_loop_missed_intervals": 0,
        },
    ]

    summary = summarize_runs(records)

    assert summary == {
        "page": "activity",
        "items": 50,
        "runs": 3,
        "data_source": "synthetic",
        "source_counts": {"activity_events": 50},
        "data_loading_median_ms": 2,
        "construction_median_ms": 20,
        "initial_median_ms": 14,
        "wheel_median_ms": 6,
        "wheel_p95_median_ms": 11,
        "wheel_max_worst_ms": 30,
        "timer_max_worst_ms": 4,
        "missed_intervals_total": 3,
    }


def test_summarize_runs_allows_real_page_without_scroll_overflow():
    record = {
        "page": "my-devices",
        "items": 2,
        "data_source": "real",
        "source_counts": {
            "activity_events": None,
            "connected_usb_devices": 22,
            "configured_usb_devices": 2,
            "displays": 2,
        },
        "data_loading_ms": 25,
        "widget_construction_ms": 50,
        "initial_paint_and_snapshot_ms": 15,
        "wheel_to_processed_snapshot": {
            "median_ms": None,
            "p95_ms": None,
            "max_ms": None,
        },
        "event_loop_timer_samples": {
            "max_ms": None,
        },
        "event_loop_missed_intervals": 0,
    }

    summary = summarize_runs([record])

    assert summary["items"] == 2
    assert summary["wheel_median_ms"] is None
    assert summary["timer_max_worst_ms"] is None
