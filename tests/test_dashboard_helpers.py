"""
Tests for the dashboard's pure logic (views/dashboard_helpers.py) and the
color helper in views/theme.py. Neither imports Kivy, so these run
without opening a window.

Run from the repo root:
    python -m pytest tests/test_dashboard_helpers.py
(`python -m` puts the repo root on sys.path so `import views...` works.)

No pytest installed? This also works:
    python tests/test_dashboard_helpers.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from views.dashboard_helpers import (  # noqa: E402
    count_done,
    eyebrow_text,
    format_generated_date,
    headline,
    next_step_index,
    progress_fraction,
    progress_text,
    use_stacked_layout,
)
from views.theme import PALETTES, hex_to_rgba, rgba  # noqa: E402


def _steps(*statuses):
    return [{"position": i, "status": s} for i, s in enumerate(statuses, start=1)]


# ---- progress -------------------------------------------------------------

def test_progress_text_counts_done_steps():
    steps = _steps("done", "done", "pending", "pending", "pending", "pending")
    assert progress_text(steps) == "2 of 6 done"


def test_progress_text_all_and_none_done():
    assert progress_text(_steps("done", "done")) == "2 of 2 done"
    assert progress_text(_steps("pending", "pending")) == "0 of 2 done"


def test_progress_with_no_steps_does_not_crash():
    assert progress_text([]) == "0 of 0 done"
    assert progress_fraction([]) == 0.0


def test_progress_fraction():
    assert progress_fraction(_steps("done", "pending", "pending", "done")) == 0.5


def test_only_the_exact_string_done_counts():
    # Shared Vocabulary: status is exactly "pending" or "done".
    assert count_done(_steps("Done", "DONE", "done ", "done")) == 1


# ---- up next ----------------------------------------------------------------

def test_next_step_is_first_pending_in_given_order():
    assert next_step_index(_steps("done", "done", "pending", "pending")) == 2


def test_next_step_none_when_all_done_or_empty():
    assert next_step_index(_steps("done", "done")) is None
    assert next_step_index([]) is None


def test_next_step_does_not_resort_by_position():
    # The view must trust the controller's order, not sort by position.
    steps = [
        {"position": 2, "status": "pending"},
        {"position": 1, "status": "pending"},
    ]
    assert next_step_index(steps) == 0


# ---- header text ------------------------------------------------------------

def test_format_generated_date_iso_and_sqlite_formats():
    assert format_generated_date("2026-10-06T12:00:00") == "Oct 6"
    assert format_generated_date("2026-10-06 12:00:00") == "Oct 6"  # SQLite datetime('now')
    assert format_generated_date("2026-11-23") == "Nov 23"


def test_format_generated_date_bad_input_returns_empty():
    assert format_generated_date(None) == ""
    assert format_generated_date("") == ""
    assert format_generated_date("not a date") == ""


def test_eyebrow_text():
    assert eyebrow_text("2026-10-06T12:00:00") == "YOUR ROADMAP · GENERATED OCT 6"
    assert eyebrow_text(None) == "YOUR ROADMAP"


def test_headline_uses_words_for_contract_range():
    assert headline(_steps(*["pending"] * 6)) == "Six steps toward your goal"
    assert headline(_steps(*["pending"] * 9)) == "Nine steps toward your goal"
    assert headline(_steps("pending")) == "One step toward your goal"
    assert headline(_steps(*["pending"] * 12)) == "12 steps toward your goal"


# ---- layout -----------------------------------------------------------------

def test_stacked_layout_breakpoint():
    assert use_stacked_layout(600) is True
    assert use_stacked_layout(899) is True
    assert use_stacked_layout(900) is False
    assert use_stacked_layout(1200) is False


# ---- theme ------------------------------------------------------------------

def test_hex_to_rgba():
    assert hex_to_rgba("#FFFFFF") == (1.0, 1.0, 1.0, 1.0)
    assert hex_to_rgba("000000") == (0.0, 0.0, 0.0, 1.0)
    assert hex_to_rgba("#CC3333") == (0.8, 0.2, 0.2, 1.0)  # Phase 1 error red, unchanged
    assert hex_to_rgba("#00000000") == (0.0, 0.0, 0.0, 0.0)
    assert hex_to_rgba("#FFFFFF", alpha=0.5)[3] == 0.5


def test_hex_to_rgba_rejects_bad_input():
    try:
        hex_to_rgba("#FFF")
    except ValueError:
        return
    raise AssertionError("expected ValueError for a 3-digit hex color")


def test_every_palette_color_parses():
    for name in PALETTES["light"]:
        assert len(rgba(name)) == 4


if __name__ == "__main__":
    tests = [value for key, value in sorted(globals().items()) if key.startswith("test_")]
    for test in tests:
        test()
        print("ok  ", test.__name__)
    print(f"{len(tests)} passed")
