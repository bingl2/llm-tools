"""log サブコマンド."""
import sys
from datetime import date, time, datetime
from typing import Optional

import typer

from timebox.paths import get_home, plan_path, log_path, log_dir
from timebox.parsers.plan_parser import parse_plan
from timebox.parsers.config_parser import parse_config
from timebox.paths import config_path
from timebox.writers.log_writer import write_log
from timebox.calculator import current_block
from timebox.output import print_json, error_json
from timebox.models import WorkLog, EventType, BlockType

app = typer.Typer(help="작업 로그")


@app.command("create")
def create(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
    time_str: str = typer.Option(..., "--time", help="HH:MM"),
    event_type_str: str = typer.Option("deep-work", "--type", help="이벤트 타입"),
    related: str = typer.Option("ad-hoc", "--related", help="관련 Big3 (예: Big 1)"),
    summary: str = typer.Option("", "--summary", help="작업 요약"),
    energy_val: Optional[int] = typer.Option(None, "--energy", help="에너지 레벨 1-5"),
    decisions_str: str = typer.Option("", "--decisions", help="결정 사항"),
    notes_str: str = typer.Option("", "--notes", help="노트"),
) -> None:
    """로그 파일 생성."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else date.today()
    ppath = plan_path(home, d)

    if not ppath.exists():
        error_json(f"플랜 파일이 없습니다: {ppath}", code="PLAN_NOT_FOUND")

    plan = parse_plan(ppath.read_text(), d)

    # Parse time
    parts = time_str.split(":")
    now_time = time(int(parts[0]), int(parts[1]))

    # Determine current block from plan
    block_info = current_block(plan, now_time)
    if block_info["current_block"]:
        cb = block_info["current_block"]
        bt_str = cb["type"]
        b_start_str, b_end_str = cb["time"].split("-")
    else:
        bt_str = "deep-work"
        b_start_str = time_str
        b_end_str = time_str

    BLOCK_TYPE_MAP = {
        "deep-work": BlockType.DEEP_WORK,
        "shallow": BlockType.SHALLOW,
        "break": BlockType.BREAK,
        "flex": BlockType.FLEX,
        "wrap-up": BlockType.WRAP_UP,
        "lunch": BlockType.LUNCH,
    }

    def _parse_t(s: str) -> time:
        p = s.split(":")
        return time(int(p[0]), int(p[1]))

    decisions = [decisions_str] if decisions_str else []
    notes = [notes_str] if notes_str else []

    log = WorkLog(
        timestamp=datetime(d.year, d.month, d.day, now_time.hour, now_time.minute),
        event_type=EventType(event_type_str),
        related_to=related,
        energy=energy_val,
        trigger=None,
        block_start=_parse_t(b_start_str),
        block_end=_parse_t(b_end_str),
        block_type=BLOCK_TYPE_MAP.get(bt_str, BlockType.DEEP_WORK),
        focus=block_info["current_block"]["focus"] if block_info["current_block"] else "",
        summary=summary,
        work_done=[summary] if summary else [],
        decisions=decisions,
        notes=notes,
        status={},
    )

    hhmm = now_time.strftime("%H%M")
    lpath = log_path(home, d, hhmm, event_type_str)
    lpath.parent.mkdir(parents=True, exist_ok=True)

    md = write_log(log)
    lpath.write_text(md)
    print_json({"created": str(lpath), "date": d.isoformat()})
