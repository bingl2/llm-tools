import os
from datetime import date
from pathlib import Path

from timebox.paths import (
    get_home,
    config_path,
    plan_path,
    log_dir,
    log_path,
    daily_review_path,
    weekly_review_path,
    ensure_dirs,
    find_logs_for_date,
    week_dates,
)


class TestGetHome:
    def test_override_takes_precedence(self):
        home = get_home(override="/custom/path")
        assert home == Path("/custom/path")

    def test_env_var_used(self, monkeypatch):
        monkeypatch.setenv("TIMEBOX_HOME", "/env/path")
        home = get_home()
        assert home == Path("/env/path")

    def test_default_is_home_timebox(self, monkeypatch):
        monkeypatch.delenv("TIMEBOX_HOME", raising=False)
        home = get_home()
        assert home == Path.home() / "timebox"

    def test_override_beats_env(self, monkeypatch):
        monkeypatch.setenv("TIMEBOX_HOME", "/env/path")
        home = get_home(override="/override/path")
        assert home == Path("/override/path")

    def test_tilde_expanded(self):
        home = get_home(override="~/my-timebox")
        assert "~" not in str(home)


class TestFilePaths:
    def test_config_path(self):
        assert config_path(Path("/tb")) == Path("/tb/_config.md")

    def test_plan_path(self):
        d = date(2026, 3, 24)
        assert plan_path(Path("/tb"), d) == Path("/tb/plans/2026-03-24.md")

    def test_log_dir(self):
        d = date(2026, 3, 24)
        assert log_dir(Path("/tb"), d) == Path("/tb/logs/2026-03-24")

    def test_log_path(self):
        d = date(2026, 3, 24)
        p = log_path(Path("/tb"), d, "0930", "deep-work")
        assert p == Path("/tb/logs/2026-03-24/0930-timebox-deep-work.md")

    def test_daily_review_path(self):
        d = date(2026, 3, 24)
        p = daily_review_path(Path("/tb"), d)
        assert p == Path("/tb/reviews/2026-03-24-timebox-review.md")

    def test_weekly_review_path(self):
        p = weekly_review_path(Path("/tb"), 2026, 13)
        assert p == Path("/tb/reviews/2026-W13-weekly-review.md")


class TestEnsureDirs:
    def test_creates_all_subdirs(self, tmp_path):
        home = tmp_path / "timebox"
        ensure_dirs(home)
        assert (home / "plans").is_dir()
        assert (home / "logs").is_dir()
        assert (home / "reviews").is_dir()
        assert (home / "goals").is_dir()

    def test_idempotent(self, tmp_path):
        home = tmp_path / "timebox"
        ensure_dirs(home)
        ensure_dirs(home)  # 두 번 호출해도 에러 없음
        assert (home / "plans").is_dir()


class TestFindLogsForDate:
    def test_returns_sorted_logs(self, timebox_home):
        from tests.factories import make_log
        d = date(2026, 3, 24)
        make_log(timebox_home, d, hhmm="1430")
        make_log(timebox_home, d, hhmm="0930")
        logs = find_logs_for_date(timebox_home, d)
        assert len(logs) == 2
        assert "0930" in logs[0].name
        assert "1430" in logs[1].name

    def test_empty_when_no_logs(self, timebox_home):
        d = date(2026, 1, 1)
        assert find_logs_for_date(timebox_home, d) == []


class TestWeekDates:
    def test_returns_seven_days(self):
        dates = week_dates(2026, 13)
        assert len(dates) == 7

    def test_starts_monday(self):
        dates = week_dates(2026, 13)
        assert dates[0].weekday() == 0  # Monday
