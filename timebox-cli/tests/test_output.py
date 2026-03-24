import json
from datetime import date, time
from io import StringIO

from timebox.output import print_json, to_dict, error_json, TimeboxEncoder
from timebox.models import Big3Stat, EnergyStat


class TestTimeboxEncoder:
    def test_encodes_date(self):
        result = json.dumps({"d": date(2026, 3, 24)}, cls=TimeboxEncoder)
        assert '"2026-03-24"' in result

    def test_encodes_time(self):
        result = json.dumps({"t": time(9, 30)}, cls=TimeboxEncoder)
        assert '"09:30"' in result

    def test_encodes_enum(self):
        from timebox.models import BlockType
        result = json.dumps({"bt": BlockType.DEEP_WORK}, cls=TimeboxEncoder)
        assert '"deep-work"' in result


class TestToDict:
    def test_converts_dataclass(self):
        stat = Big3Stat(
            id=1, name="API", estimated_blocks=2.0,
            actual_blocks=3.0, ratio=1.5, status="done",
        )
        d = to_dict(stat)
        assert d["name"] == "API"
        assert d["ratio"] == 1.5

    def test_passthrough_for_non_dataclass(self):
        raw = {"key": "value"}
        assert to_dict(raw) == raw


class TestPrintJson:
    def test_outputs_valid_json(self):
        buf = StringIO()
        print_json({"hello": "world", "n": 42}, file=buf)
        parsed = json.loads(buf.getvalue())
        assert parsed["hello"] == "world"

    def test_outputs_dataclass_as_json(self):
        buf = StringIO()
        stat = EnergyStat(entries=[], avg=3.5)
        print_json(stat, file=buf)
        parsed = json.loads(buf.getvalue())
        assert parsed["avg"] == 3.5

    def test_korean_not_escaped(self):
        buf = StringIO()
        print_json({"name": "API 리팩토링"}, file=buf)
        assert "리팩토링" in buf.getvalue()


class TestErrorJson:
    def test_raises_system_exit(self):
        import pytest
        with pytest.raises(SystemExit):
            error_json("something broke")
