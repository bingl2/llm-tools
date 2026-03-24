"""plan_writer 라운드트립 테스트."""
from datetime import date

import pytest

from tests.factories import make_plan
from timebox.parsers.plan_parser import parse_plan
from timebox.writers.plan_writer import write_plan


SAMPLE_DATE = date(2026, 3, 24)


class TestWritePlan:
    def test_roundtrip_big3(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        original = parse_plan(path.read_text(), SAMPLE_DATE)
        md = write_plan(original)
        reparsed = parse_plan(md, SAMPLE_DATE)

        assert len(reparsed.big3) == len(original.big3)
        for orig, rep in zip(original.big3, reparsed.big3):
            assert orig.number == rep.number
            assert orig.text == rep.text
            assert orig.status == rep.status
            assert orig.estimated_blocks == rep.estimated_blocks

    def test_roundtrip_blocks(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        original = parse_plan(path.read_text(), SAMPLE_DATE)
        md = write_plan(original)
        reparsed = parse_plan(md, SAMPLE_DATE)

        assert len(reparsed.blocks) == len(original.blocks)
        for orig, rep in zip(original.blocks, reparsed.blocks):
            assert orig.start == rep.start
            assert orig.end == rep.end
            assert orig.block_type == rep.block_type
            assert orig.focus == rep.focus

    def test_roundtrip_energy_log(self, timebox_home):
        path = make_plan(
            timebox_home,
            SAMPLE_DATE,
            energy_log=[("09:30", 4, "집중 좋음"), ("13:00", 3, "점심 후 처짐")],
        )
        original = parse_plan(path.read_text(), SAMPLE_DATE)
        md = write_plan(original)
        reparsed = parse_plan(md, SAMPLE_DATE)

        assert len(reparsed.energy_log) == 2
        assert reparsed.energy_log[0].level == 4
        assert reparsed.energy_log[1].notes == "점심 후 처짐"

    def test_date_in_header(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        original = parse_plan(path.read_text(), SAMPLE_DATE)
        md = write_plan(original)
        assert "2026-03-24" in md

    def test_big3_estimated_blocks_present(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        original = parse_plan(path.read_text(), SAMPLE_DATE)
        md = write_plan(original)
        assert "~2블록" in md

    def test_energy_log_table_present(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        original = parse_plan(path.read_text(), SAMPLE_DATE)
        md = write_plan(original)
        assert "## Energy Log" in md
        assert "| Time | Energy | Notes |" in md
