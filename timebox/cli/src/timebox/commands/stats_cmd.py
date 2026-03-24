"""stats 서브커맨드."""
import calendar
from datetime import date
from typing import Optional

import typer

from timebox.paths import (
    get_home, plan_path, config_path, find_logs_for_date,
    week_dates, find_recent_reviews, daily_review_path,
)
from timebox.parsers.plan_parser import parse_plan
from timebox.parsers.log_parser import parse_log
from timebox.parsers.config_parser import parse_config
from timebox.parsers.review_parser import parse_daily_review
from timebox.calculator import daily_stats, weekly_stats, carry_over_streak
from timebox.output import print_json, error_json

app = typer.Typer(help="통계")


@app.command("today")
def today(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
) -> None:
    """오늘 통계 계산 (JSON)."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else date.today()

    ppath = plan_path(home, d)
    if not ppath.exists():
        print_json({"date": d.isoformat(), "big3_done": 0, "big3_total": 0, "blocks_completed": 0, "blocks_total": 0, "ad_hoc_count": 0, "avg_energy": None})
        return

    cpath = config_path(home)
    if not cpath.exists():
        error_json(f"설정 파일이 없습니다: {cpath}", code="CONFIG_NOT_FOUND")

    plan = parse_plan(ppath.read_text(), d)
    config = parse_config(cpath.read_text())

    log_files = find_logs_for_date(home, d)
    logs = [parse_log(lf.read_text(), str(lf)) for lf in log_files]

    stats = daily_stats(plan, logs, config)
    print_json(stats)


def _load_daily_stats(home, d: date, config):
    """단일 날짜 플랜+로그 -> DailyStats. 플랜 없으면 None."""
    pp = plan_path(home, d)
    if not pp.exists():
        return None
    try:
        plan = parse_plan(pp.read_text(), d)
        log_files = find_logs_for_date(home, d)
        logs = [parse_log(lf.read_text(), str(lf)) for lf in log_files]
        return daily_stats(plan, logs, config)
    except Exception:
        return None


@app.command("week")
def week(
    year: Optional[int] = typer.Option(None, "--year", help="연도"),
    week_num: Optional[int] = typer.Option(None, "--week", help="ISO 주차"),
) -> None:
    """주간 통계 (JSON)."""
    home = get_home()
    today = date.today()
    _year = year if year is not None else today.year
    _week = week_num if week_num is not None else int(today.strftime("%V"))

    cpath = config_path(home)
    if not cpath.exists():
        error_json(f"설정 파일이 없습니다: {cpath}", code="CONFIG_NOT_FOUND")

    config = parse_config(cpath.read_text())
    dates = week_dates(_year, _week)

    day_stats = []
    for d in dates:
        ds = _load_daily_stats(home, d, config)
        if ds is not None:
            day_stats.append(ds)

    period = f"{_year}-W{_week:02d}"
    wstats = weekly_stats(day_stats, period)
    print_json(wstats)


@app.command("month")
def month(
    year: Optional[int] = typer.Option(None, "--year", help="연도"),
    month_num: Optional[int] = typer.Option(None, "--month", help="월"),
) -> None:
    """월간 통계 (JSON)."""
    home = get_home()
    today = date.today()
    _year = year if year is not None else today.year
    _month = month_num if month_num is not None else today.month

    cpath = config_path(home)
    if not cpath.exists():
        error_json(f"설정 파일이 없습니다: {cpath}", code="CONFIG_NOT_FOUND")

    config = parse_config(cpath.read_text())
    _, days_in_month = calendar.monthrange(_year, _month)
    dates = [date(_year, _month, d) for d in range(1, days_in_month + 1)]

    day_stats = []
    for d in dates:
        ds = _load_daily_stats(home, d, config)
        if ds is not None:
            day_stats.append(ds)

    period = f"{_year}-{_month:02d}"
    mstats = weekly_stats(day_stats, period)

    from dataclasses import asdict
    from timebox.output import TimeboxEncoder
    import json
    days_serialized = json.loads(
        json.dumps([asdict(d) for d in mstats.days], cls=TimeboxEncoder)
    )
    mstats_dict = {
        "month": period,
        "year": _year,
        "month_number": _month,
        "days": days_serialized,
        "total_big3_done": mstats.total_big3_done,
        "total_big3_scheduled": mstats.total_big3_scheduled,
        "avg_block_adherence": mstats.avg_block_adherence,
        "avg_energy": mstats.avg_energy,
        "total_ad_hoc": mstats.total_ad_hoc,
        "energy_by_day": mstats.energy_by_day,
    }
    print_json(mstats_dict)


@app.command("carry-over")
def carry_over(
    count: int = typer.Option(14, "--count", help="최근 리뷰 수"),
) -> None:
    """carry-over 항목 연속 일수 통계 (JSON)."""
    home = get_home()
    today = date.today()

    review_files = find_recent_reviews(home, today, count)
    reviews = []
    for rf in review_files:
        # 파일명에서 날짜 추출: "2026-03-24-timebox-review.md"
        stem = rf.stem  # "2026-03-24-timebox-review"
        date_str = stem[:10]
        try:
            d = date.fromisoformat(date_str)
            reviews.append(parse_daily_review(rf.read_text(), d))
        except (ValueError, Exception):
            pass

    items = carry_over_streak(reviews)
    print_json({
        "items": [
            {
                "name": item.name,
                "first_appeared": item.first_appeared.isoformat(),
                "streak_days": item.streak_days,
                "times_scheduled": item.times_scheduled,
                "times_dropped": item.times_dropped,
            }
            for item in items
        ]
    })
