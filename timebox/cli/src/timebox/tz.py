"""Timezone-aware date/time utilities for timebox."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

DEFAULT_TZ = "Asia/Seoul"


def get_tz(timezone: str = DEFAULT_TZ) -> ZoneInfo:
    """IANA timezone 문자열 -> ZoneInfo."""
    return ZoneInfo(timezone)


def today(timezone: str = DEFAULT_TZ) -> date:
    """timezone 기준 오늘 날짜."""
    return datetime.now(tz=get_tz(timezone)).date()


def now(timezone: str = DEFAULT_TZ) -> datetime:
    """timezone 기준 현재 시각."""
    return datetime.now(tz=get_tz(timezone))


def configured_tz() -> str:
    """config에서 timezone을 읽어 반환. 없으면 DEFAULT_TZ."""
    from timebox.paths import get_home, config_path

    home = get_home()
    cp = config_path(home)
    if cp.exists():
        from timebox.parsers.config_parser import parse_config

        config = parse_config(cp.read_text())
        return config.timezone
    return DEFAULT_TZ


def default_today() -> date:
    """config timezone 기준 오늘 날짜. config 없으면 Asia/Seoul."""
    return today(configured_tz())


def default_now() -> datetime:
    """config timezone 기준 현재 시각. config 없으면 Asia/Seoul."""
    return now(configured_tz())
