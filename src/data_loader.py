from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Entry:
    session_id: str
    course_code: str
    slot_label: str
    time_label: str
    status: str
    code: str


@dataclass
class Day:
    anchor: str
    label: str
    entries: List[Entry]


@dataclass
class Model:
    days: List[Day]


def load_model(path: Path) -> Model:
    payload = json.loads(path.read_text(encoding="utf-8"))
    days: List[Day] = []
    for day in payload.get("days", []):
        entries = [
            Entry(
                session_id=e["session_id"],
                course_code=e["course_code"],
                slot_label=e["slot_label"],
                time_label=e["time_label"],
                status=e.get("status", "pending"),
                code=e.get("code", ""),
            )
            for e in day.get("entries", [])
        ]
        days.append(Day(anchor=day["anchor"], label=day["label"], entries=entries))
    return Model(days=days)


def find_entry(model: Model, session_id: str) -> Optional[Tuple[Day, Entry]]:
    for day in model.days:
        for entry in day.entries:
            if entry.session_id == session_id:
                return day, entry
    return None


def day_groups(model: Model) -> List[Dict[str, object]]:
    groups: List[Dict[str, object]] = []
    for day in model.days:
        groups.append(
            {
                "anchor": day.anchor,
                "label": day.label,
                "entries": [
                    {
                        "session_id": entry.session_id,
                        "course_code": entry.course_code,
                        "slot_label": entry.slot_label,
                        "time_label": entry.time_label,
                        "status": entry.status,
                    }
                    for entry in day.entries
                ],
            }
        )
    return groups
