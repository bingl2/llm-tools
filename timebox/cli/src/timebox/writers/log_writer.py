"""log_writer: WorkLog -> 마크다운 문자열."""
from timebox.models import WorkLog

BLOCK_TYPE_DISPLAY: dict[str, str] = {
    "deep-work": "deep-work",
    "shallow": "shallow",
    "break": "break",
    "flex": "flex",
    "wrap-up": "wrap-up",
    "lunch": "lunch",
}


def write_log(log: WorkLog) -> str:
    """WorkLog -> 마크다운 문자열."""
    hhmm = log.timestamp.strftime("%H:%M")
    event_type = log.event_type.value
    block_start = log.block_start.strftime("%H:%M")
    block_end = log.block_end.strftime("%H:%M")
    block_type = log.block_type.value

    energy_line = f"- energy: {log.energy}" if log.energy is not None else ""

    lines = [f"# {hhmm} Timebox Log - {event_type}", ""]

    # Block
    lines.append("## Block")
    lines.append(f"{block_start}-{block_end} | {block_type}")
    if log.focus:
        lines.append(f"Focus: {log.focus}")
    lines.append("")

    # Event
    lines.append("## Event")
    lines.append(f"- type: {event_type}")
    lines.append(f"- related_to: {log.related_to}")
    if energy_line:
        lines.append(energy_line)
    if log.trigger:
        lines.append(f"- trigger: {log.trigger}")
    lines.append("")

    # Work Done
    lines.append("## Work Done")
    for item in log.work_done:
        lines.append(f"- {item}")
    lines.append("")

    # Status
    lines.append("## Status")
    for k, v in log.status.items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    # Decisions
    lines.append("## Decisions")
    for item in log.decisions:
        lines.append(f"- {item}")
    lines.append("")

    # Notes
    lines.append("## Notes")
    for item in log.notes:
        lines.append(f"- {item}")
    lines.append("")

    return "\n".join(lines)
