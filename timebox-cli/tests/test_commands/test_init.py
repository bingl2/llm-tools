import json


class TestInit:
    def test_creates_directory_structure(self, cli, env_home):
        result = cli("init")
        assert result.exit_code == 0
        assert (env_home / "plans").is_dir()
        assert (env_home / "logs").is_dir()
        assert (env_home / "reviews").is_dir()
        assert (env_home / "goals").is_dir()

    def test_creates_config_file(self, cli, env_home):
        result = cli("init")
        assert result.exit_code == 0
        assert (env_home / "_config.md").exists()

    def test_config_has_default_values(self, cli, env_home):
        cli("init")
        content = (env_home / "_config.md").read_text()
        assert "deep_work_block: 90" in content
        assert "checkin_interval: 15" in content

    def test_idempotent(self, cli, env_home):
        cli("init")
        result = cli("init")
        assert result.exit_code == 0

    def test_outputs_json_confirmation(self, cli, env_home):
        result = cli("init")
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert "home" in data
