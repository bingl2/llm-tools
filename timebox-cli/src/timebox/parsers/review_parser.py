"""review_parser: daily review 마크다운 -> dict."""
import re
from datetime import date

from timebox.parsers.common import split_sections

WEEKDAY_NAMES = ["월", "화", "수", "목", "금", "토", "일"]

# Big 3 result line: "1. [x] API 리팩토링 → 완료!"
BIG3_RESULT_RE = re.compile(
    r"^(\d+)\.\s+\[([ x~])\]\s+(.+?)\s+→\s+(.+)$",
    re.MULTILINE,
)

# Success Rate: "1/3"
SUCCESS_RATE_RE = re.compile(r"Success Rate:\s*(\S+)")

# Block Adherence: "Block Adherence: 50%"
ADHERENCE_RE = re.compile(r"Block Adherence:\s*([\d.]+)%")

# One-liner: "> text"
ONE_LINER_RE = re.compile(r"^>\s+(.+)$", re.MULTILINE)

STATUS_MAP = {" ": "todo", "x": "done", "~": "partial"}


def parse_daily_review(content: str, file_date: date) -> dict:
    """daily review 마크다운 -> dict."""
    sections = split_sections(content)
    weekday = WEEKDAY_NAMES[file_date.weekday()]

    # Big 3 Results
    big3_section = sections.get("Big 3 Results", "")
    big3_results = []
    for m in BIG3_RESULT_RE.finditer(big3_section):
        status_char = m.group(2)
        big3_results.append({
            "number": int(m.group(1)),
            "text": m.group(3).strip(),
            "status": STATUS_MAP.get(status_char, "todo"),
            "result_text": m.group(4).strip(),
        })

    success_rate_m = SUCCESS_RATE_RE.search(big3_section)
    success_rate = success_rate_m.group(1) if success_rate_m else ""

    # Estimation Accuracy
    estimation_accuracy: list[dict] = []

    # Block Analysis
    block_analysis_section = sections.get("Block Analysis", "")
    block_analysis: list[dict] = []

    adherence_m = ADHERENCE_RE.search(block_analysis_section)
    block_adherence = float(adherence_m.group(1)) if adherence_m else 0.0

    # Energy Pattern
    energy_section = sections.get("Energy Pattern", "")
    energy_pattern: dict = {}
    for line in energy_section.splitlines():
        line = line.strip()
        if line.startswith("- Peak:"):
            energy_pattern["peak"] = line.replace("- Peak:", "").strip()
        elif line.startswith("- Low:"):
            energy_pattern["low"] = line.replace("- Low:", "").strip()

    # Goal Alignment
    goal_section = sections.get("Goal Alignment", "")
    goal_alignment: dict = {}

    # Carry Forward
    carry_section = sections.get("Carry Forward", "")
    big3_candidates: list[str] = []
    open_loops: list[str] = []
    in_candidates = False
    in_loops = False
    for line in carry_section.splitlines():
        stripped = line.strip()
        if "내일 Big 3 후보" in stripped:
            in_candidates = True
            in_loops = False
        elif "오픈 루프" in stripped:
            in_candidates = False
            in_loops = True
        elif in_candidates and re.match(r"^\d+\.\s+", stripped):
            big3_candidates.append(re.sub(r"^\d+\.\s+", "", stripped))
        elif in_loops and stripped.startswith("-"):
            open_loops.append(stripped.lstrip("- ").strip())

    carry_forward = {"big3_candidates": big3_candidates, "open_loops": open_loops}

    # Daily One-liner
    one_liner_section = sections.get("Daily One-liner", "")
    one_liner_m = ONE_LINER_RE.search(one_liner_section)
    one_liner = one_liner_m.group(1).strip() if one_liner_m else ""

    # Reflection
    reflection = sections.get("Reflection", "").strip()

    # Coach's Notes
    coach_notes = sections.get("Coach's Notes", "").strip()

    return {
        "date": file_date.isoformat(),
        "weekday": weekday,
        "big3_results": big3_results,
        "success_rate": success_rate,
        "estimation_accuracy": estimation_accuracy,
        "block_analysis": block_analysis,
        "block_adherence": block_adherence,
        "energy_pattern": energy_pattern,
        "goal_alignment": goal_alignment,
        "carry_forward": carry_forward,
        "one_liner": one_liner,
        "reflection": reflection,
        "coach_notes": coach_notes,
    }
