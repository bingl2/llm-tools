"""goals_parser: 목표 마크다운 파일 -> GoalSet."""
import re

from timebox.models import Goal, GoalSet, GoalScope
from timebox.parsers.common import split_sections

# "- [W1] 코드 리뷰 완료" or "- [Y1] 사이드 프로젝트" (scope prefix + number)
GOAL_RE = re.compile(
    r"^-\s+\[([A-Za-z]\d+)\]\s+(.+?)(?:\s+\((.+)\))?\s*$",
    re.MULTILINE,
)

SCOPE_PREFIX_MAP = {
    "Y": GoalScope.YEARLY,
    "M": GoalScope.MONTHLY,
    "W": GoalScope.WEEKLY,
}


def _infer_scope(goal_id: str, default: GoalScope) -> GoalScope:
    prefix = goal_id[0].upper() if goal_id else ""
    return SCOPE_PREFIX_MAP.get(prefix, default)


def parse_goals(content: str, scope: GoalScope, period: str) -> GoalSet:
    """목표 마크다운 -> GoalSet."""
    sections = split_sections(content)
    goals_section = sections.get("Goals", content)

    goals: list[Goal] = []
    for m in GOAL_RE.finditer(goals_section):
        goal_id = m.group(1)
        text = m.group(2).strip()
        success_criteria = m.group(3).strip() if m.group(3) else None
        inferred_scope = _infer_scope(goal_id, scope)
        goals.append(Goal(
            id=goal_id,
            text=text,
            parent=None,
            status="active",
            success_criteria=success_criteria,
            scope=inferred_scope,
        ))

    return GoalSet(scope=scope, period=period, goals=goals)
