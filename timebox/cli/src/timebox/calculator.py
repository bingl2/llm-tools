from datetime import date, time
from typing import Optional

from timebox.models import (
    DayPlan,
    CheckStatus,
    WorkLog,
    EventType,
    TimeboxConfig,
    DailyStats,
    Big3Stat,
    BlockStat,
    EnergyStat,
    WeeklyStats,
    CarryOverItem,
)


def _minutes_between(start: time, end: time) -> int:
    """두 time 사이의 분."""
    return (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute)


def current_block(plan: DayPlan, now: time) -> dict:
    """현재 시각 기준 블록 정보 + 남은 시간 + 다음 블록."""
    current = None
    next_blk = None
    remaining = 0

    for i, block in enumerate(plan.blocks):
        if block.start <= now < block.end:
            current = block
            remaining = _minutes_between(now, block.end)
            if i + 1 < len(plan.blocks):
                next_blk = plan.blocks[i + 1]
            break

    # 현재 블록 이후: 다음 블록 찾기
    if current is None:
        for block in plan.blocks:
            if block.start > now:
                next_blk = block
                break

    # 다음 미완료 체크리스트 항목
    next_item = None
    if current:
        for item in current.items:
            if item.status == CheckStatus.TODO:
                next_item = item.text
                break

    # Big 3 진행률
    done = sum(1 for b in plan.big3 if b.status == CheckStatus.DONE)
    in_prog = sum(1 for b in plan.big3 if b.status == CheckStatus.PARTIAL)
    not_started = sum(1 for b in plan.big3 if b.status == CheckStatus.TODO)

    def _block_dict(blk):
        if blk is None:
            return None
        return {
            "time": f"{blk.start.strftime('%H:%M')}-{blk.end.strftime('%H:%M')}",
            "type": blk.block_type.value,
            "focus": blk.focus,
        }

    return {
        "current_time": now.strftime("%H:%M"),
        "current_block": _block_dict(current),
        "remaining_minutes": remaining,
        "next_block": _block_dict(next_blk),
        "next_checklist_item": next_item,
        "big3_progress": {
            "done": done,
            "in_progress": in_prog,
            "not_started": not_started,
        },
    }


def _actual_blocks(big3_index: int, logs: list[WorkLog], config: TimeboxConfig) -> float:
    """Big3 항목의 실제 블록 수: related_to 로그들의 총 분 / deep_work_block."""
    total_minutes = 0
    tag = f"Big {big3_index}"
    for log in logs:
        if log.related_to == tag:
            total_minutes += _minutes_between(log.block_start, log.block_end)
    return total_minutes / config.deep_work_block


def block_adherence(plan: DayPlan, logs: list[WorkLog]) -> list[BlockStat]:
    """플랜 블록 vs 실제 로그 비교 -> BlockStat 리스트."""
    results = []
    for block in plan.blocks:
        plan_focus = block.focus or ""
        # 이 블록 시간대에 해당하는 로그 찾기
        matching_log = None
        for log in logs:
            if log.block_start == block.start and log.block_end == block.end:
                matching_log = log
                break
        actual_focus = matching_log.related_to if matching_log else ""
        match = bool(actual_focus and plan_focus and actual_focus in plan_focus)
        results.append(BlockStat(
            time=f"{block.start.strftime('%H:%M')}-{block.end.strftime('%H:%M')}",
            block_type=block.block_type.value,
            plan_focus=plan_focus,
            actual_focus=actual_focus,
            match=match,
        ))
    return results


def estimation_accuracy(
    plan: DayPlan, logs: list[WorkLog], config: TimeboxConfig
) -> list[dict]:
    """Big3별 예상 vs 실제 블록 수 비교."""
    results = []
    for item in plan.big3:
        if item.estimated_blocks is None:
            continue
        actual = _actual_blocks(item.number, logs, config)
        ratio = actual / item.estimated_blocks if item.estimated_blocks > 0 else None
        results.append({
            "name": item.text,
            "estimated": item.estimated_blocks,
            "actual": actual,
            "ratio": ratio,
        })
    return results


def daily_stats(
    plan: DayPlan, logs: list[WorkLog], config: TimeboxConfig
) -> DailyStats:
    """플랜 + 로그 -> DailyStats."""
    # Big 3 stats
    big3_stats = []
    for item in plan.big3:
        actual = _actual_blocks(item.number, logs, config)
        ratio = (
            actual / item.estimated_blocks
            if item.estimated_blocks and item.estimated_blocks > 0
            else None
        )
        big3_stats.append(Big3Stat(
            id=item.number,
            name=item.text,
            estimated_blocks=item.estimated_blocks,
            actual_blocks=actual,
            ratio=ratio,
            status=item.status.value,
            related_goal=item.related_goal,
        ))

    # Completion
    done = sum(1 for b in plan.big3 if b.status == CheckStatus.DONE)
    in_prog = sum(1 for b in plan.big3 if b.status == CheckStatus.PARTIAL)
    not_started = sum(1 for b in plan.big3 if b.status == CheckStatus.TODO)
    completion = {"done": done, "in_progress": in_prog, "not_started": not_started}

    # Block adherence
    block_stats = block_adherence(plan, logs)
    if block_stats:
        matched = sum(1 for b in block_stats if b.match)
        adherence_pct = matched / len(block_stats) * 100
    else:
        adherence_pct = 0.0

    # Energy
    energies = [log.energy for log in logs if log.energy is not None]
    energy_entries = [{"energy": e} for e in energies]
    avg_energy: Optional[float] = sum(energies) / len(energies) if energies else None
    energy_stat = EnergyStat(entries=energy_entries, avg=avg_energy)

    # Ad-hoc count
    ad_hoc_count = sum(1 for log in logs if log.event_type == EventType.AD_HOC)

    # Goal alignment
    goal_alignment: dict = {}

    return DailyStats(
        date=plan.date,
        big3=big3_stats,
        completion=completion,
        blocks=block_stats,
        block_adherence=adherence_pct,
        energy=energy_stat,
        ad_hoc_count=ad_hoc_count,
        goal_alignment=goal_alignment,
    )


def weekly_stats(daily_stats_list: list[DailyStats], week: str) -> WeeklyStats:
    """일별 통계 리스트 -> WeeklyStats 집계."""
    # Parse year/week from "2026-W13"
    try:
        parts = week.split("-W")
        year = int(parts[0])
        week_number = int(parts[1])
    except (IndexError, ValueError):
        year = 0
        week_number = 0

    total_big3_done = sum(d.completion.get("done", 0) for d in daily_stats_list)
    total_big3_scheduled = sum(
        d.completion.get("done", 0) + d.completion.get("in_progress", 0) + d.completion.get("not_started", 0)
        for d in daily_stats_list
    )
    total_ad_hoc = sum(d.ad_hoc_count for d in daily_stats_list)

    if daily_stats_list:
        avg_block_adherence = sum(d.block_adherence for d in daily_stats_list) / len(daily_stats_list)
    else:
        avg_block_adherence = 0.0

    energies = [d.energy.avg for d in daily_stats_list if d.energy.avg is not None]
    avg_energy: Optional[float] = sum(energies) / len(energies) if energies else None

    energy_by_day = [
        {"date": d.date.isoformat(), "avg": d.energy.avg}
        for d in daily_stats_list
    ]

    return WeeklyStats(
        week=week,
        year=year,
        week_number=week_number,
        days=daily_stats_list,
        total_big3_done=total_big3_done,
        total_big3_scheduled=total_big3_scheduled,
        avg_block_adherence=avg_block_adherence,
        avg_energy=avg_energy,
        total_ad_hoc=total_ad_hoc,
        energy_by_day=energy_by_day,
    )


def carry_over_streak(reviews: list[dict]) -> list[CarryOverItem]:
    """일별 리뷰 목록 -> carry-over 항목별 연속 일수 추적.

    reviews: parse_daily_review() 결과 dict 리스트 (date 오름차순 정렬 권장).

    완료된 항목 제외 기준: 항목이 마지막으로 big3_candidates에 등장한 날짜(last_seen)가
    가장 최신 리뷰 날짜 기준 7일 초과이면 완료/드롭된 것으로 간주하고 제외한다.
    """
    if not reviews:
        return []

    # 날짜순 정렬
    sorted_reviews = sorted(reviews, key=lambda r: r["date"])

    # 항목별 첫 등장일, 마지막 등장일, 누적 일수, 연속 여부 추적
    first_seen: dict[str, date] = {}
    last_seen: dict[str, date] = {}
    scheduled_count: dict[str, int] = {}
    prev_day_items: set[str] = set()
    streak: dict[str, int] = {}

    for review in sorted_reviews:
        d = date.fromisoformat(review["date"]) if isinstance(review["date"], str) else review["date"]
        candidates: list[str] = review.get("carry_forward", {}).get("big3_candidates", [])
        current_items = set(candidates)

        for name in current_items:
            last_seen[name] = d
            if name not in first_seen:
                first_seen[name] = d
                streak[name] = 1
                scheduled_count[name] = 1
            else:
                scheduled_count[name] = scheduled_count.get(name, 0) + 1
                if name in prev_day_items:
                    streak[name] = streak.get(name, 1) + 1
                else:
                    streak[name] = 1

        prev_day_items = current_items

    # 가장 최신 리뷰 날짜
    latest_review_date = date.fromisoformat(sorted_reviews[-1]["date"]) if isinstance(sorted_reviews[-1]["date"], str) else sorted_reviews[-1]["date"]

    # Build CarryOverItem list
    # last_seen이 최신 리뷰 날짜 기준 7일 이내인 항목만 포함
    # (7일 초과면 완료되었거나 드롭된 것으로 간주)
    ACTIVE_WINDOW_DAYS = 7
    results = []
    for name, first_date in first_seen.items():
        days_since_last = (latest_review_date - last_seen[name]).days
        if days_since_last > ACTIVE_WINDOW_DAYS:
            continue
        times_sched = scheduled_count.get(name, 1)
        streak_days = streak.get(name, 1)
        # times_dropped = times appeared but not consecutively (approximation)
        times_dropped = max(0, times_sched - streak_days)
        results.append(CarryOverItem(
            name=name,
            first_appeared=first_date,
            streak_days=streak_days,
            times_scheduled=times_sched,
            times_dropped=times_dropped,
        ))

    return results


def energy_pattern(plans: list[DayPlan]) -> dict:
    """플랜 목록 -> 시간대별(morning/afternoon/evening) 에너지 집계.

    morning:   06:00-11:59
    afternoon: 12:00-17:59
    evening:   18:00-23:59
    """
    buckets: dict[str, list[int]] = {"morning": [], "afternoon": [], "evening": []}

    for plan in plans:
        for entry in plan.energy_log:
            hour = entry.time.hour
            if 6 <= hour < 12:
                buckets["morning"].append(entry.level)
            elif 12 <= hour < 18:
                buckets["afternoon"].append(entry.level)
            else:
                buckets["evening"].append(entry.level)

    result = {}
    for period, values in buckets.items():
        avg = sum(values) / len(values) if values else None
        result[period] = {"avg": avg, "count": len(values), "entries": values}

    return result
