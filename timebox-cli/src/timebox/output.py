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
