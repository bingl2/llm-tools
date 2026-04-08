import json
import sys
from datetime import date
from typing import Optional

import typer

from timebox.paths import get_home, plan_path
from timebox.parsers.plan_parser import parse_plan
from timebox.writers.plan_writer import write_plan
from timebox.output import print_json, error_json, load_stdin_json
from timebox.tz import default_today

app = typer.Typer(help="일간 플랜")


@app.command("show")
def show(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
) -> None:
    """플랜 조회 (JSON)."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else default_today()
    path = plan_path(home, d)

    if not path.exists():
        print_json({"date": d.isoformat(), "weekday": "", "big3": [], "blocks": [], "energy_log": [], "notes": ""})
        return

    plan = parse_plan(path.read_text(), d)
    print_json(plan)


@app.command("create")
def create(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
) -> None:
    """stdin JSON에서 플랜 마크다운 파일 생성."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else default_today()
    path = plan_path(home, d)

    data = load_stdin_json()

    # Build DayPlan from JSON then write markdown
    from timebox.models import (
        DayPlan, Big3Item, TimeBlock, EnergyEntry, CheckStatus, BlockType,
    )
    from timebox.parsers.common import parse_time

    STATUS_MAP = {"done": CheckStatus.DONE, "partial": CheckStatus.PARTIAL, "todo": CheckStatus.TODO}
    BLOCK_TYPE_MAP = {
        "deep-work": BlockType.DEEP_WORK,
        "shallow": BlockType.SHALLOW,
        "break": BlockType.BREAK,
        "flex": BlockType.FLEX,
        "wrap-up": BlockType.WRAP_UP,
        "lunch": BlockType.LUNCH,
    }

    big3 = [
        Big3Item(
            number=item["number"],
            text=item["text"],
            status=STATUS_MAP.get(item.get("status", "todo"), CheckStatus.TODO),
            estimated_blocks=item.get("estimated_blocks"),
            related_goal=item.get("related_goal"),
            raw_line="",
        )
        for item in data.get("big3", [])
    ]

    blocks = [
        TimeBlock(
            start=parse_time(b["start"]),
            end=parse_time(b["end"]),
            block_type=BLOCK_TYPE_MAP.get(b.get("block_type", "deep-work"), BlockType.DEEP_WORK),
            focus=b.get("focus"),
        )
        for b in data.get("blocks", [])
    ]

    energy_log = [
        EnergyEntry(
            time=parse_time(e["time"]),
            level=e["level"],
            notes=e.get("notes", ""),
        )
        for e in data.get("energy_log", [])
    ]

    plan = DayPlan(
        date=d,
        weekday=data.get("weekday", ""),
        big3=big3,
        blocks=blocks,
        energy_log=energy_log,
        notes=data.get("notes", ""),
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    md = write_plan(plan)
    path.write_text(md)
    print_json({"created": str(path), "date": d.isoformat()})


@app.command("check")
def check(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
    item: str = typer.Option(..., "--item", help="토글할 항목 텍스트 (부분 일치)"),
) -> None:
    """체크리스트 항목 토글 [ ] <-> [x]."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else default_today()
    path = plan_path(home, d)

    if not path.exists():
        error_json(f"플랜 파일이 없습니다: {path}", code="PLAN_NOT_FOUND")

    content = path.read_text()

    # Find the line containing the item text
    lines = content.splitlines(keepends=True)
    found = False
    new_lines = []
    for line in lines:
        if item in line and not found:
            if "- [ ]" in line or "] " in line:
                if "[x]" in line:
                    new_line = line.replace("[x]", "[ ]", 1)
                    found = True
                elif "[ ]" in line:
                    new_line = line.replace("[ ]", "[x]", 1)
                    found = True
                elif "[~]" in line:
                    new_line = line.replace("[~]", "[x]", 1)
                    found = True
                else:
                    new_line = line
            else:
                new_line = line
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    if not found:
        # Try Big3 number format: "1. [ ] text"
        new_lines = []
        for line in lines:
            if item in line and not found:
                if "[x]" in line:
                    new_line = line.replace("[x]", "[ ]", 1)
                    found = True
                elif "[ ]" in line:
                    new_line = line.replace("[ ]", "[x]", 1)
                    found = True
                elif "[~]" in line:
                    new_line = line.replace("[~]", "[x]", 1)
                    found = True
                else:
                    new_line = line
                new_lines.append(new_line)
            else:
                new_lines.append(line)

    if not found:
        error_json(f"항목을 찾을 수 없습니다: {item}", code="ITEM_NOT_FOUND")

    path.write_text("".join(new_lines))
    print_json({"toggled": item, "date": d.isoformat()})


@app.command("energy")
def energy(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
    time_str: str = typer.Option(..., "--time", help="HH:MM"),
    level: int = typer.Option(..., "--level", help="에너지 레벨 1-5"),
    notes: str = typer.Option("", "--notes", help="메모"),
) -> None:
    """Energy Log 테이블에 행 추가."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else default_today()
    path = plan_path(home, d)

    if not path.exists():
        error_json(f"플랜 파일이 없습니다: {path}", code="PLAN_NOT_FOUND")

    content = path.read_text()
    new_row = f"| {time_str} | {level}/5 | {notes} |"

    # Insert row before the closing empty line after the table header
    # Find the Energy Log section separator line "|---..." and append after last table row
    lines = content.splitlines(keepends=True)
    new_lines = []
    inserted = False
    i = 0
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        # After the separator line in Energy Log table, find end of table
        if "|------|--------|-------|" in line and not inserted:
            # Collect existing table rows
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                new_lines.append(lines[j])
                j += 1
            # Append new row
            new_lines.append(new_row + "\n")
            inserted = True
            i = j
            continue
        i += 1

    if not inserted:
        error_json("Energy Log 테이블을 찾을 수 없습니다", code="TABLE_NOT_FOUND")

    path.write_text("".join(new_lines))
    print_json({"added": new_row, "date": d.isoformat()})
