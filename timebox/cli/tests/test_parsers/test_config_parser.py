from timebox.parsers.config_parser import parse_config

from tests.factories import make_config


class TestParseConfig:
    def test_parses_default_values(self, timebox_home):
        path = make_config(timebox_home)
        config = parse_config(path.read_text())
        assert config.checkin_interval == 15
        assert config.deep_work_block == 90
        assert config.break_duration == 15

    def test_parses_github_sync_on(self, timebox_home):
        path = make_config(timebox_home, github_sync=True)
        config = parse_config(path.read_text())
        assert config.github_sync is True

    def test_parses_github_sync_off(self, timebox_home):
        path = make_config(timebox_home, github_sync=False)
        config = parse_config(path.read_text())
        assert config.github_sync is False

    def test_parses_custom_block_duration(self, timebox_home):
        path = make_config(timebox_home, deep_work_block=60)
        config = parse_config(path.read_text())
        assert config.deep_work_block == 60

    def test_parses_custom_checkin_interval(self, timebox_home):
        path = make_config(timebox_home, checkin_interval=30)
        config = parse_config(path.read_text())
        assert config.checkin_interval == 30

    def test_parses_home_path(self, timebox_home):
        path = make_config(timebox_home)
        config = parse_config(path.read_text())
        assert str(timebox_home) in config.home
