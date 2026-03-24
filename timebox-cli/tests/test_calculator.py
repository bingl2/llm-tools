"""calculator Phase 2+3 테스트: daily_stats, block_adherence, estimation_accuracy, weekly_stats, carry_over_streak, energy_pattern."""
from datetime import date, time, datetime

import pytest

from timebox.models import (
    DayPlan, Big3Item, TimeBlock, EnergyEntry,
    WorkLog, EventType, BlockType, CheckStatus,
    TimeboxConfig, DailyStats, EnergyStat, BlockStat, Big3Stat,
    CarryOverItem, WeeklyStats,
)
from timebox.calculator import (
    daily_stats, block_adherence, estimation_accuracy,
    weekly_stats, carry_over_streak, energy_pattern,
)


SAMPLE_DATE = date(2026, 3, 24)
DEFAULT_CONFIG = TimeboxConfig(
    home="~/timebox",
    deep_work_block=90,
    checkin_interval=15,
    break_duration=15,
)


def make_plan(
    big3_statuses=None,
    blocks=None,
    energy_log=None,
):
    if big3_statuses is None:
        big3_statuses = [CheckStatus.DONE, CheckStatus.PARTIAL, CheckStatus.TODO]
    big3 = [
        Big3Item(number=i+1, text=f"Task {i+1}", status=s, estimated_blocks=2.0, raw_line="")
        for i, s in enumerate(big3_statuses)
    ]
    if blocks is None:
        blocks = [
            TimeBlock(start=time(9, 0), end=time(10, 30), block_type=BlockType.DEEP_WORK, focus="Task 1"),
            TimeBlock(start=time(10, 30), end=time(10, 45), block_type=BlockType.BREAK, focus=None),
            TimeBlock(start=time(10, 45), end=time(12, 0), block_type=BlockType.DEEP_WORK, focus="Task 2"),
        ]
    return DayPlan(
        date=SAMPLE_DATE,
        weekday="화",
        big3=big3,
        blocks=blocks,
        energy_log=energy_log or [],
    )


def make_log(
    related_to="Big 1",
    event_type=EventType.DEEP_WORK,
    energy=4,
    block_start=time(9, 0),
    block_end=time(10, 30),
):
    return WorkLog(
        timestamp=datetime(2026, 3, 24, 9, 30),
        event_type=event_type,
        related_to=related_to,
        energy=energy,
        trigger=None,
        block_start=block_start,
        block_end=block_end,
        block_type=BlockType.DEEP_WORK,
        focus="Task 1",
        summary="작업 완료",
    )


class TestBlockAdherence:
    def test_all_match(self):
        plan = make_plan()
        logs = [
            make_log(related_to="Big 1", block_start=time(9, 0), block_end=time(10, 30)),
            make_log(related_to="Big 2", block_start=time(10, 45), block_end=time(12, 0)),
        ]
        result = block_adherence(plan, logs)
        assert len(result) == len(plan.blocks)

    def test_returns_block_stat_list(self):
        plan = make_plan()
        logs = [make_log()]
        result = block_adherence(plan, logs)
        from timebox.models import BlockStat
        assert all(isinstance(b, BlockStat) for b in result)

    def test_block_stat_fields(self):
        plan = make_plan()
        logs = [make_log(block_start=time(9, 0), block_end=time(10, 30))]
        result = block_adherence(plan, logs)
        b = result[0]
        assert hasattr(b, "time")
        assert hasattr(b, "block_type")
        assert hasattr(b, "plan_focus")
        assert hasattr(b, "actual_focus")
        assert hasattr(b, "match")

    def test_match_when_focus_matches(self):
        plan = make_plan(
            blocks=[
                TimeBlock(start=time(9, 0), end=time(10, 30), block_type=BlockType.DEEP_WORK, focus="Task 1"),
            ]
        )
        logs = [make_log(related_to="Big 1", block_start=time(9, 0), block_end=time(10, 30))]
        result = block_adherence(plan, logs)
        # focus가 있는 블록에 로그가 있으면 actual_focus가 채워짐
        assert result[0].actual_focus != ""


class TestEstimationAccuracy:
    def test_returns_list(self):
        plan = make_plan()
        logs = [make_log()]
        result = estimation_accuracy(plan, logs, DEFAULT_CONFIG)
        assert isinstance(result, list)

    def test_each_item_has_fields(self):
        plan = make_plan()
        logs = [make_log()]
        result = estimation_accuracy(plan, logs, DEFAULT_CONFIG)
        if result:
            item = result[0]
            assert "name" in item
            assert "estimated" in item
            assert "actual" in item
            assert "ratio" in item

    def test_only_items_with_estimated_blocks(self):
        plan = make_plan()
        # Big3 items all have estimated_blocks=2.0
        result = estimation_accuracy(plan, [], DEFAULT_CONFIG)
        assert len(result) == 3


class TestDailyStats:
    def test_returns_daily_stats_object(self):
        plan = make_plan()
        logs = [make_log()]
        result = daily_stats(plan, logs, DEFAULT_CONFIG)
        from timebox.models import DailyStats
        assert isinstance(result, DailyStats)

    def test_date_matches(self):
        plan = make_plan()
        result = daily_stats(plan, [], DEFAULT_CONFIG)
        assert result.date == SAMPLE_DATE

    def test_big3_stat_count(self):
        plan = make_plan()
        result = daily_stats(plan, [], DEFAULT_CONFIG)
        assert len(result.big3) == 3

    def test_completion_dict(self):
        plan = make_plan(big3_statuses=[CheckStatus.DONE, CheckStatus.PARTIAL, CheckStatus.TODO])
        result = daily_stats(plan, [], DEFAULT_CONFIG)
        assert result.completion["done"] == 1
        assert result.completion["in_progress"] == 1
        assert result.completion["not_started"] == 1

    def test_ad_hoc_count(self):
        plan = make_plan()
        logs = [
            make_log(event_type=EventType.AD_HOC),
            make_log(event_type=EventType.AD_HOC),
            make_log(event_type=EventType.DEEP_WORK),
        ]
        result = daily_stats(plan, logs, DEFAULT_CONFIG)
        assert result.ad_hoc_count == 2

    def test_energy_avg_none_when_no_logs(self):
        plan = make_plan()
        result = daily_stats(plan, [], DEFAULT_CONFIG)
        assert result.energy.avg is None

    def test_energy_avg_calculated(self):
        plan = make_plan()
        logs = [make_log(energy=4), make_log(energy=2)]
        result = daily_stats(plan, logs, DEFAULT_CONFIG)
        assert result.energy.avg == 3.0

    def test_block_adherence_float(self):
        plan = make_plan()
        result = daily_stats(plan, [], DEFAULT_CONFIG)
        assert isinstance(result.block_adherence, float)

    def test_goal_alignment_dict(self):
        plan = make_plan()
        result = daily_stats(plan, [], DEFAULT_CONFIG)
        assert isinstance(result.goal_alignment, dict)


def _make_daily_stats(d: date, done: int = 1, total: int = 3, adherence: float = 50.0, avg_energy: float | None = 3.0) -> DailyStats:
    big3 = [
        Big3Stat(id=i+1, name=f"Task {i+1}", estimated_blocks=2.0, actual_blocks=1.0,
                 ratio=0.5, status="done" if i < done else "todo")
        for i in range(total)
    ]
    energy = EnergyStat(entries=[{"energy": 3}] if avg_energy else [], avg=avg_energy)
    return DailyStats(
        date=d,
        big3=big3,
        completion={"done": done, "in_progress": 0, "not_started": total - done},
        blocks=[],
        block_adherence=adherence,
        energy=energy,
        ad_hoc_count=0,
        goal_alignment={},
    )


class TestWeeklyStats:
    def test_returns_weekly_stats_object(self):
        days = [_make_daily_stats(date(2026, 3, 23 + i)) for i in range(3)]
        result = weekly_stats(days, "2026-W13")
        assert isinstance(result, WeeklyStats)

    def test_week_field(self):
        days = [_make_daily_stats(date(2026, 3, 23))]
        result = weekly_stats(days, "2026-W13")
        assert result.week == "2026-W13"

    def test_total_big3_done(self):
        days = [
            _make_daily_stats(date(2026, 3, 23), done=2, total=3),
            _make_daily_stats(date(2026, 3, 24), done=1, total=3),
        ]
        result = weekly_stats(days, "2026-W13")
        assert result.total_big3_done == 3

    def test_total_big3_scheduled(self):
        days = [
            _make_daily_stats(date(2026, 3, 23), done=1, total=3),
            _make_daily_stats(date(2026, 3, 24), done=1, total=3),
        ]
        result = weekly_stats(days, "2026-W13")
        assert result.total_big3_scheduled == 6

    def test_avg_block_adherence(self):
        days = [
            _make_daily_stats(date(2026, 3, 23), adherence=60.0),
            _make_daily_stats(date(2026, 3, 24), adherence=40.0),
        ]
        result = weekly_stats(days, "2026-W13")
        assert result.avg_block_adherence == 50.0

    def test_avg_energy_none_when_no_days(self):
        result = weekly_stats([], "2026-W13")
        assert result.avg_energy is None

    def test_avg_energy_calculated(self):
        days = [
            _make_daily_stats(date(2026, 3, 23), avg_energy=4.0),
            _make_daily_stats(date(2026, 3, 24), avg_energy=2.0),
        ]
        result = weekly_stats(days, "2026-W13")
        assert result.avg_energy == 3.0

    def test_empty_days(self):
        result = weekly_stats([], "2026-W13")
        assert result.total_big3_done == 0
        assert result.total_ad_hoc == 0
        assert result.avg_block_adherence == 0.0


class TestCarryOverStreak:
    def _make_review(self, d: date, candidates: list[str]) -> dict:
        return {
            "date": d.isoformat(),
            "carry_forward": {"big3_candidates": candidates, "open_loops": []},
        }

    def test_returns_list(self):
        reviews = [self._make_review(date(2026, 3, 24), ["API 리팩토링"])]
        result = carry_over_streak(reviews)
        assert isinstance(result, list)

    def test_single_item_streak_1(self):
        reviews = [
            self._make_review(date(2026, 3, 23), ["API 리팩토링"]),
            self._make_review(date(2026, 3, 24), ["API 리팩토링"]),
        ]
        result = carry_over_streak(reviews)
        item = next(r for r in result if r.name == "API 리팩토링")
        assert item.streak_days >= 1

    def test_times_scheduled_counts(self):
        reviews = [
            self._make_review(date(2026, 3, 22), ["문서 작성"]),
            self._make_review(date(2026, 3, 23), ["문서 작성"]),
            self._make_review(date(2026, 3, 24), ["문서 작성"]),
        ]
        result = carry_over_streak(reviews)
        item = next(r for r in result if r.name == "문서 작성")
        assert item.times_scheduled == 3

    def test_item_not_in_reviews_has_no_streak(self):
        reviews = [
            self._make_review(date(2026, 3, 22), ["A"]),
            self._make_review(date(2026, 3, 23), ["B"]),
        ]
        result = carry_over_streak(reviews)
        # A appears only once, B appears only once
        for item in result:
            assert item.streak_days >= 1

    def test_first_appeared_date(self):
        reviews = [
            self._make_review(date(2026, 3, 22), ["항목"]),
            self._make_review(date(2026, 3, 24), ["항목"]),
        ]
        result = carry_over_streak(reviews)
        item = next(r for r in result if r.name == "항목")
        assert item.first_appeared == date(2026, 3, 22)

    def test_empty_reviews(self):
        result = carry_over_streak([])
        assert result == []

    def test_returns_carry_over_items(self):
        reviews = [self._make_review(date(2026, 3, 24), ["테스트"])]
        result = carry_over_streak(reviews)
        assert all(isinstance(r, CarryOverItem) for r in result)


class TestEnergyPattern:
    def _make_plan_with_energy(self, d: date, entries: list[tuple]) -> DayPlan:
        """entries: [(time_str, level, notes), ...]"""
        energy_log = [
            EnergyEntry(time=time(int(t.split(":")[0]), int(t.split(":")[1])), level=lvl, notes=n)
            for t, lvl, n in entries
        ]
        return DayPlan(
            date=d, weekday="월", big3=[], blocks=[], energy_log=energy_log,
        )

    def test_returns_dict(self):
        plans = [self._make_plan_with_energy(date(2026, 3, 24), [("09:30", 4, "좋음")])]
        result = energy_pattern(plans)
        assert isinstance(result, dict)

    def test_morning_key(self):
        plans = [self._make_plan_with_energy(date(2026, 3, 24), [("09:30", 4, "좋음")])]
        result = energy_pattern(plans)
        assert "morning" in result

    def test_afternoon_key(self):
        plans = [self._make_plan_with_energy(date(2026, 3, 24), [("14:00", 3, "보통")])]
        result = energy_pattern(plans)
        assert "afternoon" in result

    def test_evening_key(self):
        plans = [self._make_plan_with_energy(date(2026, 3, 24), [("19:00", 2, "피곤")])]
        result = energy_pattern(plans)
        assert "evening" in result

    def test_morning_avg_calculation(self):
        plans = [
            self._make_plan_with_energy(date(2026, 3, 23), [("08:00", 4, "")]),
            self._make_plan_with_energy(date(2026, 3, 24), [("10:00", 2, "")]),
        ]
        result = energy_pattern(plans)
        assert result["morning"]["avg"] == 3.0

    def test_empty_plans(self):
        result = energy_pattern([])
        assert isinstance(result, dict)
