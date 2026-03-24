"""log_writer 라운드트립 테스트."""
from datetime import date

import pytest

from tests.factories import make_log
from timebox.parsers.log_parser import parse_log
from timebox.writers.log_writer import write_log


SAMPLE_DATE = date(2026, 3, 24)


class TestWriteLog:
    def test_roundtrip_event_type(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE)
        original = parse_log(path.read_text(), str(path))
        md = write_log(original)
        reparsed = parse_log(md)
        assert reparsed.event_type == original.event_type

    def test_roundtrip_related_to(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, related_to="Big 2")
        original = parse_log(path.read_text(), str(path))
        md = write_log(original)
        reparsed = parse_log(md)
        assert reparsed.related_to == original.related_to

    def test_roundtrip_energy(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, energy=3)
        original = parse_log(path.read_text(), str(path))
        md = write_log(original)
        reparsed = parse_log(md)
        assert reparsed.energy == 3

    def test_roundtrip_block_times(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, block_start="09:00", block_end="10:30")
        original = parse_log(path.read_text(), str(path))
        md = write_log(original)
        reparsed = parse_log(md)
        assert reparsed.block_start == original.block_start
        assert reparsed.block_end == original.block_end

    def test_roundtrip_work_done(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, summary="API 구현 완료")
        original = parse_log(path.read_text(), str(path))
        md = write_log(original)
        reparsed = parse_log(md)
        assert "API 구현 완료" in reparsed.work_done

    def test_no_energy_line_when_none(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, energy=None)
        original = parse_log(path.read_text(), str(path))
        md = write_log(original)
        assert "energy" not in md or "- energy:" not in md
