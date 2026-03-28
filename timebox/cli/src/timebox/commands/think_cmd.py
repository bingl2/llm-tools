"""think 서브커맨드."""
import sys
from datetime import date, time, datetime, timedelta
from typing import Optional

import typer

from timebox.paths import get_home, think_path, thinks_dir, find_thinks_for_date
from timebox.parsers.think_parser import parse_think
from timebox.output import print_json, error_json

app = typer.Typer(help="생각 기록")


@app.command("create")
def create(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
    time_str: str = typer.Option(..., "--time", help="HH:MM"),
    name: str = typer.Option(..., "--name", help="짧은 영문 이름 (kebab-case)"),
) -> None:
    """think 파일 생성. 마크다운 내용은 stdin으로 받는다."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else date.today()

    parts = time_str.split(":")
    hhmm = f"{int(parts[0]):02d}{int(parts[1]):02d}"

    content = sys.stdin.read()
    if not content.strip():
        error_json("stdin에서 내용을 읽을 수 없습니다.", code="EMPTY_CONTENT")

    tpath = think_path(home, d, hhmm, name)
    tpath.parent.mkdir(parents=True, exist_ok=True)
    tpath.write_text(content)

    print_json({"created": str(tpath), "date": d.isoformat(), "name": name})


@app.command("show")
def show(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
    name: Optional[str] = typer.Option(None, "--name", help="파일 이름 (확장자 제외)"),
) -> None:
    """think 파일 조회."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else date.today()

    files = find_thinks_for_date(home, d)
    if not files:
        error_json(f"{d.isoformat()}에 think 기록이 없습니다.", code="THINK_NOT_FOUND")

    if name:
        matched = [f for f in files if name in f.stem]
        if not matched:
            error_json(f"'{name}' think를 찾을 수 없습니다.", code="THINK_NOT_FOUND")
        target = matched[0]
    else:
        target = files[-1]  # 가장 최근

    entry = parse_think(target.read_text(), str(target))
    print_json({
        "file": str(target),
        "date": entry.timestamp.strftime("%Y-%m-%d %H:%M"),
        "short_name": entry.short_name,
        "tags": entry.tags,
        "mood": entry.mood,
        "content": entry.raw_content,
    })


@app.command("list")
def list_thinks(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
    from_str: Optional[str] = typer.Option(None, "--from", help="시작일 YYYY-MM-DD"),
    to_str: Optional[str] = typer.Option(None, "--to", help="종료일 YYYY-MM-DD"),
) -> None:
    """think 파일 목록 조회."""
    home = get_home()

    if from_str and to_str:
        start = date.fromisoformat(from_str)
        end = date.fromisoformat(to_str)
    elif date_str:
        start = end = date.fromisoformat(date_str)
    else:
        start = end = date.today()

    entries = []
    d = start
    while d <= end:
        for f in find_thinks_for_date(home, d):
            entry = parse_think(f.read_text(), str(f))
            entries.append({
                "file": str(f),
                "date": entry.timestamp.strftime("%Y-%m-%d %H:%M"),
                "short_name": entry.short_name,
                "tags": entry.tags,
                "mood": entry.mood,
            })
        d += timedelta(days=1)

    print_json({"count": len(entries), "entries": entries})
