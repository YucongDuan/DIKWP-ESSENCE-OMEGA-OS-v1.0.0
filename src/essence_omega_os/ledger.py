from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .utils import canonical_json, sha256_text, stable_id

GENESIS_HASH = "0" * 64


@dataclass
class HashLedger:
    """Append-only deterministic event ledger.

    Timestamps are deliberately absent from the hashed body. A run is replayable from
    the scenario, implementation version and event sequence alone.
    """

    records: list[dict[str, Any]] = field(default_factory=list)

    def append(
        self,
        kind: str,
        payload: dict[str, Any],
        *,
        stage: str,
        parents: list[str] | None = None,
    ) -> dict[str, Any]:
        previous = self.records[-1]["hash"] if self.records else GENESIS_HASH
        event_body = {
            "index": len(self.records),
            "stage": str(stage),
            "kind": str(kind),
            "parents": sorted(parents or []),
            "payload": payload,
            "prev_hash": previous,
        }
        event_body["event_id"] = stable_id("evt", event_body)
        event_body["hash"] = sha256_text(canonical_json(event_body))
        self.records.append(event_body)
        return event_body

    @property
    def head_hash(self) -> str:
        return self.records[-1]["hash"] if self.records else GENESIS_HASH

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for record in self.records:
                handle.write(canonical_json(record) + "\n")

    @staticmethod
    def verify_records(records: list[dict[str, Any]]) -> tuple[bool, list[str]]:
        errors: list[str] = []
        previous = GENESIS_HASH
        for index, record in enumerate(records):
            if record.get("index") != index:
                errors.append(f"index mismatch at {index}")
            if record.get("prev_hash") != previous:
                errors.append(f"prev_hash mismatch at {index}")
            body = dict(record)
            stored_hash = body.pop("hash", None)
            stored_event_id = body.pop("event_id", None)
            expected_event_id = stable_id("evt", body)
            if stored_event_id != expected_event_id:
                errors.append(f"event_id mismatch at {index}")
            hash_body = dict(body)
            hash_body["event_id"] = stored_event_id
            expected_hash = sha256_text(canonical_json(hash_body))
            if stored_hash != expected_hash:
                errors.append(f"hash mismatch at {index}")
            previous = stored_hash or ""
        return not errors, errors

    @classmethod
    def read_and_verify(cls, path: Path) -> tuple[bool, list[str], list[dict[str, Any]]]:
        records: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    return False, [f"invalid JSON on line {line_number}: {exc}"], records
        valid, errors = cls.verify_records(records)
        return valid, errors, records
