"""E2E 워크플로우 테스트: init → plan create → log create → stats today → review create → stats carry-over."""
import json
from datetime import date
from pathlib import Path

import pytest
from typer.testing import CliRunner
from timebox.cli import app
from timebox.paths import plan_path, log_dir, daily_review_path


SAMPLE_DATE = date(2026, 3, 24)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(runner, env_home):
    def invoke(*args: str):
        return runner.invoke(app, list(args))
    return invoke


class TestFullWorkflow:
    def test_full_workflow(self, cli, runner, env_home):
        """전체 워크플로우: init → plan → log → stats today → review → carry-over."""

        # 1. init
        result = cli("init")
        assert result.exit_code == 0, result.output
        assert (env_home / "plans").exists()
        assert (env_home / "logs").exists()
        assert (env_home / "reviews").exists()
        assert (env_home / "goals").exists()
        assert (env_home / "_config.md").exists()

        # 2. plan create (stdin JSON) - big3 items require 'number' field
        plan_data = {
            "big3": [
                {"number": 1, "text": "API 리팩토링", "estimated_blocks": 2},
                {"number": 2, "text": "버그 수정", "estimated_blocks": 1},
                {"number": 3, "text": "문서 작성", "estimated_blocks": 1},
            ],
            "blocks": [
                {"start": "09:00", "end": "10:30", "block_type": "deep-work", "focus": "Big 3 #1"},
                {"start": "10:30", "end": "10:45", "block_type": "break", "focus": ""},
                {"start": "10:45", "end": "12:00", "block_type": "deep-work", "focus": "Big 3 #2"},
            ],
        }
        result = runner.invoke(app, ["plan", "create", "--date", "2026-03-24"],
                               input=json.dumps(plan_data))
        assert result.exit_code == 0, result.output
        assert plan_path(env_home, SAMPLE_DATE).exists()

        # 3. log create (uses CLI options, not stdin JSON)
        result = runner.invoke(app, [
            "log", "create",
            "--date", "2026-03-24",
            "--time", "09:30",
            "--type", "deep-work",
            "--related", "Big 1",
            "--energy", "4",
            "--summary", "엔드포인트 정리 완료",
        ])
        assert result.exit_code == 0, result.output
        assert log_dir(env_home, SAMPLE_DATE).exists()
        assert len(list(log_dir(env_home, SAMPLE_DATE).glob("*.md"))) >= 1

        # 4. stats today
        result = cli("stats", "today", "--date", "2026-03-24")
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "big3" in data
        assert "completion" in data
        assert "block_adherence" in data
        assert "energy" in data
        assert "ad_hoc_count" in data

        # 5. review create (stdin JSON)
        review_data = {
            "big3_results": [
                {"number": 1, "text": "API 리팩토링", "status": "done", "result_text": "완료!"},
                {"number": 2, "text": "버그 수정", "status": "partial", "result_text": "70%"},
                {"number": 3, "text": "문서 작성", "status": "todo", "result_text": "미착수"},
            ],
            "one_liner": "오늘 집중 좋았다",
        }
        result = runner.invoke(app, ["review", "create", "--date", "2026-03-24"],
                               input=json.dumps(review_data))
        assert result.exit_code == 0, result.output
        assert daily_review_path(env_home, SAMPLE_DATE).exists()

        # 6. stats carry-over
        result = cli("stats", "carry-over")
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_stats_today_without_plan_returns_empty(self, cli, env_home):
        """플랜 없이 stats today 실행 → 빈 데이터 반환."""
        cli("init")
        result = cli("stats", "today", "--date", "2099-12-31")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["big3_done"] == 0

    def test_stats_week_after_plan_creation(self, cli, runner, env_home):
        """플랜 생성 후 stats week 실행 → days 필드에 데이터 포함."""
        cli("init")

        plan_data = {
            "big3": [{"number": 1, "text": "작업", "estimated_blocks": 1}],
            "blocks": [{"start": "09:00", "end": "10:30", "block_type": "deep-work", "focus": "Big 3 #1"}],
        }
        runner.invoke(app, ["plan", "create", "--date", "2026-03-24"],
                      input=json.dumps(plan_data))

        result = cli("stats", "week", "--year", "2026", "--week", "13")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["days"]) >= 1
