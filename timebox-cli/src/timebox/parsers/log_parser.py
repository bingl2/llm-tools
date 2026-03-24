import re
from datetime import datetime, time

from timebox.models import WorkLog, EventType, BlockType
from timebox.parsers.common import split_sections, parse_time
from timebox.parsers.plan_parser import _parse_block_type

# ── Event 메타데이터 ──
EVENT_META_RE = re.compile(
    r"^-\s+(type|related_to|energy|trigger):\s+(.+)$", re.MULTILINE
)

# ── Block 헤더 ──
BLOCK_LINE_RE = re.compile(r"(\d{2}:\d{2})-(\d{2}:\d{2})\s+\|\s+(.+)")

# ── 타임스탬프 (파일명에서) ──
LOG_FILENAME_RE = re.compile(r"(\d{4})-timebox-(.+)\.md$")


def parse_log(content: str, filepath: str = "") -> WorkLog:
    """logs/{YYYY-MM-DD}/{HHmm}-timebox-{type}.md -> WorkLog."""
    sections = split_sections(content)

    # Event 메타데이터
    event_section = sections.get("Event", "")
    meta: dict[str, str] = {}
    for m in EVENT_META_RE.finditer(event_section):
        meta[m.group(1)] = m.group(2).strip()

    # Block 정보
    block_section = sections.get("Block", "")
    block_match = BLOCK_LINE_RE.search(block_section)

    block_start = parse_time(block_match.group(1)) if block_match else time(0, 0)
    block_end = parse_time(block_match.group(2)) if block_match else time(0, 0)
    block_type_str = block_match.group(3).strip() if block_match else "deep-work"
    block_type = _parse_block_type(block_type_str)

    # Focus
    focus_line = ""
    for line in block_section.splitlines():
        if line.startswith("Focus:"):
            focus_line = line.replace("Focus:", "").strip()
            break

    # Work Done
    work_section = sections.get("Work Done", "")
    work_done = [
        line.lstrip("- ").strip()
        for line in work_section.splitlines()
        if line.strip().startswith("-")
    ]

    # Status
    status_section = sections.get("Status", "")
    status: dict[str, str] = {}
    for line in status_section.splitlines():
        if line.strip().startswith("-"):
            parts = line.lstrip("- ").split(":", 1)
            if len(parts) == 2:
                status[parts[0].strip()] = parts[1].strip()

    # Decisions
    decisions_section = sections.get("Decisions", "")
    decisions = [
        line.lstrip("- ").strip()
        for line in decisions_section.splitlines()
        if line.strip().startswith("-")
    ]

    # Notes
    notes_section = sections.get("Notes", "")
    notes = [
        line.lstrip("- ").strip()
        for line in notes_section.splitlines()
        if line.strip().startswith("-")
    ]

    # 타임스탬프: 파일명에서 추출
    timestamp = datetime.now()
    if filepath:
        fname_match = LOG_FILENAME_RE.search(filepath)
        if fname_match:
            hhmm = fname_match.group(1)
            try:
                hour, minute = int(hhmm[:2]), int(hhmm[2:])
                timestamp = timestamp.replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
            except (ValueError, IndexError):
                pass

    # summary: Work Done의 첫 항목 또는 빈 문자열
    summary = work_done[0] if work_done else ""

    return WorkLog(
        timestamp=timestamp,
        event_type=EventType(meta.get("type", "deep-work")),
        related_to=meta.get("related_to", "ad-hoc"),
        energy=int(meta["energy"]) if "energy" in meta else None,
        trigger=meta.get("trigger"),
        block_start=block_start,
        block_end=block_end,
        block_type=block_type,
        focus=focus_line,
        summary=summary,
        work_done=work_done,
        decisions=decisions,
        notes=notes,
        status=status,
    )
