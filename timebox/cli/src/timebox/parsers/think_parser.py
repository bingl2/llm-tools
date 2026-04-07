"""think 파일 파서 — YAML frontmatter + 마크다운 본문."""
import re
from datetime import datetime

from timebox.models import ThinkEntry
from timebox.tz import default_now

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TAG_RE = re.compile(r"tags:\s*\[([^\]]*)\]")
MOOD_RE = re.compile(r"mood:\s*(.+)$", re.MULTILINE)
DATE_RE = re.compile(r"date:\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})")
FILENAME_RE = re.compile(r"(\d{8})-(\d{4})-(.+)\.md$")


def parse_think(content: str, filepath: str = "") -> ThinkEntry:
    """thinks/{YYYY-MM-DD}/{YYYYMMDD}-{HHMM}-{name}.md -> ThinkEntry."""
    # Parse frontmatter
    tags: list[str] = []
    mood = ""
    timestamp = default_now()

    fm = FRONTMATTER_RE.match(content)
    if fm:
        fm_text = fm.group(1)

        m = DATE_RE.search(fm_text)
        if m:
            timestamp = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M")

        m = TAG_RE.search(fm_text)
        if m:
            tags = [t.strip().strip("\"'") for t in m.group(1).split(",") if t.strip()]

        m = MOOD_RE.search(fm_text)
        if m:
            mood = m.group(1).strip()

    # Parse short_name from filepath
    short_name = ""
    if filepath:
        m = FILENAME_RE.search(filepath)
        if m:
            short_name = m.group(3)

    return ThinkEntry(
        timestamp=timestamp,
        short_name=short_name,
        tags=tags,
        mood=mood,
        raw_content=content,
    )
