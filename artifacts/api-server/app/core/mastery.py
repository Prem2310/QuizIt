"""Leitner-style spaced repetition for the "practice your weak topics" mode.

Five boxes. A wrong answer drops a question back to box 1 (due immediately, so it
resurfaces in the very next weak-topics session). A correct answer promotes it and
pushes the next review further out.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

MAX_BOX = 5
BOX_INTERVAL_DAYS: dict[int, int] = {1: 0, 2: 1, 3: 3, 4: 7, 5: 14}


def next_box_level(current_box: int, is_correct: bool) -> int:
    if not is_correct:
        return 1
    return min(current_box + 1, MAX_BOX)


def due_at_for_box(box_level: int, now: datetime | None = None) -> datetime:
    now = now or datetime.now(UTC)
    return now + timedelta(days=BOX_INTERVAL_DAYS.get(box_level, 0))
