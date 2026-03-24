from datetime import date, time
from typing import Optional

import typer

from timebox.paths import get_home, plan_path, find_logs_for_date
from timebox.parsers.plan_parser import parse_plan
from timebox.parsers.log_parser import parse_log
from timebox.calculator import current_block
from timebox.output import print_json, error_json
from timebox.models import EventType


def now(
    date_str: Optional[str] = typer.Option(None, "--date", help="YYYY-MM-DD"),
    time_str: Optional[str] = typer.Option(None, "--time", help="HH:MM (테스트용)"),
) -> None:
    """현재 블록 + 남은 시간 + 다음 체크리스트 항목."""
    home = get_home()
    d = date.fromisoformat(date_str) if date_str else date.today()
    path = plan_path(home, d)

    if not path.exists():
        print_json({"current_block": None, "next_block": None, "remaining_minutes": 0, "today_ad_hoc_count": 0, "message": "플랜이 아직 없습니다"})
        return

    plan = parse_plan(path.read_text(), d)

    if time_str:
        parts = time_str.split(":")
        now_time = time(int(parts[0]), int(parts[1]))
    else:
        from datetime import datetime
        now_time = datetime.now().time()

    result = current_block(plan, now_time)

    # ad-hoc 카운트 추가
    log_files = find_logs_for_date(home, d)
    ad_hoc_count = 0
    for lf in log_files:
        log = parse_log(lf.read_text(), str(lf))
        if log.event_type == EventType.AD_HOC:
            ad_hoc_count += 1
    result["today_ad_hoc_count"] = ad_hoc_count

    print_json(result)
