"""Unit tests for tools/imm2dataverse.py: in-process mapping and rule checks.

Only synthetic records; no network. Run from the repository root with
``python -m unittest discover -s tests/tools``.
"""

import json
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent.parent
sys.path.insert(0, str(ROOT))

from tools.imm2dataverse import (  # noqa: E402
    ConfigError,
    evaluate,
    load_config,
    load_languages,
    normalize_related,
    project,
    safe_stem,
    split_persons,
)


def base_record(**overrides):
    record = {
        "record_id": "2025-01-01_OHX_0001",
        "interview_date": "2025-01-01",
        "interviewer": "A. B.",
        "title": "Interview on work and migration",
        "consent_status": "public",
        "accessRights": "open",
        "language": "deu",
        "abstract": "The narrator describes work and migration experiences.",
    }
    record.update(overrides)
    return record


class ConverterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config(str(ROOT / "tools" / "examples" / "collection-OHX.toml"))
        cls.languages = load_languages(str(ROOT / "tools" / "data" / "dataverse-languages.tsv"))

    def test_example_config_loads(self):
        self.assertEqual(self.config["code"], "OHX")
        self.assertTrue(self.config["synthetic"])
        self.assertEqual(self.config["export_consent"], ["public"])

    def test_table_size_and_spot_values(self):
        self.assertEqual(len(self.languages), 7915)
        for code, name in (
            ("deu", "German"),
            ("ltz", "Luxembourgish, Letzeburgesch"),
            ("fra", "French"),
            ("eng", "English"),
            ("por", "Portuguese"),
            ("ita", "Italian"),
            ("nld", "Dutch"),
        ):
            self.assertEqual(self.languages[code], name)

    def test_broken_config_rejected(self):
        with self.assertRaises(ConfigError):
            load_config(str(TESTS_DIR / "does-not-exist.toml"))

    def test_split_persons_semicolon_only(self):
        self.assertEqual(split_persons("Jane Smith; John Doe"), ["Jane Smith", "John Doe"])
        self.assertEqual(split_persons("Smith, John"), ["Smith, John"])
        self.assertEqual(split_persons("Jane Smith (0000-0001-2345-6789)"), ["Jane Smith"])
        self.assertIsNone(split_persons("(0000-0001-2345-6789)"))

    def test_split_persons_keeps_year_brackets(self):
        self.assertEqual(split_persons("Example Person (1939)"), ["Example Person (1939)"])
        self.assertEqual(
            split_persons("Jane Smith (0000-0001-2345-6789); Example Person (1939)"),
            ["Jane Smith", "Example Person (1939)"],
        )

    def test_normalize_related(self):
        hosts = ["doi.org", "example.org"]
        self.assertEqual(
            normalize_related("https://example.org/a/b", hosts),
            "https://example.org/a/b",
        )
        self.assertEqual(
            normalize_related("https://example.org:8443/a/b", hosts),
            "https://example.org:8443/a/b",
        )
        self.assertEqual(
            normalize_related("doi:10.5555/imm-example-0042", hosts),
            "https://doi.org/10.5555/imm-example-0042",
        )
        for bad in (
            "http://example.org/plain",
            "https://elsewhere.org/file.pdf",
            "https://user@example.org/file.pdf",
            "not a url",
            "https://doi.org:bad/10.5555/qa",
            "https://example.org/a/b?x=1",
            "https://example.org/a/b#frag",
            "https://example.org/a/b?",
            "https://example.org/a/b#",
            "doi:10.5555/qa?x=1",
        ):
            self.assertIsNone(normalize_related(bad, hosts), bad)

    def test_safe_stem(self):
        self.assertEqual(safe_stem("2025-01-01_OHX_0001"), "DS_2025-01-01_OHX_0001")
        self.assertEqual(safe_stem("WALZ-1000"), "DS_WALZ-1000")
        for bad in ("", ".", "..", "a/b", "a\\b", "WALZ-0003/../x",
                    "WALZ-1000\tQA", "A\nB", "A\rb", "A\x00B", "A\x7fB"):
            self.assertIsNone(safe_stem(bad), bad)

    def test_evaluate_build(self):
        status, _detail = evaluate(base_record(), self.config, self.languages, [])
        self.assertEqual(status, "BUILD")

    def test_evaluate_skips(self):
        cases = [
            (base_record(consent_status="withdrawn", accessRights="closed"), "withdrawn"),
            (base_record(accessRights="closed"), "access-closed"),
            (base_record(consent_status="embargoed"), "embargoed"),
            (base_record(consent_status="teaching"), "consent-not-exported"),
            (base_record(accessRights="restricted"), "access-not-exported"),
            (base_record(language="zzz"), "language-unmapped"),
        ]
        record = base_record()
        del record["abstract"]
        cases.append((record, "abstract-missing"))
        names = [["harbor"], ["master"]]
        cases.append((base_record(title="Notes by the Harbor Master"), "name-hit"))
        for record, reason in cases:
            entries = names if reason == "name-hit" else []
            status, detail = evaluate(record, self.config, self.languages, entries)
            self.assertEqual((status, detail), ("SKIP", reason))

    def test_project_never_list(self):
        record = base_record(
            interviewee_display="Pseudonym A",
            governance_ref="urn:example:governance:synth-1",
            consent_status="public",
            timecoded_segments=[{"start": "00:00:00", "end": "00:01:00", "label": "X"}],
        )
        payload, _skipped = project(record, self.config, self.languages)
        text = json.dumps(payload)
        for token in ("Pseudonym A", "governance_ref", "consent_status", "interviewee_display",
                      "timecoded_segments", "accessRights", "synth-1"):
            self.assertNotIn(token, text)

    def test_licence_garbage_is_rejected(self):
        import tempfile

        base = (ROOT / "tools" / "examples" / "collection-OHX.toml").read_text(encoding="utf-8")
        variants = [
            base.replace('names_file = ""', 'names_file = ""\ncustom_terms_of_use = " "'),
            base.replace('names_file = ""', 'names_file = ""\ncustom_terms_of_use = 7'),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for i, text in enumerate(variants):
                path = Path(tmp) / f"coll-{i}.toml"
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(ConfigError, msg=f"variant {i}"):
                    load_config(str(path))

    def test_missing_switches_default_false(self):
        import tempfile

        base = (ROOT / "tools" / "examples" / "collection-OHX.toml").read_text(encoding="utf-8")
        text = base.replace("export_record_id = false\n", "").replace("export_interviewer = false\n", "")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coll.toml"
            path.write_text(text, encoding="utf-8")
            config = load_config(str(path))
        self.assertIs(config["export_record_id"], False)
        self.assertIs(config["export_interviewer"], False)

    def test_checked_licence_mode_reaches_projection(self):
        self.assertEqual(self.config["license_mode"], "license")
        payload, _skipped = project(base_record(), self.config, self.languages)
        version = payload["datasetVersion"]
        self.assertIn("license", version)
        self.assertNotIn("termsOfUse", version)

    def test_multiple_authors_share_one_compound(self):
        import copy

        config = copy.deepcopy(self.config)
        config["authors"] = [
            {"name": "First Author", "affiliation": "First Institute"},
            {"name": "Second Author", "affiliation": ""},
        ]
        payload, _skipped = project(base_record(), config, self.languages)
        fields = payload["datasetVersion"]["metadataBlocks"]["citation"]["fields"]
        authors = [f for f in fields if f["typeName"] == "author"]
        self.assertEqual(len(authors), 1)
        self.assertEqual(
            [c["authorName"]["value"] for c in authors[0]["value"]],
            ["First Author", "Second Author"],
        )

    def test_encoded_blocked_name_in_url_is_hit(self):
        entries = [["harbor", "master"]]
        record = base_record(related_materials=["https://example.org/%48arbor%20%4daster.pdf"])
        config = dict(self.config)
        config["allowed_hosts"] = ["example.org"]
        self.assertEqual(evaluate(record, config, self.languages, entries), ("SKIP", "name-hit"))

    def test_snapshot_bytes_parse_and_hash(self):
        import hashlib
        import tempfile

        from tools.imm2dataverse import load_config as reload_config

        base = (ROOT / "tools" / "examples" / "collection-OHX.toml").read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coll.toml"
            path.write_bytes(base)
            raw = path.read_bytes()
            path.write_text(base.decode("utf-8").replace(
                "export_interviewer = false", "export_interviewer = true"), encoding="utf-8")
            config = reload_config(str(path), raw)
        self.assertIs(config["export_interviewer"], False)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), hashlib.sha256(base).hexdigest())

    def test_exclusive_placement_keeps_foreign_bytes(self):
        import tempfile

        from tools.imm2dataverse import _write_file

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "DS_X.json"
            target.write_bytes(b'{"foreign": true}')
            with self.assertRaises(FileExistsError):
                _write_file(target, b'{"own": true}')
            self.assertEqual(target.read_bytes(), b'{"foreign": true}')

    def test_fail_names_file_rule_and_path_never_value(self):
        import json
        import subprocess
        import sys
        import tempfile

        collection = str(ROOT / "tools" / "examples" / "collection-OHX.toml")
        with tempfile.TemporaryDirectory() as tmp:
            bad_path = Path(tmp) / "marker.json"
            bad_path.write_text(json.dumps(base_record(record_id="SYNTHETIC_PRIVATE_MARKER")), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "imm2dataverse.py"),
                 "check", "--collection", collection, str(bad_path)],
                capture_output=True, text=True, cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(proc.stderr, "")
            lines = proc.stdout.splitlines()
            self.assertEqual(len(lines), 1, proc.stdout)
            self.assertIn("FAIL", lines[0])
            self.assertIn("R7", lines[0])
            self.assertIn("record_id", lines[0])
            self.assertIn("marker.json", lines[0])
            self.assertNotIn("SYNTHETIC_PRIVATE_MARKER", proc.stdout)
            out = Path(tmp) / "out-marker"
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "imm2dataverse.py"),
                 "build", "--collection", collection, "--out", str(out), str(bad_path)],
                capture_output=True, text=True, cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 1)
            self.assertNotIn("SYNTHETIC_PRIVATE_MARKER", proc.stdout)
            self.assertNotIn("SYNTHETIC_PRIVATE_MARKER", proc.stderr)
            self.assertFalse(out.exists())
            # Positive counterpart: a valid id keeps its label.
            good_path = Path(tmp) / "good.json"
            good_path.write_text(json.dumps(base_record()), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "imm2dataverse.py"),
                 "check", "--collection", collection, str(good_path)],
                capture_output=True, text=True, cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 0)
            self.assertIn("BUILD 2025-01-01_OHX_0001", proc.stdout)

    def test_check_masks_control_chars_in_record_file_name(self):
        import json
        import subprocess
        import sys
        import tempfile

        collection = str(ROOT / "tools" / "examples" / "collection-OHX.toml")
        with tempfile.TemporaryDirectory() as tmp:
            tricky = Path(tmp) / "lf\nname.json"
            tricky.write_text(
                json.dumps(base_record(record_id="SYNTHETIC_PRIVATE_MARKER")), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "imm2dataverse.py"),
                 "check", "--collection", collection, str(tricky)],
                capture_output=True, text=True, cwd=str(ROOT),
            )
            self.assertEqual(proc.returncode, 1)
            self.assertEqual(proc.stderr, "")
            lines = proc.stdout.splitlines()
            self.assertEqual(len(lines), 1, proc.stdout)
            self.assertIn("FAIL", lines[0])
            self.assertIn("R7", lines[0])
            self.assertIn("record_id", lines[0])
            self.assertIn("lf?name.json", lines[0])
            self.assertNotIn("SYNTHETIC_PRIVATE_MARKER", proc.stdout)

    def test_schema_errors_are_exit_2_for_check_and_build(self):
        import io
        import json
        import tempfile
        from contextlib import redirect_stdout
        from unittest import mock

        import tools.imm2dataverse as converter_module

        collection = str(ROOT / "tools" / "examples" / "collection-OHX.toml")
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
                with mock.patch.object(converter_module, "SCHEMA_PATH", schema_path):
                    for command in ("check", "build"):
                        out_dir = Path(tmp) / f"out-{schema_path.stem}-{command}"
                        argv = ["check", "--collection", collection, str(record_path)]
                        if command == "build":
                            argv = ["build", "--collection", collection,
                                    "--out", str(out_dir), str(record_path)]
                        buf = io.StringIO()
                        with redirect_stdout(buf):
                            code = converter_module.run(argv)
                        out = buf.getvalue()
                        self.assertEqual(code, 2, f"{schema_path.name}/{command}")
                        self.assertIn(f"ERROR {reason}", out)
                        self.assertNotIn("Traceback", out)
                        self.assertNotIn("SKIP", out)
            good = Path(tmp) / "good-schema.json"
            good.write_text(
                (ROOT / "schema" / "core.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            with mock.patch.object(converter_module, "SCHEMA_PATH", good):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = converter_module.run(
                        ["check", "--collection", collection, str(record_path)])
                self.assertEqual(code, 0)
                self.assertIn("BUILD 2025-01-01_OHX_0001", buf.getvalue())

    def test_project_committed_fixture(self):
        record = json.loads((TESTS_DIR / "conv-build.json").read_text(encoding="utf-8"))
        config = dict(self.config)
        config["export_interviewer"] = True
        config["export_record_id"] = True
        config["allowed_hosts"] = ["doi.org", "example.org"]
        self.assertEqual(evaluate(record, config, self.languages, [])[0], "BUILD")
        payload, skipped = project(record, config, self.languages)
        self.assertEqual(skipped, 4)
        self.assertEqual(set(payload), {"datasetVersion"})
        by_name = {f["typeName"]: f for f in payload["datasetVersion"]["metadataBlocks"]["citation"]["fields"]}
        self.assertEqual(by_name["language"]["value"], ["German", "Luxembourgish, Letzeburgesch"])
        self.assertEqual(
            [c["contributorName"]["value"] for c in by_name["contributor"]["value"]],
            ["Jane Smith", "John Doe"],
        )


if __name__ == "__main__":
    unittest.main()
