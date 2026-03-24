"""goals 커맨드 테스트."""
import json
from datetime import date

import pytest

from tests.factories import make_config


SAMPLE_DATE = date(2026, 3, 24)
SAMPLE_YEAR = 2026
SAMPLE_MONTH = 3
SAMPLE_WEEK = 13


def make_weekly_goals(home, year=SAMPLE_YEAR, week=SAMPLE_WEEK) -> None:
    path = home / "goals" / f"{year}-W{week:02d}.md"
    path.write_text(f"""# {year}-W{week:02d} 주간 목표

## Goals

- [W1] 코드 리뷰 완료
- [W2] 테스트 커버리지 80%

## Notes
이번 주 핵심 목표
""")


def make_yearly_goals(home, year=SAMPLE_YEAR) -> None:
    path = home / "goals" / f"{year}.md"
    path.write_text(f"""# {year} 연간 목표

## Goals

- [Y1] 사이드 프로젝트 런칭
- [Y2] 기술 블로그 12편

## Notes
올해 큰 그림
""")


def make_monthly_goals(home, year=SAMPLE_YEAR, month=SAMPLE_MONTH) -> None:
    path = home / "goals" / f"{year}-{month:02d}.md"
    path.write_text(f"""# {year}-{month:02d} 월간 목표

## Goals

- [M1] API 리팩토링 완료
- [M2] 문서화

## Notes
이번 달 목표
""")


class TestGoalsShow:
    def test_weekly_returns_json(self, cli, env_home):
        make_config(env_home)
        make_weekly_goals(env_home)
        result = cli("goals", "show", "--scope", "weekly",
                     "--year", str(SAMPLE_YEAR), "--week", str(SAMPLE_WEEK))
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_weekly_has_scope_field(self, cli, env_home):
        make_config(env_home)
        make_weekly_goals(env_home)
        result = cli("goals", "show", "--scope", "weekly",
                     "--year", str(SAMPLE_YEAR), "--week", str(SAMPLE_WEEK))
        data = json.loads(result.output)
        assert "scope" in data
        assert data["scope"] == "weekly"

    def test_weekly_has_goals_field(self, cli, env_home):
        make_config(env_home)
        make_weekly_goals(env_home)
        result = cli("goals", "show", "--scope", "weekly",
                     "--year", str(SAMPLE_YEAR), "--week", str(SAMPLE_WEEK))
        data = json.loads(result.output)
        assert "goals" in data
        assert isinstance(data["goals"], list)

    def test_yearly_returns_json(self, cli, env_home):
        make_config(env_home)
        make_yearly_goals(env_home)
        result = cli("goals", "show", "--scope", "yearly",
                     "--year", str(SAMPLE_YEAR))
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "scope" in data
        assert data["scope"] == "yearly"

    def test_monthly_returns_json(self, cli, env_home):
        make_config(env_home)
        make_monthly_goals(env_home)
        result = cli("goals", "show", "--scope", "monthly",
                     "--year", str(SAMPLE_YEAR), "--month", str(SAMPLE_MONTH))
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "scope" in data
        assert data["scope"] == "monthly"

    def test_empty_when_no_file(self, cli, env_home):
        make_config(env_home)
        result = cli("goals", "show", "--scope", "weekly",
                     "--year", "2099", "--week", "01")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["scope"] == "weekly"
        assert data["goals"] == []


class TestGoalsProgress:
    def test_returns_json(self, cli, env_home):
        make_config(env_home)
        make_weekly_goals(env_home)
        result = cli("goals", "progress",
                     "--year", str(SAMPLE_YEAR), "--week", str(SAMPLE_WEEK))
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_has_week_field(self, cli, env_home):
        make_config(env_home)
        make_weekly_goals(env_home)
        result = cli("goals", "progress",
                     "--year", str(SAMPLE_YEAR), "--week", str(SAMPLE_WEEK))
        data = json.loads(result.output)
        assert "week" in data

    def test_has_goals_progress_field(self, cli, env_home):
        make_config(env_home)
        make_weekly_goals(env_home)
        result = cli("goals", "progress",
                     "--year", str(SAMPLE_YEAR), "--week", str(SAMPLE_WEEK))
        data = json.loads(result.output)
        assert "goals" in data

    def test_empty_when_no_goals_file(self, cli, env_home):
        make_config(env_home)
        result = cli("goals", "progress", "--year", "2099", "--week", "01")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["goals"] == []
