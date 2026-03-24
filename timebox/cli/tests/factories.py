"""테스트용 마크다운 파일 생성 팩토리.

사용법:
    plan_path = make_plan(home, date(2026, 3, 24), big3=[
        ("API 리팩토링", 2, " "),
        ("프론트 버그", 1, " "),
    ])
"""
from pathlib import Path
from datetime import date


WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def make_config(
    home: Path,
    deep_work_block: int = 90,
    checkin_interval: int = 15,
    github_sync: bool = False,
) -> Path:
    path = home / "_config.md"
    path.write_text(f"""# Timebox Config

## 경로
- home: {home}

## 연동
- github_sync: {"on" if github_sync else "off"}
- notification_channel: claude-code
- google_calendar: off

## 운영
- checkin_interval: {checkin_interval}  (분 — 체크인 루프 주기)
- deep_work_block: {deep_work_block}  (분 — 1블록의 기준 시간)
- break_duration: 15  (분)

## 변경 이력
- {date.today().isoformat()}: 테스트용 생성
""")
    return path


def make_plan(
    home: Path,
    d: date,
    big3: list[tuple[str, float | None, str]] | None = None,
    blocks: list[tuple[str, str, str, str]] | None = None,
    energy_log: list[tuple[str, int, str]] | None = None,
) -> Path:
    """plans/{YYYY-MM-DD}.md 생성.

    big3: [(text, estimated_blocks, status_char)]
    blocks: [(start, end, type, focus)]
    energy_log: [(time, level, notes)]
    """
    weekday = WEEKDAYS[d.weekday()]

    if big3 is None:
        big3 = [
            ("API 리팩토링", 2, " "),
            ("프론트 버그 수정", 1, " "),
            ("문서 v1 작성", 1, " "),
        ]

    if blocks is None:
        blocks = [
            ("09:00", "10:30", "Deep Work", "Big 3 #1"),
            ("10:30", "10:45", "Break", ""),
            ("10:45", "12:00", "Deep Work", "Big 3 #2"),
            ("12:00", "13:00", "Lunch", ""),
            ("13:00", "14:00", "Shallow Work", ""),
            ("14:00", "15:30", "Deep Work", "Big 3 #3"),
            ("15:30", "15:45", "Break", ""),
            ("15:45", "17:00", "Flex", ""),
            ("17:00", "17:30", "Wrap-up", ""),
        ]

    lines = [f"# {d.isoformat()} ({weekday}) Timebox", ""]

    lines.append("## Big 3")
    for i, (text, est, status) in enumerate(big3, 1):
        blocks_str = f" (~{est}블록)" if est else ""
        lines.append(f"{i}. [{status}] {text}{blocks_str}")
    lines.append("")

    lines.append("## Schedule")
    lines.append("")
    for start, end, btype, focus in blocks:
        lines.append(f"### {start}-{end} | {btype}")
        if focus:
            lines.append(f"**Focus**: {focus}")
        lines.append("")

    lines.append("## Energy Log")
    lines.append("| Time | Energy | Notes |")
    lines.append("|------|--------|-------|")
    if energy_log:
        for t, level, notes in energy_log:
            lines.append(f"| {t} | {level}/5 | {notes} |")
    lines.append("")

    lines.append("## Notes")
    lines.append("")

    path = home / "plans" / f"{d.isoformat()}.md"
    path.write_text("\n".join(lines))
    return path


def make_log(
    home: Path,
    d: date,
    hhmm: str = "0930",
    event_type: str = "deep-work",
    related_to: str = "Big 1",
    energy: int | None = 4,
    block_start: str = "09:00",
    block_end: str = "10:30",
    focus: str = "API 리팩토링",
    summary: str = "엔드포인트 정리 완료",
) -> Path:
    log_dir = home / "logs" / d.isoformat()
    log_dir.mkdir(parents=True, exist_ok=True)

    energy_line = f"- energy: {energy}" if energy else ""

    content = f"""# {hhmm[:2]}:{hhmm[2:]} Timebox Log - {event_type}

## Block
{block_start}-{block_end} | {event_type}
Focus: {focus}

## Event
- type: {event_type}
- related_to: {related_to}
{energy_line}

## Work Done
- {summary}

## Status
- Big 3 #1: 진행중

## Decisions

## Notes
"""

    path = log_dir / f"{hhmm}-timebox-{event_type}.md"
    path.write_text(content)
    return path


def make_daily_review(
    home: Path,
    d: date,
    big3_results: list[tuple[str, str, str]] | None = None,
    block_adherence: int = 50,
) -> Path:
    weekday = WEEKDAYS[d.weekday()]

    if big3_results is None:
        big3_results = [
            ("x", "API 리팩토링", "완료!"),
            ("~", "프론트 버그", "70% 진행"),
            (" ", "문서 v1", "미착수"),
        ]

    lines = [f"# {d.isoformat()} ({weekday}) Timebox Review", ""]
    lines.append("## Big 3 Results")
    done_count = sum(1 for s, _, _ in big3_results if s == "x")
    for i, (status, text, result) in enumerate(big3_results, 1):
        lines.append(f"{i}. [{status}] {text} → {result}")
    lines.append("")
    lines.append(f"Success Rate: {done_count}/{len(big3_results)}")
    lines.append("")

    lines.append("## Estimation Accuracy")
    lines.append("| Big 3 | 예상 | 실제 | 배율 |")
    lines.append("|-------|------|------|------|")
    lines.append("| API 리팩토링 | 2블록 | 2블록 | 1.0x |")
    lines.append("")

    lines.append("## Block Analysis")
    lines.append("| Block | Plan | Actual | Match |")
    lines.append("|-------|------|--------|-------|")
    lines.append("| 09:00-10:30 Deep | API 리팩토링 | API 리팩토링 | O |")
    lines.append("")
    lines.append(f"Block Adherence: {block_adherence}%")
    lines.append("")

    lines.append("## Energy Pattern")
    lines.append("- Peak: 09:00-12:00")
    lines.append("- Low: 15:00-17:00")
    lines.append("")

    lines.append("## Goal Alignment")
    lines.append("- 목표 직접 기여: 2블록")
    lines.append("- 유지/운영: 1블록")
    lines.append("")

    lines.append("## Carry Forward")
    lines.append("### 내일 Big 3 후보")
    lines.append("1. 프론트 버그 수정")
    lines.append("2. 문서 v1")
    lines.append("")
    lines.append("### 오픈 루프")
    lines.append("- 디자이너 피드백 대기")
    lines.append("")

    lines.append("## Daily One-liner")
    lines.append("> 오전 집중 좋았고, 오후에 무너짐")
    lines.append("")

    lines.append("## Reflection")
    lines.append("오늘 오전에 몰입이 잘 됐다.")
    lines.append("")

    lines.append("## Coach's Notes")
    lines.append("오전 2블록 연속 몰입이 인상적입니다.")
    lines.append("> When-Then: 점심 후 에너지가 떨어지면, Shallow부터 시작한다")
    lines.append("> 질문: 오전 몰입 조건을 내일도 재현할 수 있을까?")
    lines.append("")

    path = home / "reviews" / f"{d.isoformat()}-timebox-review.md"
    path.write_text("\n".join(lines))
    return path
