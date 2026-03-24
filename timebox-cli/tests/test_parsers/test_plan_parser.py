from datetime import date, time

from timebox.parsers.plan_parser import parse_plan
from timebox.models import CheckStatus, BlockType

from tests.factories import make_plan


SAMPLE_DATE = date(2026, 3, 24)  # 화요일


class TestParsePlanBig3:
    def test_parses_three_items(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert len(plan.big3) == 3

    def test_parses_text_and_status(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE, big3=[
            ("API 리팩토링", 2, "x"),
            ("프론트 버그", 1, " "),
            ("문서 v1", 1, "~"),
        ])
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert plan.big3[0].text == "API 리팩토링"
        assert plan.big3[0].status == CheckStatus.DONE
        assert plan.big3[1].status == CheckStatus.TODO
        assert plan.big3[2].status == CheckStatus.PARTIAL

    def test_parses_estimated_blocks(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert plan.big3[0].estimated_blocks == 2.0
        assert plan.big3[1].estimated_blocks == 1.0

    def test_parses_number(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert plan.big3[0].number == 1
        assert plan.big3[1].number == 2
        assert plan.big3[2].number == 3

    def test_no_estimated_blocks(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE, big3=[
            ("간단한 작업", None, " "),
        ])
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert plan.big3[0].estimated_blocks is None


class TestParsePlanBlocks:
    def test_parses_block_count(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert len(plan.blocks) == 9  # 기본 템플릿 블록 수

    def test_parses_block_times(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        first = plan.blocks[0]
        assert first.start == time(9, 0)
        assert first.end == time(10, 30)

    def test_parses_block_type(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert plan.blocks[0].block_type == BlockType.DEEP_WORK
        assert plan.blocks[1].block_type == BlockType.BREAK
        assert plan.blocks[3].block_type == BlockType.LUNCH

    def test_parses_focus(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert plan.blocks[0].focus == "Big 3 #1"
        assert plan.blocks[1].focus is None  # Break has no focus


class TestParsePlanEnergyLog:
    def test_parses_energy_entries(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE, energy_log=[
            ("09:30", 4, "집중 좋음"),
            ("14:00", 3, "보통"),
        ])
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert len(plan.energy_log) == 2
        assert plan.energy_log[0].time == time(9, 30)
        assert plan.energy_log[0].level == 4
        assert plan.energy_log[0].notes == "집중 좋음"

    def test_empty_energy_log(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert plan.energy_log == []


class TestParsePlanMetadata:
    def test_date_and_weekday(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        plan = parse_plan(path.read_text(), SAMPLE_DATE)
        assert plan.date == SAMPLE_DATE
        assert plan.weekday == "화"

    def test_raw_content_preserved(self, timebox_home):
        path = make_plan(timebox_home, SAMPLE_DATE)
        content = path.read_text()
        plan = parse_plan(content, SAMPLE_DATE)
        assert plan.raw_content == content
