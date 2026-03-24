from datetime import date, time

from timebox.parsers.log_parser import parse_log
from timebox.models import EventType, BlockType

from tests.factories import make_log


SAMPLE_DATE = date(2026, 3, 24)


class TestParseLog:
    def test_parses_event_type(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, event_type="deep-work")
        log = parse_log(path.read_text(), str(path))
        assert log.event_type == EventType.DEEP_WORK

    def test_parses_interrupt_type(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, event_type="interrupt")
        log = parse_log(path.read_text(), str(path))
        assert log.event_type == EventType.INTERRUPT

    def test_parses_related_to(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, related_to="Big 2")
        log = parse_log(path.read_text(), str(path))
        assert log.related_to == "Big 2"

    def test_parses_energy(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, energy=5)
        log = parse_log(path.read_text(), str(path))
        assert log.energy == 5

    def test_parses_no_energy(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, energy=None)
        log = parse_log(path.read_text(), str(path))
        assert log.energy is None

    def test_parses_block_times(self, timebox_home):
        path = make_log(
            timebox_home, SAMPLE_DATE,
            block_start="14:00", block_end="15:30",
        )
        log = parse_log(path.read_text(), str(path))
        assert log.block_start == time(14, 0)
        assert log.block_end == time(15, 30)

    def test_parses_focus(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, focus="프론트엔드 수정")
        log = parse_log(path.read_text(), str(path))
        assert log.focus == "프론트엔드 수정"

    def test_parses_work_done(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, summary="엔드포인트 정리 완료")
        log = parse_log(path.read_text(), str(path))
        assert "엔드포인트 정리 완료" in log.work_done

    def test_parses_timestamp_from_filename(self, timebox_home):
        path = make_log(timebox_home, SAMPLE_DATE, hhmm="1430")
        log = parse_log(path.read_text(), str(path))
        assert log.timestamp.hour == 14
        assert log.timestamp.minute == 30
