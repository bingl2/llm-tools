from datetime import time

import pytest

from timebox.parsers.common import (
    split_sections,
    parse_checkboxes,
    parse_table,
    parse_time,
    parse_check_status,
)
from timebox.models import CheckStatus


class TestSplitSections:
    def test_splits_by_h2_headers(self):
        content = """# Title

## Big 3
1. [ ] API 리팩토링

## Schedule
### 09:00-10:30 | Deep Work

## Notes
nothing
"""
        sections = split_sections(content)
        assert "Big 3" in sections
        assert "Schedule" in sections
        assert "Notes" in sections
        assert "API 리팩토링" in sections["Big 3"]

    def test_nested_h3_included_in_parent_h2(self):
        content = """## Schedule

### 09:00-10:30 | Deep Work
**Focus**: Big 3 #1

### 10:30-10:45 | Break

## Notes
end
"""
        sections = split_sections(content)
        assert "09:00-10:30" in sections["Schedule"]
        assert "10:30-10:45" in sections["Schedule"]
        assert "end" in sections["Notes"]

    def test_empty_content_returns_empty_dict(self):
        assert split_sections("") == {}

    def test_no_headers_returns_empty_dict(self):
        assert split_sections("just plain text\nno headers") == {}


class TestParseCheckStatus:
    def test_space_is_todo(self):
        assert parse_check_status(" ") == CheckStatus.TODO

    def test_x_is_done(self):
        assert parse_check_status("x") == CheckStatus.DONE

    def test_tilde_is_partial(self):
        assert parse_check_status("~") == CheckStatus.PARTIAL

    def test_unknown_defaults_to_todo(self):
        assert parse_check_status("?") == CheckStatus.TODO


class TestParseCheckboxes:
    def test_parses_todo_items(self):
        text = "- [ ] 첫 번째\n- [x] 두 번째\n- [~] 세 번째"
        result = parse_checkboxes(text)
        assert len(result) == 3
        assert result[0] == (CheckStatus.TODO, "첫 번째", "- [ ] 첫 번째")
        assert result[1] == (CheckStatus.DONE, "두 번째", "- [x] 두 번째")
        assert result[2] == (CheckStatus.PARTIAL, "세 번째", "- [~] 세 번째")

    def test_empty_text_returns_empty_list(self):
        assert parse_checkboxes("") == []

    def test_ignores_non_checkbox_lines(self):
        text = "some text\n- [ ] real item\n- not a checkbox"
        result = parse_checkboxes(text)
        assert len(result) == 1
        assert result[0][1] == "real item"


class TestParseTable:
    def test_parses_standard_table(self):
        text = """| Time | Energy | Notes |
|------|--------|-------|
| 09:30 | 4/5 | 집중 좋음 |
| 14:00 | 3/5 | 보통 |"""
        rows = parse_table(text)
        assert len(rows) == 2
        assert rows[0]["Time"] == "09:30"
        assert rows[0]["Energy"] == "4/5"
        assert rows[1]["Notes"] == "보통"

    def test_empty_table_returns_empty_list(self):
        assert parse_table("") == []

    def test_header_only_returns_empty_list(self):
        text = "| A | B |\n|---|---|"
        assert parse_table(text) == []


class TestParseTime:
    def test_parses_hhmm(self):
        assert parse_time("09:30") == time(9, 30)
        assert parse_time("17:00") == time(17, 0)

    def test_extracts_time_from_longer_string(self):
        assert parse_time("Block 09:30-10:00") == time(9, 30)

    def test_raises_on_invalid_format(self):
        with pytest.raises(ValueError, match="시간 형식 오류"):
            parse_time("invalid")
