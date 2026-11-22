import pytest

from perf.measure_ui_responsiveness import EventLoopMonitor, summarize


def test_event_loop_monitor_counts_deadlines_missed_during_a_stall():
    monitor = EventLoopMonitor(interval_ms=16)
    monitor.next_deadline = 1.0

    monitor.record_callback(1.05)

    assert monitor.delays_ms == pytest.approx([50.0])
    assert monitor.missed_intervals == 3


def test_summarize_uses_nearest_rank_p95():
    result = summarize([1.0, 2.0, 3.0, 4.0, 5.0])

    assert result == {
        "count": 5,
        "median_ms": 3.0,
        "p95_ms": 5.0,
        "max_ms": 5.0,
    }
