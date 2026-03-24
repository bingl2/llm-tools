"""review create/show 커맨드 테스트."""
import json
from datetime import date

import pytest

from tests.factories import make_daily_review, make_config


SAMPLE_DATE = date(2026, 3, 24)

SAMPLE_REVIEW_JSON = {
    "date": "2026-03-24",
    "weekday": "화",
    "big3_results": [
        {"number": 1, "text": "API 리팩토링", "status": "done", "result_text": "완료!", "estimated_blocks": 2.0, "actual_blocks": 2.0},
        {"number": 2, "text": "프론트 버그", "status": "partial", "result_text": "70%", "estimated_blocks": 1.0, "actual_blocks": 0.5},
    ],
    "success_rate": "1/2",
    "estimation_accuracy": [
        {"name": "API 리팩토링", "estimated": 2.0, "actual": 2.0, "ratio": 1.0},
    ],
    "block_analysis": [
        {"time": "09:00-10:30", "block_type": "deep-work", "planned": "API 리팩토링", "actual": "API 리팩토링", "match": True},
    ],
    "block_adherence": 80.0,
    "energy_pattern": {"peak": "09:00-12:00", "low": "15:00-17:00"},
    "goal_alignment": {"direct": 2, "maintenance": 1},
    "carry_forward": {
        "big3_candidates": ["프론트 버그 수정"],
        "open_loops": ["디자이너 피드백 대기"],
    },
    "one_liner": "오전 집중 좋았고, 오후에 무너짐",
    "reflection": "오늘 오전에 몰입이 잘 됐다.",
    "coach_notes": "오전 2블록 연속 몰입이 인상적입니다.",
}


class TestReviewCreate:
    def test_creates_review_file(self, runner, env_home):
        make_config(env_home)
        from timebox.cli import app
        result = runner.invoke(
            app,
            ["review", "create", "--date", "2026-03-24"],
            input=json.dumps(SAMPLE_REVIEW_JSON),
        )
        assert result.exit_code == 0
        review_path = env_home / "reviews" / "2026-03-24-timebox-review.md"
        assert review_path.exists()

    def test_review_file_content(self, runner, env_home):
        make_config(env_home)
        from timebox.cli import app
        runner.invoke(
            app,
            ["review", "create", "--date", "2026-03-24"],
            input=json.dumps(SAMPLE_REVIEW_JSON),
        )
        review_path = env_home / "reviews" / "2026-03-24-timebox-review.md"
        content = review_path.read_text()
        assert "2026-03-24" in content
        assert "API 리팩토링" in content

    def test_output_is_json(self, runner, env_home):
        make_config(env_home)
        from timebox.cli import app
        result = runner.invoke(
            app,
            ["review", "create", "--date", "2026-03-24"],
            input=json.dumps(SAMPLE_REVIEW_JSON),
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)


class TestReviewShow:
    def test_shows_review_as_json(self, cli, env_home):
        make_config(env_home)
        make_daily_review(env_home, SAMPLE_DATE)
        result = cli("review", "show", "--date", "2026-03-24")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_review_has_date(self, cli, env_home):
        make_config(env_home)
        make_daily_review(env_home, SAMPLE_DATE)
        result = cli("review", "show", "--date", "2026-03-24")
        data = json.loads(result.output)
        assert "date" in data
        assert data["date"] == "2026-03-24"

    def test_review_has_big3_results(self, cli, env_home):
        make_config(env_home)
        make_daily_review(env_home, SAMPLE_DATE)
        result = cli("review", "show", "--date", "2026-03-24")
        data = json.loads(result.output)
        assert "big3_results" in data

    def test_empty_when_no_review(self, cli, env_home):
        result = cli("review", "show", "--date", "2099-01-01")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["date"] == "2099-01-01"
        assert data["big3_review"] == []
