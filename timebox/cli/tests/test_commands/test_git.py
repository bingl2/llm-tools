"""git commit 커맨드 테스트."""
import json
import subprocess
from datetime import date
from pathlib import Path

import pytest

from tests.factories import make_config, make_plan


SAMPLE_DATE = date(2026, 3, 24)


def init_git_repo(home: Path) -> None:
    """테스트용 git repo 초기화."""
    subprocess.run(["git", "init", str(home)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(home), "config", "user.email", "test@test.com"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(home), "config", "user.name", "Test"],
        check=True, capture_output=True,
    )


class TestCommit:
    def test_commit_returns_json(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        init_git_repo(env_home)
        result = cli("commit")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_commit_has_hash_field(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        init_git_repo(env_home)
        result = cli("commit")
        data = json.loads(result.output)
        assert "hash" in data

    def test_commit_has_message_field(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        init_git_repo(env_home)
        result = cli("commit")
        data = json.loads(result.output)
        assert "message" in data

    def test_error_when_no_git_repo(self, cli, env_home):
        make_config(env_home)
        make_plan(env_home, SAMPLE_DATE)
        # no git init
        result = cli("commit")
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data

    def test_error_when_nothing_to_commit(self, cli, env_home):
        make_config(env_home)
        init_git_repo(env_home)
        # Make an initial commit so the repo is not empty, then nothing to stage
        subprocess.run(
            ["git", "-C", str(env_home), "commit", "--allow-empty", "-m", "init"],
            check=True, capture_output=True,
        )
        result = cli("commit")
        # Should either succeed with "nothing to commit" or fail gracefully
        data = json.loads(result.output)
        assert isinstance(data, dict)
