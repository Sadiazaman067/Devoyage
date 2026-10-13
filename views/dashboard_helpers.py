"""
Pure logic for the dashboard -- no Kivy imports on purpose.

Anything that can be decided from plain data (how many steps are done,
what the header says, whether the layout should stack) lives here, so
tests/test_dashboard_helpers.py can check it without opening a window.
views/dashboard.py only turns these answers into widgets.
"""
from datetime import datetime

DONE = "done"  # Shared Vocabulary: a step's status is exactly "pending" or "done".

# Below this window width (in dp), the two columns stack vertically.
STACK_BREAKPOINT_DP = 900

_NUMBER_WORDS = {
    1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
    6: "Six", 7: "Seven", 8: "Eight", 9: "Nine",
}


def count_done(steps):
    return sum(1 for step in steps if step.get("status") == DONE)


def progress_text(steps):
    """[done, pending, done] -> '2 of 3 done'."""
    return f"{count_done(steps)} of {len(steps)} done"


def progress_fraction(steps):
    """0.0 to 1.0 for the progress bar fill. An empty roadmap is 0, not a crash."""
    if not steps:
        return 0.0
    return count_done(steps) / len(steps)


def next_step_index(steps):
    """Index of the first pending step (gets the 'Up next' badge), or None if all done.

    Uses the list order as given -- the controller already sorted by position,
    and the view must not re-sort.
    """
    for index, step in enumerate(steps):
        if step.get("status") != DONE:
            return index
    return None


def format_generated_date(generated_at):
    """'2026-10-06T12:00:00' or SQLite's '2026-10-06 12:00:00' -> 'Oct 6'.

    Returns '' if the value is missing or not a date, so the header never crashes.
    """
    if not generated_at:
        return ""
    try:
        moment = datetime.fromisoformat(str(generated_at))
    except ValueError:
        return ""
    # f"{moment.day}" instead of %-d: %-d doesn't exist on Windows.
    return f"{moment:%b} {moment.day}"


def eyebrow_text(generated_at):
    """The small uppercase label above the title: 'YOUR ROADMAP · GENERATED OCT 6'."""
    date = format_generated_date(generated_at)
    text = f"Your roadmap · generated {date}" if date else "Your roadmap"
    return text.upper()


def headline(steps):
    """'Six steps toward your goal'. Words for 1-9 (the LLM contract allows 5-9 steps)."""
    count = len(steps)
    word = _NUMBER_WORDS.get(count, str(count))
    noun = "step" if count == 1 else "steps"
    return f"{word} {noun} toward your goal"


def use_stacked_layout(width_dp):
    """True when the window is too narrow for steps + the 340dp not-now panel side by side."""
    return width_dp < STACK_BREAKPOINT_DP
