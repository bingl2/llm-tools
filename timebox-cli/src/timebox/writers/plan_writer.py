"""plan_writer: DayPlan -> 마크다운 문자열."""
from timebox.models import DayPlan, CheckStatus


# 블록 타입 -> 표시 문자열 매핑 (plan_parser BLOCK_TYPE_MAP의 역방향)
BLOCK_TYPE_DISPLAY: dict[str, str] = {
    "deep-work": "Deep Work",
    "shallow": "Shallow Work",
    "break": "Break",
    "flex": "Flex",
    "wrap-up": "Wrap-up",
    "lunch": "Lunch",
}

STATUS_CHAR: dict[str, str] = {
    CheckStatus.DONE: "x",
    CheckStatus.PARTIAL: "~",
    CheckStatus.TODO: " ",
}


def write_plan(plan: DayPlan) -> str:
    """DayPlan -> 마크다운 문자열."""
    lines = [f"# {plan.date.isoformat()} ({plan.weekday}) Timebox", ""]

    # Big 3
    lines.append("## Big 3")
    for item in plan.big3:
        status_char = STATUS_CHAR.get(item.status, " ")
        blocks_str = f" (~{item.estimated_blocks:g}블록)" if item.estimated_blocks is not None else ""
        lines.append(f"{item.number}. [{status_char}] {item.text}{blocks_str}")
    lines.append("")

    # Schedule
    lines.append("## Schedule")
    lines.append("")
    for block in plan.blocks:
        start = block.start.strftime("%H:%M")
        end = block.end.strftime("%H:%M")
        display = BLOCK_TYPE_DISPLAY.get(block.block_type.value, block.block_type.value)
        lines.append(f"### {start}-{end} | {display}")
        if block.focus:
            lines.append(f"**Focus**: {block.focus}")
        for item in block.items:
            status_char = STATUS_CHAR.get(item.status, " ")
            lines.append(f"- [{status_char}] {item.text}")
        lines.append("")

    # Energy Log
    lines.append("## Energy Log")
    lines.append("| Time | Energy | Notes |")
    lines.append("|------|--------|-------|")
    for entry in plan.energy_log:
        t = entry.time.strftime("%H:%M")
        lines.append(f"| {t} | {entry.level}/5 | {entry.notes} |")
    lines.append("")

    # Notes
    lines.append("## Notes")
    if plan.notes:
        lines.append(plan.notes)
    lines.append("")

    return "\n".join(lines)
