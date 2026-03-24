import os
from datetime import date, timedelta
from pathlib import Path


def get_home(override: str | None = None) -> Path:
    """$TIMEBOX_HOME 해석. override > 환경변수 > 기본값 순."""
    if override:
        return Path(override).expanduser()
    env = os.environ.get("TIMEBOX_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / "timebox"


def config_path(home: Path) -> Path:
    return home / "_config.md"


def plan_path(home: Path, d: date) -> Path:
    return home / "plans" / f"{d.isoformat()}.md"


def log_dir(home: Path, d: date) -> Path:
    return home / "logs" / d.isoformat()


def log_path(home: Path, d: date, hhmm: str, event_type: str) -> Path:
    return log_dir(home, d) / f"{hhmm}-timebox-{event_type}.md"


def daily_review_path(home: Path, d: date) -> Path:
    return home / "reviews" / f"{d.isoformat()}-timebox-review.md"


def weekly_review_path(home: Path, year: int, week: int) -> Path:
    return home / "reviews" / f"{year}-W{week:02d}-weekly-review.md"


def monthly_review_path(home: Path, year: int, month: int) -> Path:
    return home / "reviews" / f"{year}-{month:02d}-monthly-review.md"


def yearly_review_path(home: Path, year: int) -> Path:
    return home / "reviews" / f"{year}-yearly-review.md"


def foundation_path(home: Path, year: int) -> Path:
    return home / "goals" / f"{year}-foundation.md"


def yearly_goals_path(home: Path, year: int) -> Path:
    return home / "goals" / f"{year}.md"


def monthly_goals_path(home: Path, year: int, month: int) -> Path:
    return home / "goals" / f"{year}-{month:02d}.md"


def weekly_goals_path(home: Path, year: int, week: int) -> Path:
    return home / "goals" / f"{year}-W{week:02d}.md"


def ensure_dirs(home: Path) -> None:
    """timebox init: 디렉토리 구조 생성."""
    for d in ["plans", "logs", "reviews", "goals"]:
        (home / d).mkdir(parents=True, exist_ok=True)


def find_logs_for_date(home: Path, d: date) -> list[Path]:
    """특정 날짜의 로그 파일 목록 (시간순 정렬)."""
    ld = log_dir(home, d)
    if not ld.exists():
        return []
    return sorted(ld.glob("*.md"))


def find_recent_reviews(home: Path, d: date, count: int = 3) -> list[Path]:
    """최근 n개 daily review 파일."""
    review_dir = home / "reviews"
    if not review_dir.exists():
        return []
    reviews = sorted(review_dir.glob("*-timebox-review.md"), reverse=True)
    return reviews[:count]


def week_dates(year: int, week: int) -> list[date]:
    """ISO week의 월~일 날짜 리스트."""
    jan4 = date(year, 1, 4)  # 1월 4일은 항상 ISO week 1에 포함
    start = jan4 + timedelta(weeks=week - 1, days=-jan4.weekday())
    return [start + timedelta(days=i) for i in range(7)]
