from datetime import date

from timebox.models import TimeboxConfig


def write_config(config: TimeboxConfig) -> str:
    """TimeboxConfig -> 마크다운 문자열."""
    return f"""# Timebox Config

## 경로
- home: {config.home}

## 연동
- github_sync: {"on" if config.github_sync else "off"}
- notification_channel: {config.notification_channel}
- google_calendar: {"on" if config.google_calendar else "off"}
- obsidian_vault: {"on" if config.obsidian_vault else "off"}

## 운영
- checkin_interval: {config.checkin_interval}  (분 — 체크인 루프 주기)
- deep_work_block: {config.deep_work_block}  (분 — 1블록의 기준 시간)
- break_duration: {config.break_duration}  (분)

## 변경 이력
- {date.today().isoformat()}: 초기 설정 생성
"""
