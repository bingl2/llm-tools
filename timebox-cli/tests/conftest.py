import pytest
from pathlib import Path
from timebox.models import TimeboxConfig


@pytest.fixture
def timebox_home(tmp_path: Path) -> Path:
    """테스트용 $TIMEBOX_HOME: 디렉토리 구조 생성."""
    home = tmp_path / "timebox"
    for d in ["plans", "logs", "reviews", "goals"]:
        (home / d).mkdir(parents=True)
    return home


@pytest.fixture
def default_config() -> TimeboxConfig:
    """기본 설정."""
    return TimeboxConfig(
        home="~/timebox",
        checkin_interval=15,
        deep_work_block=90,
        break_duration=15,
    )


@pytest.fixture
def env_home(timebox_home: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """$TIMEBOX_HOME 환경변수 설정."""
    monkeypatch.setenv("TIMEBOX_HOME", str(timebox_home))
    return timebox_home
