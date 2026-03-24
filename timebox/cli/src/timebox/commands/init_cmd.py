from timebox.paths import get_home, ensure_dirs, config_path
from timebox.models import TimeboxConfig
from timebox.writers.config_writer import write_config
from timebox.output import print_json


def init(home_override: str | None = None) -> None:
    """디렉토리 구조 + _config.md 생성."""
    home = get_home(home_override)
    ensure_dirs(home)

    cfg_path = config_path(home)
    if not cfg_path.exists():
        config = TimeboxConfig(home=str(home))
        cfg_path.write_text(write_config(config))

    print_json({"status": "ok", "home": str(home)})
