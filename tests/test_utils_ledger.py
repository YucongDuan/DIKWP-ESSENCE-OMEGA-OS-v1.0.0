from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from essence_omega_os.ledger import GENESIS_HASH, HashLedger
from essence_omega_os.utils import canonical_json, merkle_root, ratio, sha256_text, stable_id


class UtilsTests(unittest.TestCase):
    def test_canonical_json_orders_keys(self):
        self.assertEqual(canonical_json({"b": 2, "a": 1}), '{"a":1,"b":2}')

    def test_canonical_json_preserves_unicode(self):
        self.assertIn("本质", canonical_json({"x": "本质"}))

    def test_sha256_is_stable(self):
        self.assertEqual(sha256_text("abc"), sha256_text("abc"))

    def test_stable_id_prefix(self):
        self.assertTrue(stable_id("x", {"a": 1}).startswith("x-"))

    def test_stable_id_changes_with_payload(self):
        self.assertNotEqual(stable_id("x", {"a": 1}), stable_id("x", {"a": 2}))

    def test_ratio(self):
        self.assertEqual(ratio(1, 2), 0.5)

    def test_ratio_empty_default(self):
        self.assertEqual(ratio(0, 0), 1.0)

    def test_merkle_empty_is_hash_of_empty(self):
        self.assertEqual(merkle_root([]), sha256_text(""))

    def test_merkle_is_deterministic(self):
        items = [sha256_text("a"), sha256_text("b"), sha256_text("c")]
        self.assertEqual(merkle_root(items), merkle_root(items))


class LedgerTests(unittest.TestCase):
    def test_genesis_hash_length(self):
        self.assertEqual(len(GENESIS_HASH), 64)

    def test_append_sets_prev_hash(self):
        ledger = HashLedger()
        first = ledger.append("a", {"x": 1}, stage="s1")
        second = ledger.append("b", {"x": 2}, stage="s2")
        self.assertEqual(first["prev_hash"], GENESIS_HASH)
        self.assertEqual(second["prev_hash"], first["hash"])

    def test_verify_valid_records(self):
        ledger = HashLedger()
        ledger.append("a", {"x": 1}, stage="s1")
        ledger.append("b", {"x": 2}, stage="s2")
        valid, errors = HashLedger.verify_records(ledger.records)
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_tamper_is_detected(self):
        ledger = HashLedger()
        ledger.append("a", {"x": 1}, stage="s1")
        ledger.records[0]["payload"]["x"] = 9
        valid, errors = HashLedger.verify_records(ledger.records)
        self.assertFalse(valid)
        self.assertTrue(any("hash mismatch" in item for item in errors))

    def test_reordering_is_detected(self):
        ledger = HashLedger()
        ledger.append("a", {"x": 1}, stage="s1")
        ledger.append("b", {"x": 2}, stage="s2")
        records = list(reversed(ledger.records))
        valid, errors = HashLedger.verify_records(records)
        self.assertFalse(valid)
        self.assertTrue(errors)

    def test_write_and_read(self):
        ledger = HashLedger()
        ledger.append("a", {"x": 1}, stage="s1")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.jsonl"
            ledger.write(path)
            valid, errors, records = HashLedger.read_and_verify(path)
            self.assertTrue(valid)
            self.assertEqual(errors, [])
            self.assertEqual(len(records), 1)

    def test_invalid_json_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.jsonl"
            path.write_text("not json\n", encoding="utf-8")
            valid, errors, records = HashLedger.read_and_verify(path)
            self.assertFalse(valid)
            self.assertEqual(records, [])
            self.assertIn("invalid JSON", errors[0])


if __name__ == "__main__":
    unittest.main()
