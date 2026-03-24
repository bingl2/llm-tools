import pytest
from typer.testing import CliRunner
from timebox.cli import app


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def cli(runner, env_home):
    """CLI를 env_home 환경에서 실행하는 헬퍼."""
    def invoke(*args: str):
        return runner.invoke(app, list(args))
    return invoke
