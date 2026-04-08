"""goals 서브커맨드."""
from datetime import date
from typing import Optional

import typer

from timebox.models import GoalScope
from timebox.output import print_json, error_json
from timebox.parsers.goals_parser import parse_goals
from timebox.parsers.plan_parser import parse_plan
from timebox.parsers.review_parser import parse_daily_review
from timebox.paths import (
    get_home,
    weekly_goals_path,
    monthly_goals_path,
    yearly_goals_path,
    week_dates,
    find_logs_for_date,
    plan_path,
)
from timebox.tz import default_today

app = typer.Typer(help="목표 관리")


@app.command("show")
def show(
    scope: str = typer.Option("weekly", "--scope", help="yearly|monthly|weekly"),
    year: int = typer.Option(None, "--year", help="연도"),
    month: int = typer.Option(None, "--month", help="월 (monthly 전용)"),
    week: int = typer.Option(None, "--week", help="ISO 주차 (weekly 전용)"),
) -> None:
    """목표 파일을 JSON으로 출력."""
    home = get_home()
    today = default_today()

    _year = year if year is not None else today.year
    _month = month if month is not None else today.month
    _week = week if week is not None else int(today.strftime("%V"))

    if scope == "yearly":
        path = yearly_goals_path(home, _year)
        goal_scope = GoalScope.YEARLY
        period = str(_year)
    elif scope == "monthly":
        path = monthly_goals_path(home, _year, _month)
        goal_scope = GoalScope.MONTHLY
        period = f"{_year}-{_month:02d}"
    else:  # weekly
        path = weekly_goals_path(home, _year, _week)
        goal_scope = GoalScope.WEEKLY
        period = f"{_year}-W{_week:02d}"

    if not path.exists():
        print_json({"scope": scope, "period": period, "goals": []})
        return

    goal_set = parse_goals(path.read_text(), goal_scope, period)
    print_json({
        "scope": scope,
        "period": period,
        "goals": [
            {
                "id": g.id,
                "text": g.text,
                "status": g.status,
                "scope": g.scope.value,
                "success_criteria": g.success_criteria,
                "parent": g.parent,
            }
            for g in goal_set.goals
        ],
    })


@app.command("progress")
def progress(
    year: int = typer.Option(None, "--year", help="연도"),
    week: int = typer.Option(None, "--week", help="ISO 주차"),
) -> None:
    """주간 목표 진행 현황 (플랜 Big 3 참조 집계)."""
    home = get_home()
    today = default_today()

    _year = year if year is not None else today.year
    _week = week if week is not None else int(today.strftime("%V"))
    period = f"{_year}-W{_week:02d}"

    path = weekly_goals_path(home, _year, _week)
    if not path.exists():
        print_json({"week": period, "goals": []})
        return

    goal_set = parse_goals(path.read_text(), GoalScope.WEEKLY, period)

    # 해당 주의 플랜 파일에서 Big 3 related_goal 참조 수 집계
    dates = week_dates(_year, _week)
    goal_mentions: dict[str, int] = {g.id: 0 for g in goal_set.goals}

    for d in dates:
        pp = plan_path(home, d)
        if pp.exists():
            try:
                plan = parse_plan(pp.read_text(), d)
                for item in plan.big3:
                    if item.related_goal and item.related_goal in goal_mentions:
                        goal_mentions[item.related_goal] += 1
            except Exception:
                pass

    goals_progress = [
        {
            "id": g.id,
            "text": g.text,
            "status": g.status,
            "mentions": goal_mentions.get(g.id, 0),
        }
        for g in goal_set.goals
    ]

    print_json({
        "week": period,
        "goals": goals_progress,
    })
