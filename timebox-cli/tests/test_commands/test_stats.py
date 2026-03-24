"""stats 커맨드 테스트."""
import json
from datetime import date

import pytest

from tests.factories import make_plan, make_config, make_log, make_daily_review


SAMPLE_DATE = date(2026, 3, 24)
SAMPLE_YEAR = 2026
SAMPLE_WEEK = 13
SAMPLE_MONTH = 3


class TestStatsToday:
    def test_returns_json(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        result = cli("stats", "today", "--date", "2026-03-24")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_has_big3_field(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        result = cli("stats", "today", "--date", "2026-03-24")
        data = json.loads(result.output)
        assert "big3" in data

    def test_has_completion_field(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        result = cli("stats", "today", "--date", "2026-03-24")
        data = json.loads(result.output)
        assert "completion" in data

    def test_has_block_adherence(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        result = cli("stats", "today", "--date", "2026-03-24")
        data = json.loads(result.output)
        assert "block_adherence" in data

    def test_has_energy_field(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        result = cli("stats", "today", "--date", "2026-03-24")
        data = json.loads(result.output)
        assert "energy" in data

    def test_has_ad_hoc_count(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        make_log(env_home, SAMPLE_DATE, event_type="ad-hoc")
        result = cli("stats", "today", "--date", "2026-03-24")
        data = json.loads(result.output)
        assert "ad_hoc_count" in data
        assert data["ad_hoc_count"] >= 1

    def test_empty_when_no_plan(self, cli, env_home):
        make_config(env_home)
        result = cli("stats", "today", "--date", "2099-01-01")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["date"] == "2099-01-01"
        assert data["big3_done"] == 0

    def test_error_when_no_config(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("stats", "today", "--date", "2026-03-24")
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data


class TestStatsWeek:
    def test_returns_json(self, cli, env_home):
        make_config(env_home)
        # 2026-W13: 2026-03-23 ~ 2026-03-29
        make_plan(env_home, date(2026, 3, 23))
        make_plan(env_home, date(2026, 3, 24))
        result = cli("stats", "week", "--year", "2026", "--week", "13")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_has_week_field(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, date(2026, 3, 23))
        result = cli("stats", "week", "--year", "2026", "--week", "13")
        data = json.loads(result.output)
        assert "week" in data

    def test_has_days_field(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, date(2026, 3, 24))
        result = cli("stats", "week", "--year", "2026", "--week", "13")
        data = json.loads(result.output)
        assert "days" in data
        assert isinstance(data["days"], list)

    def test_has_total_big3_done(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, date(2026, 3, 24))
        result = cli("stats", "week", "--year", "2026", "--week", "13")
        data = json.loads(result.output)
        assert "total_big3_done" in data

    def test_empty_week_returns_zero_stats(self, cli, env_home):
        make_config(env_home)
        # no plans at all
        result = cli("stats", "week", "--year", "2026", "--week", "13")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["total_big3_done"] == 0

    def test_error_when_no_config(self, cli, env_home):
        result = cli("stats", "week", "--year", "2026", "--week", "13")
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data


class TestStatsMonth:
    def test_returns_json(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, date(2026, 3, 1))
        result = cli("stats", "month", "--year", "2026", "--month", "3")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_has_month_field(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, date(2026, 3, 1))
        result = cli("stats", "month", "--year", "2026", "--month", "3")
        data = json.loads(result.output)
        assert "month" in data

    def test_has_days_field(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, date(2026, 3, 1))
        result = cli("stats", "month", "--year", "2026", "--month", "3")
        data = json.loads(result.output)
        assert "days" in data

    def test_empty_month_returns_zero_stats(self, cli, env_home):
        make_config(env_home)
        result = cli("stats", "month", "--year", "2026", "--month", "3")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["total_big3_done"] == 0

    def test_error_when_no_config(self, cli, env_home):
        result = cli("stats", "month", "--year", "2026", "--month", "3")
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data


class TestStatsCarryOver:
    def test_returns_json(self, cli, env_home):
        make_config(env_home)
        make_daily_review(env_home, date(2026, 3, 24))
        result = cli("stats", "carry-over")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_has_items_field(self, cli, env_home):
        make_config(env_home)
        make_daily_review(env_home, date(2026, 3, 24))
        result = cli("stats", "carry-over")
        data = json.loads(result.output)
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_no_reviews_returns_empty(self, cli, env_home):
        make_config(env_home)
        result = cli("stats", "carry-over")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["items"] == []
