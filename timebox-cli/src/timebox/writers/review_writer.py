"""review_writer: dict -> 마크다운 문자열."""

STATUS_CHAR = {
    "done": "x",
    "partial": "~",
    "todo": " ",
}


def write_daily_review(data: dict) -> str:
    """dict (from LLM via stdin JSON) -> daily review 마크다운."""
    d = data.get("date", "")
    weekday = data.get("weekday", "")
    lines = [f"# {d} ({weekday}) Timebox Review", ""]

    # Big 3 Results
    lines.append("## Big 3 Results")
    big3_results = data.get("big3_results", [])
    done_count = sum(1 for r in big3_results if r.get("status") == "done")
    for r in big3_results:
        status_char = STATUS_CHAR.get(r.get("status", "todo"), " ")
        text = r.get("text", "")
        result_text = r.get("result_text", "")
        lines.append(f"{r['number']}. [{status_char}] {text} → {result_text}")
    lines.append("")
    lines.append(f"Success Rate: {data.get('success_rate', f'{done_count}/{len(big3_results)}')}")
    lines.append("")

    # Estimation Accuracy
    lines.append("## Estimation Accuracy")
    lines.append("| Big 3 | 예상 | 실제 | 배율 |")
    lines.append("|-------|------|------|------|")
    for item in data.get("estimation_accuracy", []):
        name = item.get("name", "")
        estimated = item.get("estimated", 0)
        actual = item.get("actual", 0)
        ratio = item.get("ratio", 0)
        lines.append(f"| {name} | {estimated:g}블록 | {actual:g}블록 | {ratio:.1f}x |")
    lines.append("")

    # Block Analysis
    lines.append("## Block Analysis")
    lines.append("| Block | Plan | Actual | Match |")
    lines.append("|-------|------|--------|-------|")
    for b in data.get("block_analysis", []):
        t = b.get("time", "")
        bt = b.get("block_type", "")
        planned = b.get("planned", "")
        actual = b.get("actual", "")
        match = "O" if b.get("match") else "X"
        lines.append(f"| {t} {bt} | {planned} | {actual} | {match} |")
    lines.append("")
    adherence = data.get("block_adherence", 0)
    lines.append(f"Block Adherence: {adherence:.0f}%")
    lines.append("")

    # Energy Pattern
    lines.append("## Energy Pattern")
    energy = data.get("energy_pattern", {})
    if isinstance(energy, dict):
        if "peak" in energy:
            lines.append(f"- Peak: {energy['peak']}")
        if "low" in energy:
            lines.append(f"- Low: {energy['low']}")
        for k, v in energy.items():
            if k not in ("peak", "low"):
                lines.append(f"- {k}: {v}")
    lines.append("")

    # Goal Alignment
    lines.append("## Goal Alignment")
    goal = data.get("goal_alignment", {})
    if isinstance(goal, dict):
        direct = goal.get("direct", 0)
        maintenance = goal.get("maintenance", 0)
        lines.append(f"- 목표 직접 기여: {direct}블록")
        lines.append(f"- 유지/운영: {maintenance}블록")
    lines.append("")

    # Carry Forward
    lines.append("## Carry Forward")
    carry = data.get("carry_forward", {})
    lines.append("### 내일 Big 3 후보")
    for i, candidate in enumerate(carry.get("big3_candidates", []), 1):
        lines.append(f"{i}. {candidate}")
    lines.append("")
    lines.append("### 오픈 루프")
    for loop in carry.get("open_loops", []):
        lines.append(f"- {loop}")
    lines.append("")

    # Daily One-liner
    lines.append("## Daily One-liner")
    one_liner = data.get("one_liner", "")
    if one_liner:
        lines.append(f"> {one_liner}")
    lines.append("")

    # Reflection
    lines.append("## Reflection")
    reflection = data.get("reflection", "")
    if reflection:
        lines.append(reflection)
    lines.append("")

    # Coach's Notes
    lines.append("## Coach's Notes")
    coach_notes = data.get("coach_notes", "")
    if coach_notes:
        lines.append(coach_notes)
    lines.append("")

    return "\n".join(lines)
