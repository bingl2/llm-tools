import re
from datetime import time

from timebox.models import CheckStatus

# ── 섹션 분리 ──

SECTION_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


def split_sections(content: str) -> dict[str, str]:
    """마크다운을 ## 헤더 기준으로 {헤더: 본문} dict로 분리.

    중첩 헤더(###)는 상위 섹션(##)에 포함된다.
    """
    sections: dict[str, str] = {}
    matches = list(SECTION_RE.finditer(content))

    for i, m in enumerate(matches):
        level = len(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = len(content)
        for j in range(i + 1, len(matches)):
            if len(matches[j].group(1)) <= level:
                end = matches[j].start()
                break
        sections[title] = content[start:end].strip()

    return sections


# ── 체크박스 파싱 ──

CHECK_RE = re.compile(r"^-\s+\[([ x~])\]\s+(.+)$", re.MULTILINE)


def parse_check_status(char: str) -> CheckStatus:
    """체크박스 문자 -> CheckStatus."""
    match char:
        case "x":
            return CheckStatus.DONE
        case "~":
            return CheckStatus.PARTIAL
        case _:
            return CheckStatus.TODO


def parse_checkboxes(text: str) -> list[tuple[CheckStatus, str, str]]:
    """텍스트에서 체크박스 항목들을 (status, text, raw_line)으로 반환."""
    results = []
    for m in CHECK_RE.finditer(text):
        status = parse_check_status(m.group(1))
        results.append((status, m.group(2).strip(), m.group(0)))
    return results


# ── 테이블 파싱 ──


def parse_table(text: str) -> list[dict[str, str]]:
    """마크다운 테이블 -> list of dicts.

    첫 행 = 헤더, 두번째 행 = 구분선(---|---), 나머지 = 데이터.
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip().startswith("|")]
    if len(lines) < 3:
        return []

    headers = [h.strip() for h in lines[0].split("|") if h.strip()]
    rows = []
    for line in lines[2:]:  # 구분선 스킵
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


# ── 시간 파싱 ──

TIME_RE = re.compile(r"(\d{2}):(\d{2})")


def parse_time(s: str) -> time:
    """'HH:MM' 문자열 -> time 객체."""
    m = TIME_RE.search(s)
    if not m:
        raise ValueError(f"시간 형식 오류: {s}")
    return time(int(m.group(1)), int(m.group(2)))
