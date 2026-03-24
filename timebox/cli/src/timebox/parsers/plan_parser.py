import re
from datetime import date, time

from timebox.models import (
    DayPlan,
    Big3Item,
    TimeBlock,
    EnergyEntry,
    CheckItem,
    CheckStatus,
    BlockType,
)
from timebox.parsers.common import (
    split_sections,
    parse_check_status,
    parse_checkboxes,
    parse_time,
)

# ── Big 3 정규식 ──
# 매칭: "1. [ ] API 리팩토링 (~2블록)"
BIG3_RE = re.compile(
    r"^(\d+)\.\s+\[([ x~])\]\s+"  # 번호 + 체크박스
    r"(.+?)"  # 텍스트
    r"(?:\s+\(~([\d.]+)블록\))?"  # 블록 수 (선택)
    r"\s*$",
    re.MULTILINE,
)

# ── 블록 스케줄 정규식 ──
# 매칭: "### 09:00-10:30 | Deep Work"
BLOCK_HEADER_RE = re.compile(
    r"^###\s+(\d{2}:\d{2})-(\d{2}:\d{2})\s+\|\s+(.+)$",
    re.MULTILINE,
)

# ── Energy Log 테이블 행 ──
# 매칭: "| 09:30 | 4/5 | 집중 좋음 |"
ENERGY_RE = re.compile(
    r"^\|\s*(\d{2}:\d{2})\s*\|\s*(\d)/5\s*\|\s*(.+?)\s*\|$",
    re.MULTILINE,
)

# ── 블록 타입 매핑 ──
BLOCK_TYPE_MAP: dict[str, BlockType] = {
    "deep work": BlockType.DEEP_WORK,
    "deep": BlockType.DEEP_WORK,
    "shallow work": BlockType.SHALLOW,
    "shallow": BlockType.SHALLOW,
    "break": BlockType.BREAK,
    "flex": BlockType.FLEX,
    "wrap-up": BlockType.WRAP_UP,
    "wrap up": BlockType.WRAP_UP,
    "lunch": BlockType.LUNCH,
}


def _parse_block_type(text: str) -> BlockType:
    """블록 타입 문자열 -> BlockType enum. 관대하게 매칭."""
    normalized = text.strip().lower()
    for key, bt in BLOCK_TYPE_MAP.items():
        if key in normalized:
            return bt
    return BlockType.DEEP_WORK  # 기본값


# ── Focus 파싱 ──
FOCUS_RE = re.compile(r"\*\*Focus\*\*:\s*(.+)")

WEEKDAY_NAMES = ["월", "화", "수", "목", "금", "토", "일"]


def parse_plan(content: str, file_date: date) -> DayPlan:
    """plans/{YYYY-MM-DD}.md -> DayPlan."""
    sections = split_sections(content)
    weekday = WEEKDAY_NAMES[file_date.weekday()]

    # Big 3
    big3_section = sections.get("Big 3", "")
    big3_items: list[Big3Item] = []
    for m in BIG3_RE.finditer(big3_section):
        number = int(m.group(1))
        status = parse_check_status(m.group(2))
        text = m.group(3).strip()
        est_blocks = float(m.group(4)) if m.group(4) else None

        big3_items.append(Big3Item(
            number=number,
            text=text,
            status=status,
            estimated_blocks=est_blocks,
            raw_line=m.group(0),
        ))

    # Schedule 블록
    blocks: list[TimeBlock] = []
    block_matches = list(BLOCK_HEADER_RE.finditer(content))
    for i, m in enumerate(block_matches):
        start = parse_time(m.group(1))
        end = parse_time(m.group(2))
        block_type = _parse_block_type(m.group(3))

        # 블록 본문: 이 헤더부터 다음 ### 헤더까지
        body_start = m.end()
        body_end = (
            block_matches[i + 1].start()
            if i + 1 < len(block_matches)
            else len(content)
        )
        body = content[body_start:body_end]

        # Focus 추출
        focus_match = FOCUS_RE.search(body)
        focus = focus_match.group(1).strip() if focus_match else None

        # 체크리스트
        items = [
            CheckItem(text=t, status=s, raw_line=r)
            for s, t, r in parse_checkboxes(body)
        ]

        blocks.append(TimeBlock(
            start=start,
            end=end,
            block_type=block_type,
            focus=focus,
            items=items,
        ))

    # Energy Log
    energy_section = sections.get("Energy Log", "")
    energy_log: list[EnergyEntry] = []
    for m in ENERGY_RE.finditer(energy_section):
        energy_log.append(EnergyEntry(
            time=parse_time(m.group(1)),
            level=int(m.group(2)),
            notes=m.group(3).strip(),
        ))

    # Notes
    notes = sections.get("Notes", "")

    return DayPlan(
        date=file_date,
        weekday=weekday,
        big3=big3_items,
        blocks=blocks,
        energy_log=energy_log,
        notes=notes,
        raw_content=content,
    )
