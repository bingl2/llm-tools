"""log create 커맨드 테스트."""
import json
from datetime import date

import pytest

from tests.factories import make_plan, make_config


SAMPLE_DATE = date(2026, 3, 24)


class TestLogCreate:
    def test_creates_log_file(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        result = cli(
            "log", "create",
            "--date", "2026-03-24",
            "--time", "09:30",
            "--type", "deep-work",
            "--related", "Big 1",
            "--summary", "엔드포인트 정리 완료",
            "--energy", "4",
        )
        assert result.exit_code == 0
        log_dir = env_home / "logs" / "2026-03-24"
        assert log_dir.exists()
        logs = list(log_dir.glob("*.md"))
        assert len(logs) == 1

    def test_log_file_content(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        result = cli(
            "log", "create",
            "--date", "2026-03-24",
            "--time", "09:30",
            "--type", "deep-work",
            "--related", "Big 1",
            "--summary", "엔드포인트 정리 완료",
            "--energy", "4",
        )
        assert result.exit_code == 0
        log_dir = env_home / "logs" / "2026-03-24"
        logs = list(log_dir.glob("*.md"))
        content = logs[0].read_text()
        assert "deep-work" in content
        assert "Big 1" in content
        assert "엔드포인트 정리 완료" in content

    def test_output_is_json(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        result = cli(
            "log", "create",
            "--date", "2026-03-24",
            "--time", "09:30",
            "--type", "deep-work",
            "--related", "Big 1",
            "--summary", "작업 요약",
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "path" in data or "ok" in data or "created" in data or isinstance(data, dict)

    def test_error_when_no_plan(self, cli, env_home):
        make_config(env_home)
        result = cli(
            "log", "create",
            "--date", "2099-01-01",
            "--time", "09:30",
            "--type", "deep-work",
            "--related", "Big 1",
            "--summary", "테스트",
        )
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data
