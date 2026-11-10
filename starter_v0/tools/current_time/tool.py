from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from tools._shared import err

WEEKDAYS_VI = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]


def _utcnow() -> datetime:
    """Separate function so unit tests can freeze the clock."""
    return datetime.now(timezone.utc)


def current_time(utc_offset_hours: int = 7) -> dict[str, Any]:
    """Return the current date/time for a UTC offset (default +7 = Vietnam). Pure local, no network."""
    try:
        try:
            offset = int(utc_offset_hours)
        except (TypeError, ValueError):
            offset = 7
        if not -12 <= offset <= 14:
            raise ValueError(f"utc_offset_hours must be between -12 and 14, got {offset}")
        now = _utcnow().astimezone(timezone(timedelta(hours=offset)))
        return {
            "tool": "current_time",
            "utc_offset_hours": offset,
            "iso": now.isoformat(timespec="seconds"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": WEEKDAYS_VI[now.weekday()],
        }
    except Exception as exc:
        return err("current_time", exc)
