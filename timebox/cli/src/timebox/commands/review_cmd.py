"""review サブコマンド."""
import json
import sys
from datetime import date
from typing import Optional

import typer

from timebox.paths import get_home, daily_review_path
from timebox.parsers.review_parser import parse_daily_review
from timebox.writers.review_writer import write_daily_review
from timebox.output import print_json, error_json, load_stdin_json

app = typer.Typer(help="리뷰")


@app.command("create")
def create(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
) -> None:
    """stdin JSON에서 daily review 마크다운 파일 생성."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else date.today()
    path = daily_review_path(home, d)

    data = load_stdin_json()

    path.parent.mkdir(parents=True, exist_ok=True)
    md = write_daily_review(data)
    path.write_text(md)
    print_json({"created": str(path), "date": d.isoformat()})


@app.command("show")
def show(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
) -> None:
    """daily review 조회 (JSON)."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else date.today()
    path = daily_review_path(home, d)

    if not path.exists():
        print_json({"date": d.isoformat(), "weekday": "", "big3_review": [], "carry_over": [], "energy_pattern": "", "tomorrow_top1": "", "notes": ""})
        return

    data = parse_daily_review(path.read_text(), d)
    print_json(data)
