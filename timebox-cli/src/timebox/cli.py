from typing import Optional

import typer

from timebox.commands import plan_cmd, now_cmd, init_cmd, log_cmd, stats_cmd, review_cmd
from timebox.commands import goals_cmd, git_cmd

app = typer.Typer(
    name="timebox",
    help="타임박싱 기반 시간 관리 CLI — LLM 코칭 시스템의 데이터 엔진",
    no_args_is_help=True,
)


@app.callback()
def main(
    home: Optional[str] = typer.Option(
        None,
        "--home",
        help="$TIMEBOX_HOME 오버라이드",
        envvar="TIMEBOX_HOME",
    ),
) -> None:
    """글로벌 옵션 처리."""
    # home은 envvar로 자동 처리됨
    pass


app.command("init")(init_cmd.init)
app.command("now")(now_cmd.now)
app.add_typer(plan_cmd.app, name="plan")
app.add_typer(log_cmd.app, name="log")
app.add_typer(stats_cmd.app, name="stats")
app.add_typer(review_cmd.app, name="review")
app.add_typer(goals_cmd.app, name="goals")
app.command("commit")(git_cmd.commit)
