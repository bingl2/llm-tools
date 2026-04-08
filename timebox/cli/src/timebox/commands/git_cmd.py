"""git commit 커맨드."""
import subprocess
from datetime import date
from typing import Optional

import typer

from timebox.output import print_json, error_json
from timebox.paths import get_home
from timebox.tz import default_today


def commit(
    push: bool = typer.Option(False, "--push", help="커밋 후 push"),
) -> None:
    """timebox 데이터 파일을 git 자동 커밋."""
    home = get_home()
    today = default_today()

    # git repo 확인
    check = subprocess.run(
        ["git", "-C", str(home), "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
    )
    if check.returncode != 0:
        error_json(f"git 저장소가 아닙니다: {home}", code="NOT_GIT_REPO")

    # 파일 스테이징
    add_result = subprocess.run(
        ["git", "-C", str(home), "add", "plans/", "logs/", "reviews/", "goals/", "_config.md"],
        capture_output=True,
        text=True,
    )
    if add_result.returncode != 0:
        error_json(f"git add 실패: {add_result.stderr}", code="GIT_ADD_FAILED")

    # 스테이징된 변경사항 확인
    status_result = subprocess.run(
        ["git", "-C", str(home), "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )
    staged_files = [f for f in status_result.stdout.strip().splitlines() if f]

    if not staged_files:
        print_json({
            "hash": None,
            "message": "nothing to commit",
            "files": [],
        })
        return

    # 커밋 메시지
    file_summary = f"{len(staged_files)} file(s)"
    commit_msg = f"timebox: {today.isoformat()} — {file_summary}"

    commit_result = subprocess.run(
        ["git", "-C", str(home), "commit", "-m", commit_msg],
        capture_output=True,
        text=True,
    )
    if commit_result.returncode != 0:
        error_json(f"git commit 실패: {commit_result.stderr}", code="GIT_COMMIT_FAILED")

    # 커밋 해시 가져오기
    hash_result = subprocess.run(
        ["git", "-C", str(home), "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
    )
    commit_hash = hash_result.stdout.strip()

    # push
    if push:
        push_result = subprocess.run(
            ["git", "-C", str(home), "push"],
            capture_output=True,
            text=True,
        )
        if push_result.returncode != 0:
            error_json(f"git push 실패: {push_result.stderr}", code="GIT_PUSH_FAILED")

    print_json({
        "hash": commit_hash,
        "message": commit_msg,
        "files": staged_files,
    })
