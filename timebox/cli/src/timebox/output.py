import json
import sys
from dataclasses import asdict
from datetime import date, time, datetime
from typing import Any

import click


class TimeboxEncoder(json.JSONEncoder):
    """date, time, datetime, Enum을 JSON으로 변환."""

    def default(self, o: Any) -> Any:
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if isinstance(o, time):
            return o.strftime("%H:%M")
        if hasattr(o, "value"):  # Enum
            return o.value
        return super().default(o)


def to_dict(obj: Any) -> dict:
    """dataclass -> dict. 중첩된 dataclass도 재귀적으로 변환."""
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return obj


def to_json_str(data: Any) -> str:
    """데이터를 JSON 문자열로 변환."""
    d = to_dict(data) if hasattr(data, "__dataclass_fields__") else data
    return json.dumps(d, cls=TimeboxEncoder, ensure_ascii=False, indent=2)


def print_json(data: Any, file=None) -> None:
    """JSON을 stdout으로 출력. click.echo로 CliRunner 호환."""
    click.echo(to_json_str(data), file=file)


def error_json(message: str, code: str = "ERROR") -> None:
    """에러를 JSON으로 출력 후 exit(1)."""
    print_json({"error": message, "code": code})
    raise SystemExit(1)


def load_stdin_json() -> Any:
    """stdin에서 JSON을 파싱. zsh echo의 제어 문자 문제를 자동 보정."""
    import re

    raw = sys.stdin.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # zsh echo가 \n을 리터럴 개행으로 변환한 경우 보정:
        # JSON 문자열 값 내부의 제어 문자(개행, 탭 등)를 이스케이프 처리
        sanitized = re.sub(
            r'"(?:[^"\\]|\\.)*"',
            lambda m: m.group(0).replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t"),
            raw,
        )
        try:
            return json.loads(sanitized)
        except json.JSONDecodeError as e:
            error_json(f"JSON 파싱 오류: {e}", code="INVALID_JSON")
