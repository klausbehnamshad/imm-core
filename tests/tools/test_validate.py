"""Unit tests for tools/validate.py: one positive counterpart per rule.

Only synthetic records; no network. Run from the repository root with
``python -m unittest discover -s tests/tools``.
"""

import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent.parent
sys.path.insert(0, str(ROOT))

from tools.validate import (  # noqa: E402
    check_rules,
    check_schema,
    load_collection,
    load_schema,
    validate_file,
)
from jsonschema import Draft7Validator, FormatChecker  # noqa: E402


def base_record(**overrides):
    record = {
        "record_id": "2025-01-01_OHX_0001",
        "interview_date": "2025-01-01",
        "interviewer": "A. B.",
        "title": "Interview on work",
        "consent_status": "public",
        "accessRights": "open",
        "language": "eng",
    }
    record.update(overrides)
    return record


COLLECTION = {
    "record_id_pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}_OHX_[0-9]{4}$",
    "consent_values": ["research-only", "teaching", "public", "embargoed"],
}


class RuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_schema(ROOT / "schema" / "core.schema.json")
        cls.validator = Draft7Validator(cls.schema, format_checker=FormatChecker())

    def assert_rules(self, record, want_errors, want_warnings=None, collection=None):
        self.assertEqual(check_schema(record, self.validator), [])
        errors, warnings = check_rules(record, self.schema, collection)
        self.assertEqual({r for r, _p in errors}, set(want_errors))
        self.assertEqual({r for r, _p in warnings}, set(want_warnings or ()))

    def test_r1_rejects_trailing_newline(self):
        self.assert_rules(base_record(language="deu\n"), ["R1"])

    def test_r1_accepts_clean_codes(self):
        rec = base_record(language="deu", languages=["deu", "ltz"])
        rec["timecoded_segments"] = [
            {"start": "00:00:00", "end": "00:59:59", "label": "All"}
        ]
        self.assert_rules(rec, [])

    def test_r2_requires_language_in_languages(self):
        self.assert_rules(base_record(language="eng", languages=["deu"]), ["R2"])

    def test_r2_accepts_containment(self):
        self.assert_rules(base_record(language="deu", languages=["ltz", "deu"]), [])

    def test_r2_absent_languages_is_valid(self):
        self.assert_rules(base_record(), [])

    def test_r3_rejects_serialized_list(self):
        self.assert_rules(base_record(keywords=["['a', 'b']"]), ["R3"])

    def test_r3_rejects_serialized_list_with_whitespace(self):
        self.assert_rules(base_record(keywords=["  ['one', 'two']  "]), ["R3"])
        self.assert_rules(base_record(title="  ['one', 'two']"), ["R3"])

    def test_r3_warns_on_bare_prefix(self):
        self.assert_rules(base_record(keywords=["['draft"]), [], ["R3"])

    def test_r3_plain_bracket_text_is_valid(self):
        self.assert_rules(base_record(title="[Draft] interview notes"), [])

    def test_r4_rejects_end_before_start(self):
        rec = base_record(
            timecoded_segments=[{"start": "00:05:00", "end": "00:03:00", "label": "X"}]
        )
        self.assert_rules(rec, ["R4"])

    def test_r4_rejects_backward_start(self):
        rec = base_record(
            timecoded_segments=[
                {"start": "00:03:00", "end": "00:08:00", "label": "A"},
                {"start": "00:00:00", "end": "00:02:00", "label": "B"},
            ]
        )
        self.assert_rules(rec, ["R4"])

    def test_r4_accepts_overlap_and_equal_starts(self):
        rec = base_record(
            timecoded_segments=[
                {"start": "00:00:00", "end": "00:05:00", "label": "A"},
                {"start": "00:00:00", "end": "00:08:00", "label": "B"},
            ]
        )
        self.assert_rules(rec, [])

    def test_r5_comma_is_warning_only(self):
        self.assert_rules(base_record(interviewer="Smith, John"), [], ["R5"])

    def test_r5_semicolon_list_is_clean(self):
        self.assert_rules(base_record(interviewer="Smith, Jane; Doe, John"), [], ["R5"])
        self.assert_rules(base_record(interviewer="Jane Smith; John Doe"), [])

    def test_r6_rejects_unknown_consent(self):
        rec = base_record(consent_status="internal-only")
        self.assert_rules(rec, ["R6"], collection=COLLECTION)

    def test_r6_accepts_withdrawn(self):
        rec = base_record(consent_status="withdrawn", accessRights="closed")
        self.assert_rules(rec, [], collection=COLLECTION)

    def test_r6_accepts_listed_consent(self):
        self.assert_rules(base_record(), [], collection=COLLECTION)

    def test_r7_rejects_foreign_pattern(self):
        rec = base_record(record_id="WALZ-0003")
        self.assert_rules(rec, ["R7"], collection=COLLECTION)

    def test_r7_accepts_collection_pattern(self):
        self.assert_rules(base_record(), [], collection=COLLECTION)

    def test_r8_rejects_blank_text(self):
        self.assert_rules(base_record(title="   "), ["R8"])
        self.assert_rules(base_record(keywords=["  "]), ["R8"])
        rec = base_record(
            timecoded_segments=[{"start": "00:00:00", "end": "00:01:00", "label": "  "}]
        )
        self.assert_rules(rec, ["R8"])

    def test_output_names_only_file_rule_path(self):
        errors, warnings, tool_error = validate_file(
            str(TESTS_DIR.parent / "invalid-rules" / "blank-title.json"),
            self.validator,
            self.schema,
            COLLECTION,
        )
        self.assertIsNone(tool_error)
        self.assertEqual(errors, [("R8", "title")])
        self.assertEqual(warnings, [])
        for _rule, path in errors + warnings:
            self.assertNotIn("   ", path)

    def test_collection_loading(self):
        with self.assertRaises(ValueError):
            load_collection(str(TESTS_DIR / "does-not-exist.toml"))

    def test_collection_integer_pattern_is_value_error(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coll-int-pattern.toml"
            path.write_text(
                '[collection]\nrecord_id_pattern = 42\n'
                'consent_values = ["public"]\n',
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_collection(str(path))

    def test_missing_file_is_tool_error(self):
        _errors, _warnings, tool_error = validate_file(
            str(TESTS_DIR / "does-not-exist.json"), self.validator, self.schema
        )
        self.assertEqual(tool_error, "unreadable")

    def test_cli_diagnosis_masks_control_chars_in_file_name(self):
        import json
        import subprocess
        import sys
        import tempfile

        record = base_record(title="   ")
        with tempfile.TemporaryDirectory() as tmp:
            normal = Path(tmp) / "blank.json"
            normal.write_text(json.dumps(record), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "validate.py"), str(normal)],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(proc.stderr, "")
            lines = proc.stdout.splitlines()
            self.assertEqual(len(lines), 1)
            self.assertIn("R8", lines[0])
            self.assertIn("title", lines[0])

            tricky = Path(tmp) / "lf\nname.json"
            tricky.write_text(json.dumps(record), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "validate.py"), str(tricky)],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(proc.stderr, "")
            lines = proc.stdout.splitlines()
            self.assertEqual(len(lines), 1, proc.stdout)
            self.assertIn("R8", lines[0])
            self.assertIn("title", lines[0])
            self.assertIn("lf?name.json", lines[0])

    def test_cli_schema_read_errors_are_exit_2(self):
        import io
        import json
        import tempfile
        from contextlib import redirect_stdout
        from unittest import mock

        import tools.validate as validate_module

        with tempfile.TemporaryDirectory() as tmp:
            record_path = Path(tmp) / "record.json"
            record_path.write_text(json.dumps(base_record()), encoding="utf-8")
            missing = Path(tmp) / "no-schema.json"
            non_utf8 = Path(tmp) / "non-utf8-schema.json"
            non_utf8.write_bytes(b'{"type": \xff\xfe not-json}')
            invalid = Path(tmp) / "invalid-schema.json"
            invalid.write_text(
                json.dumps({"type": "object", "properties": {"language": {"type": 42}}}),
                encoding="utf-8",
            )
            cases = [
                (missing, "schema-unreadable"),
                (non_utf8, "schema-unreadable"),
                (invalid, "schema-invalid"),
            ]
            for schema_path, reason in cases:
                buf = io.StringIO()
                with mock.patch.object(validate_module, "SCHEMA_PATH", schema_path):
                    with redirect_stdout(buf):
                        code = validate_module.run([str(record_path)])
                out = buf.getvalue()
                self.assertEqual(code, 2, schema_path.name)
                self.assertIn(f"ERROR {reason}", out)
                self.assertNotIn("Traceback", out)
            good = Path(tmp) / "good-schema.json"
            good.write_text(
                (ROOT / "schema" / "core.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            buf = io.StringIO()
            with mock.patch.object(validate_module, "SCHEMA_PATH", good):
                with redirect_stdout(buf):
                    code = validate_module.run([str(record_path)])
            self.assertEqual(code, 0)
            self.assertEqual(buf.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
