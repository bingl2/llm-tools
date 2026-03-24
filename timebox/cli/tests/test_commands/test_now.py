import json
from datetime import date

from tests.factories import make_plan


SAMPLE_DATE = date(2026, 3, 24)


class TestNow:
    def test_shows_current_block(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("now", "--date", "2026-03-24", "--time", "09:30")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["current_block"] is not None
        assert data["current_block"]["type"] == "deep-work"

    def test_shows_remaining_minutes(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("now", "--date", "2026-03-24", "--time", "10:00")
        data = json.loads(result.output)
        assert data["remaining_minutes"] == 30  # 10:30까지 30분

    def test_shows_next_block(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("now", "--date", "2026-03-24", "--time", "09:30")
        data = json.loads(result.output)
        assert data["next_block"] is not None

    def test_shows_big3_progress(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("now", "--date", "2026-03-24", "--time", "14:00")
        data = json.loads(result.output)
        assert "big3_progress" in data

    def test_no_plan_returns_empty(self, cli, env_home):
        result = cli("now", "--date", "2099-01-01", "--time", "09:00")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["current_block"] is None
        assert data["today_ad_hoc_count"] == 0

    def test_after_hours_no_current_block(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("now", "--date", "2026-03-24", "--time", "22:00")
        data = json.loads(result.output)
        assert data["current_block"] is None
