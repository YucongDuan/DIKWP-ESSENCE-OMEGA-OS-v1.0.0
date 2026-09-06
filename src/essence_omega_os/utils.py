from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


def canonical_json(value: Any) -> str:
    """Return deterministic UTF-8 JSON used by every hash and stable identifier."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_id(prefix: str, payload: Any, length: int = 20) -> str:
    return f"{prefix}-{sha256_text(canonical_json(payload))[:length]}"


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def merkle_root(hex_hashes: Iterable[str]) -> str:
    layer = [item.lower() for item in hex_hashes]
    if not layer:
        return sha256_text("")
    while len(layer) > 1:
        if len(layer) % 2:
            layer.append(layer[-1])
        layer = [
            hashlib.sha256(bytes.fromhex(layer[i]) + bytes.fromhex(layer[i + 1])).hexdigest()
            for i in range(0, len(layer), 2)
        ]
    return layer[0]


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def ratio(numerator: int | float, denominator: int | float, *, empty: float = 1.0) -> float:
    if denominator == 0:
        return float(empty)
    return float(numerator) / float(denominator)


def deep_get(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    cursor: Any = mapping
    for key in keys:
        if not isinstance(cursor, dict) or key not in cursor:
            return default
        cursor = cursor[key]
    return cursor


def sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted({str(value) for value in values})
