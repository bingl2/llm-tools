import re

from timebox.models import TimeboxConfig

# 매칭: "- checkin_interval: 15  (분 — 체크인 루프 주기)"
CONFIG_KV_RE = re.compile(
    r"^-\s+(\w+):\s+(.+?)(?:\s+\(.*\))?$",
    re.MULTILINE,
)


def parse_config(content: str) -> TimeboxConfig:
    """_config.md -> TimeboxConfig."""
    kv: dict[str, str] = {}
    for m in CONFIG_KV_RE.finditer(content):
        kv[m.group(1)] = m.group(2).strip()

    return TimeboxConfig(
        home=kv.get("home", "~/timebox"),
        github_sync=kv.get("github_sync", "off").lower() == "on",
        google_calendar=kv.get("google_calendar", "off").lower() == "on",
        notification_channel=kv.get("notification_channel", "claude-code"),
        checkin_interval=int(kv.get("checkin_interval", "15")),
        deep_work_block=int(kv.get("deep_work_block", "90")),
        break_duration=int(kv.get("break_duration", "15")),
    )
