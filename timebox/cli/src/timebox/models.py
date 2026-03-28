from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, datetime
from enum import StrEnum
from typing import Optional


# ──────────────────────────────────────
# Enums
# ──────────────────────────────────────

class BlockType(StrEnum):
    DEEP_WORK = "deep-work"
    SHALLOW = "shallow"
    BREAK = "break"
    FLEX = "flex"
    WRAP_UP = "wrap-up"
    LUNCH = "lunch"


class CheckStatus(StrEnum):
    TODO = "todo"
    DONE = "done"
    PARTIAL = "partial"


class EventType(StrEnum):
    DEEP_WORK = "deep-work"
    INTERRUPT = "interrupt"
    SWITCH = "switch"
    AD_HOC = "ad-hoc"
    BREAK = "break"
    SHALLOW = "shallow"


class ReviewPeriod(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class GoalScope(StrEnum):
    YEARLY = "yearly"
    MONTHLY = "monthly"
    WEEKLY = "weekly"


# ──────────────────────────────────────
# Plan
# ──────────────────────────────────────

@dataclass(frozen=True)
class CheckItem:
    text: str
    status: CheckStatus
    raw_line: str


@dataclass
class Big3Item:
    number: int
    text: str
    status: CheckStatus
    estimated_blocks: Optional[float] = None
    related_goal: Optional[str] = None
    sub_items: list[CheckItem] = field(default_factory=list)
    raw_line: str = ""


@dataclass
class TimeBlock:
    start: time
    end: time
    block_type: BlockType
    focus: Optional[str] = None
    items: list[CheckItem] = field(default_factory=list)


@dataclass
class EnergyEntry:
    time: time
    level: int
    notes: str


@dataclass
class DayPlan:
    date: date
    weekday: str
    big3: list[Big3Item]
    blocks: list[TimeBlock]
    energy_log: list[EnergyEntry] = field(default_factory=list)
    notes: str = ""
    raw_content: str = ""


# ──────────────────────────────────────
# Log
# ──────────────────────────────────────

@dataclass
class WorkLog:
    timestamp: datetime
    event_type: EventType
    related_to: str
    energy: Optional[int]
    trigger: Optional[str]
    block_start: time
    block_end: time
    block_type: BlockType
    focus: str
    summary: str
    work_done: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    status: dict[str, str] = field(default_factory=dict)


# ──────────────────────────────────────
# Review
# ──────────────────────────────────────

@dataclass
class Big3Result:
    number: int
    text: str
    status: CheckStatus
    result_text: str
    estimated_blocks: Optional[float] = None
    actual_blocks: Optional[float] = None


@dataclass
class BlockAnalysis:
    start: time
    end: time
    block_type: str
    planned: str
    actual: str
    match: str


@dataclass
class DailyReview:
    date: date
    big3_results: list[Big3Result]
    success_rate: str
    estimation_accuracy: list[dict]
    block_analysis: list[BlockAnalysis]
    block_adherence: float
    energy_pattern: dict
    goal_alignment: dict
    carry_forward: dict
    one_liner: str = ""
    reflection: str = ""
    coach_notes: str = ""


# ──────────────────────────────────────
# Config
# ──────────────────────────────────────

@dataclass
class TimeboxConfig:
    home: str
    github_sync: bool = False
    google_calendar: bool = False
    notification_channel: str = "claude-code"
    checkin_interval: int = 15
    deep_work_block: int = 90
    break_duration: int = 15
    obsidian_vault: bool = False


# ──────────────────────────────────────
# Think
# ──────────────────────────────────────

@dataclass
class ThinkEntry:
    timestamp: datetime
    short_name: str
    tags: list[str] = field(default_factory=list)
    mood: str = ""
    raw_content: str = ""


# ──────────────────────────────────────
# Goals
# ──────────────────────────────────────

@dataclass
class Goal:
    id: str
    text: str
    parent: Optional[str]
    status: str
    success_criteria: Optional[str]
    scope: GoalScope


@dataclass
class GoalSet:
    scope: GoalScope
    period: str
    goals: list[Goal]


# ──────────────────────────────────────
# Stats 출력
# ──────────────────────────────────────

@dataclass
class Big3Stat:
    id: int
    name: str
    estimated_blocks: Optional[float]
    actual_blocks: float
    ratio: Optional[float]
    status: str
    progress_pct: Optional[int] = None
    related_goal: Optional[str] = None


@dataclass
class BlockStat:
    time: str
    block_type: str
    plan_focus: str
    actual_focus: str
    match: bool


@dataclass
class EnergyStat:
    entries: list[dict]
    avg: Optional[float]


@dataclass
class DailyStats:
    date: date
    big3: list[Big3Stat]
    completion: dict
    blocks: list[BlockStat]
    block_adherence: float
    energy: EnergyStat
    ad_hoc_count: int
    goal_alignment: dict


@dataclass
class CarryOverItem:
    name: str
    first_appeared: date
    streak_days: int
    times_scheduled: int
    times_dropped: int


@dataclass
class WeeklyStats:
    week: str                         # "2026-W13"
    year: int
    week_number: int
    days: list[DailyStats]
    total_big3_done: int
    total_big3_scheduled: int
    avg_block_adherence: float
    avg_energy: Optional[float]
    total_ad_hoc: int
    energy_by_day: list[dict]         # [{"date": ..., "avg": ...}, ...]
