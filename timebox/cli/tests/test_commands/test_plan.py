import json
from datetime import date

from tests.factories import make_plan, make_config


SAMPLE_DATE = date(2026, 3, 24)

SAMPLE_PLAN_JSON = {
    "date": "2026-03-24",
    "weekday": "화",
    "big3": [
        {"number": 1, "text": "API 리팩토링", "status": "todo", "estimated_blocks": 2.0, "related_goal": None},
        {"number": 2, "text": "프론트 버그", "status": "todo", "estimated_blocks": 1.0, "related_goal": None},
        {"number": 3, "text": "문서 v1", "status": "todo", "estimated_blocks": 1.0, "related_goal": None},
    ],
    "blocks": [
        {"start": "09:00", "end": "10:30", "block_type": "deep-work", "focus": "Big 3 #1"},
        {"start": "10:30", "end": "10:45", "block_type": "break", "focus": None},
        {"start": "10:45", "end": "12:00", "block_type": "deep-work", "focus": "Big 3 #2"},
        {"start": "12:00", "end": "13:00", "block_type": "lunch", "focus": None},
        {"start": "13:00", "end": "14:00", "block_type": "shallow", "focus": None},
        {"start": "14:00", "end": "15:30", "block_type": "deep-work", "focus": "Big 3 #3"},
        {"start": "15:30", "end": "15:45", "block_type": "break", "focus": None},
        {"start": "15:45", "end": "17:00", "block_type": "flex", "focus": None},
        {"start": "17:00", "end": "17:30", "block_type": "wrap-up", "focus": None},
    ],
    "energy_log": [],
    "notes": "",
}


class TestPlanShow:
    def test_shows_plan_as_json(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("plan", "show", "--date", "2026-03-24")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["date"] == "2026-03-24"
        assert len(data["big3"]) == 3

    def test_big3_fields_present(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("plan", "show", "--date", "2026-03-24")
        data = json.loads(result.output)
        big1 = data["big3"][0]
        assert "text" in big1
        assert "status" in big1
        assert "estimated_blocks" in big1
        assert "number" in big1

    def test_blocks_present(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("plan", "show", "--date", "2026-03-24")
        data = json.loads(result.output)
        assert len(data["blocks"]) == 9

    def test_empty_when_no_plan(self, cli, env_home):
        result = cli("plan", "show", "--date", "2099-01-01")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["date"] == "2099-01-01"
        assert data["big3"] == []
        assert data["blocks"] == []


class TestPlanCreate:
    def test_creates_plan_file(self, runner, env_home):
        from timebox.cli import app
        result = runner.invoke(
            app,
            ["plan", "create", "--date", "2026-03-24"],
            input=json.dumps(SAMPLE_PLAN_JSON),
        )
        assert result.exit_code == 0
        plan_path = env_home / "plans" / "2026-03-24.md"
        assert plan_path.exists()

    def test_plan_file_has_big3(self, runner, env_home):
        from timebox.cli import app
        runner.invoke(
            app,
            ["plan", "create", "--date", "2026-03-24"],
            input=json.dumps(SAMPLE_PLAN_JSON),
        )
        plan_path = env_home / "plans" / "2026-03-24.md"
        content = plan_path.read_text()
        assert "API 리팩토링" in content
        assert "## Big 3" in content

    def test_output_is_json(self, runner, env_home):
        from timebox.cli import app
        result = runner.invoke(
            app,
            ["plan", "create", "--date", "2026-03-24"],
            input=json.dumps(SAMPLE_PLAN_JSON),
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)


class TestPlanCheck:
    def test_toggles_unchecked_to_checked(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("plan", "check", "--date", "2026-03-24", "--item", "API 리팩토링")
        assert result.exit_code == 0
        plan_path = env_home / "plans" / "2026-03-24.md"
        content = plan_path.read_text()
        assert "[x]" in content

    def test_toggles_checked_to_unchecked(self, cli, env_home):
        make_plan(
            env_home,
            SAMPLE_DATE,
            big3=[("API 리팩토링", 2, "x"), ("프론트 버그 수정", 1, " "), ("문서 v1 작성", 1, " ")],
        )
        result = cli("plan", "check", "--date", "2026-03-24", "--item", "API 리팩토링")
        assert result.exit_code == 0
        plan_path = env_home / "plans" / "2026-03-24.md"
        content = plan_path.read_text()
        # After toggle, should be unchecked
        assert "[ ]" in content

    def test_output_is_json(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("plan", "check", "--date", "2026-03-24", "--item", "API 리팩토링")
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_error_when_item_not_found(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli("plan", "check", "--date", "2026-03-24", "--item", "존재하지않는항목xyz")
        assert result.exit_code == 1
        data = json.loads(result.output)
        assert "error" in data

    def test_error_when_no_plan(self, cli, env_home):
        result = cli("plan", "check", "--date", "2099-01-01", "--item", "API 리팩토링")
        assert result.exit_code == 1


class TestPlanEnergy:
    def test_adds_energy_row(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli(
            "plan", "energy",
            "--date", "2026-03-24",
            "--time", "09:30",
            "--level", "4",
            "--notes", "집중 잘 됨",
        )
        assert result.exit_code == 0
        plan_path = env_home / "plans" / "2026-03-24.md"
        content = plan_path.read_text()
        assert "09:30" in content
        assert "4/5" in content
        assert "집중 잘 됨" in content

    def test_output_is_json(self, cli, env_home):
        make_plan(env_home, SAMPLE_DATE)
        result = cli(
            "plan", "energy",
            "--date", "2026-03-24",
            "--time", "09:30",
            "--level", "4",
            "--notes", "테스트",
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_error_when_no_plan(self, cli, env_home):
        result = cli(
            "plan", "energy",
            "--date", "2099-01-01",
            "--time", "09:30",
            "--level", "4",
        )
        assert result.exit_code == 1
