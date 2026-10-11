#!/usr/bin/env python3
"""Validate IMM-Core records against the JSON Schema plus rules R1-R8.

Usage:
    python tools/validate.py RECORD.json [RECORD.json ...]
    python tools/validate.py --collection tools/examples/collection-OHX.toml RECORD.json
    python tools/validate.py --self-test

Step one is JSON parsing and Draft-07 schema validation with a format
checker. Step two runs the additional rules R1-R8, which the schema cannot
express (full-string pattern match, cross-field checks, serialized lists,
segment order, collection checks, blank text). Patterns are read from the
schema itself; no pattern is hard-coded here a second time.

Output lines name only the file, the rule and the field path, because
validator messages can contain input values. Exit 0 means every record is
valid (warnings are allowed). Exit 1 means at least one record is invalid.
Exit 2 means the configuration, a file, the JSON parsing or the tool run
itself could not be evaluated. This tool works offline on local files only
and needs nothing but the ``jsonschema`` package plus the standard library.

Requires: Python >= 3.11 (``tomllib`` reads the collection file), jsonschema.
"""

import argparse
import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "core.schema.json"
EXAMPLES_DIR = ROOT / "examples"
INVALID_DIR = ROOT / "tests" / "invalid"
INVALID_RULES_DIR = ROOT / "tests" / "invalid-rules"
TOOLS_TESTS_DIR = ROOT / "tests" / "tools"

RULES = ("R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8")

LIST_PREFIX_RE = re.compile(r"\[\s*['\"]")
TIMECODE_SHAPE_RE = re.compile(r"[0-9]{2}:[0-9]{2}:[0-9]{2}")


def display_path(name):
    """Render a file path for a single console line.

    Control characters (tab, CR, LF and others) become ``?`` so a
    crafted file name can never split a diagnosis into two lines.
    Field paths from the schema need no masking; only displayed
    input paths go through here.
    """
    return "".join("?" if ord(c) < 0x20 or ord(c) == 0x7F else c for c in str(name))


def load_schema(path=SCHEMA_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def iter_string_nodes(node, path):
    """Yield (path, pattern, min_length) for every string node in the schema.

    Walks ``properties`` and array ``items`` down to nested timecodes and
    list entries. ``path`` uses ``name`` for objects, ``name[i]`` is resolved
    by the caller for concrete values; here ``[]`` marks array items.
    """
    if not isinstance(node, dict):
        return
    if node.get("type") == "object":
        for name, sub in (node.get("properties") or {}).items():
            yield from iter_string_nodes(sub, f"{path}.{name}" if path else name)
    elif node.get("type") == "array":
        yield from iter_string_nodes(node.get("items", {}), f"{path}[]")
    elif node.get("type") == "string":
        yield (path, node.get("pattern"), node.get("minLength"))


def schema_string_map(schema):
    """Map generic field path (with []) to (pattern, min_length)."""
    return {p: (pat, ml) for (p, pat, ml) in iter_string_nodes(schema, "")}


def iter_record_strings(value, generic_map, prefix=""):
    """Yield (field_path, string_value, pattern, min_length) for a record.

    Paths are concrete (``languages[0]``, ``timecoded_segments[1].start``);
    the generic schema path replaces each index with ``[]`` for lookup.
    """
    if isinstance(value, dict):
        for key, sub in value.items():
            yield from iter_record_strings(sub, generic_map, f"{prefix}.{key}" if prefix else key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from iter_record_strings(item, generic_map, f"{prefix}[{i}]")
    elif isinstance(value, str):
        generic = re.sub(r"\[\d+\]", "[]", prefix)
        pat, ml = generic_map.get(generic, (None, None))
        yield (prefix, value, pat, ml)


def format_schema_path(parts):
    out = ""
    for part in parts:
        if isinstance(part, int):
            out += f"[{part}]"
        else:
            out = f"{out}.{part}" if out else str(part)
    return out or "(record)"


def check_schema(record, validator):
    """Return [(rule, path)] for schema violations; messages are dropped."""
    found = []
    for error in validator.iter_errors(record):
        found.append(("SCHEMA", format_schema_path(list(error.absolute_path))))
    return found


def check_rules(record, schema, collection=None):
    """Run R1-R8 on a schema-valid record. Returns (errors, warnings)."""
    errors = []
    warnings = []
    smap = schema_string_map(schema)
    strings = list(iter_record_strings(record, smap))

    # R1: full match of every schema pattern on present strings.
    for path, value, pattern, _ml in strings:
        if pattern and re.fullmatch(pattern, value) is None:
            errors.append(("R1", path))

    # R2: languages must contain language.
    if "languages" in record and isinstance(record.get("languages"), list):
        lang = record.get("language")
        if lang not in record["languages"]:
            errors.append(("R2", "languages"))

    # R3: serialized non-empty string-only list is an error; a bare
    # list-like prefix that does not parse is a warning. Safe parser only.
    # Detection uses a stripped helper value; the record file is never
    # trimmed or rewritten.
    for path, value, _pat, _ml in strings:
        stripped = value.strip()
        if LIST_PREFIX_RE.match(stripped):
            try:
                parsed = ast.literal_eval(stripped)
            except (SyntaxError, ValueError):
                parsed = None
            if isinstance(parsed, list) and parsed and all(isinstance(x, str) for x in parsed):
                errors.append(("R3", path))
            else:
                warnings.append(("R3", path))

    # R4: end >= start per segment; start not before predecessor start.
    # Only well-formed timecodes take part; R1 flags the rest.
    segments = record.get("timecoded_segments") or []
    start_pat = (smap.get("timecoded_segments[].start") or (None, None))[0]
    end_pat = (smap.get("timecoded_segments[].end") or (None, None))[0]
    prev_start = None
    if isinstance(segments, list):
        for i, seg in enumerate(segments):
            if not isinstance(seg, dict):
                continue
            start = seg.get("start")
            end = seg.get("end")
            start_ok = isinstance(start, str) and start_pat and re.fullmatch(start_pat, start)
            end_ok = isinstance(end, str) and end_pat and re.fullmatch(end_pat, end)
            if start_ok and end_ok and end < start:
                errors.append(("R4", f"timecoded_segments[{i}]"))
            if start_ok:
                if prev_start is not None and start < prev_start:
                    errors.append(("R4", f"timecoded_segments[{i}]"))
                prev_start = start

    # R5: comma-separated persons are a warning only, never an error.
    for field in ("interviewer", "interviewee_display"):
        value = record.get(field)
        if isinstance(value, str) and "," in value:
            warnings.append(("R5", field))

    # R6/R7: collection checks.
    if collection is not None:
        consent = record.get("consent_status")
        if consent != "withdrawn" and consent not in collection["consent_values"]:
            errors.append(("R6", "consent_status"))
        rid = record.get("record_id")
        try:
            rid_ok = isinstance(rid, str) and re.fullmatch(collection["record_id_pattern"], rid) is not None
        except (TypeError, re.error):
            rid_ok = False
        if not rid_ok:
            errors.append(("R7", "record_id"))

    # R8: strings under minLength >= 1 must be non-blank after strip,
    # including list entries and segment labels (label is checked even
    # though the schema sets no minLength on it).
    for path, value, _pat, ml in strings:
        needs = (ml is not None and ml >= 1) or path.endswith(".label") or path == "label"
        if needs and not value.strip():
            errors.append(("R8", path))

    return errors, warnings


def load_collection(path):
    """Load a collection TOML file. Raises ValueError with a fixed reason."""
    import tomllib

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError("unreadable") from exc
    except Exception as exc:  # tomllib.TOMLDecodeError
        raise ValueError("invalid-toml") from exc
    try:
        coll = data["collection"]
        pattern = coll["record_id_pattern"]
        values = coll["consent_values"]
    except (KeyError, TypeError) as exc:
        raise ValueError("missing-keys") from exc
    if not isinstance(pattern, str):
        raise ValueError("bad-pattern")
    try:
        re.compile(pattern)
    except re.error as exc:
        raise ValueError("bad-pattern") from exc
    if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v for v in values):
        raise ValueError("bad-consent-values")
    return {"record_id_pattern": pattern, "consent_values": values}


def validate_file(path, validator, schema, collection=None):
    """Validate one file. Returns (errors, warnings, tool_error)."""
    try:
        with open(path, encoding="utf-8") as f:
            record = json.load(f)
    except (OSError, UnicodeDecodeError):
        return [], [], "unreadable"
    except json.JSONDecodeError:
        return [], [], "invalid-json"
    if not isinstance(record, dict):
        return [("SCHEMA", "(record)")], [], None
    schema_errors = check_schema(record, validator)
    if schema_errors:
        # A wrong JSON field type is Exit 1; rules run on valid records only.
        return schema_errors, [], None
    errors, warnings = check_rules(record, schema, collection)
    return errors, warnings, None


def run(argv=None):
    parser = argparse.ArgumentParser(description="Validate IMM-Core records (schema plus rules R1-R8).")
    parser.add_argument("records", nargs="*", help="Record JSON files to validate.")
    parser.add_argument("--collection", default=None, help="Collection TOML file for rules R6/R7.")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in separation checks.")
    args = parser.parse_args(argv)

    try:
        schema = load_schema(SCHEMA_PATH)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        print(f"{display_path(SCHEMA_PATH)} ERROR schema-unreadable")
        return 2
    try:
        Draft7Validator.check_schema(schema)
    except Exception:
        print(f"{display_path(SCHEMA_PATH)} ERROR schema-invalid")
        return 2
    validator = Draft7Validator(schema, format_checker=FormatChecker())

    if args.self_test:
        return self_test(validator, schema)

    if not args.records:
        print("ERROR no-input-files")
        return 2

    collection = None
    if args.collection is not None:
        try:
            collection = load_collection(args.collection)
        except ValueError as exc:
            print(f"{display_path(args.collection)} ERROR collection-{exc}")
            return 2

    exit_code = 0
    for name in args.records:
        errors, warnings, tool_error = validate_file(name, validator, schema, collection)
        shown = display_path(name)
        if tool_error is not None:
            print(f"{shown} ERROR {tool_error}")
            exit_code = 2
            continue
        for rule, path in warnings:
            print(f"{shown} {rule} {path} warning")
        for rule, path in errors:
            print(f"{shown} {rule} {path}")
        if errors and exit_code == 0:
            exit_code = 1
    return exit_code


def cli(args, validator, schema):
    """Run the CLI in-process for tests. Returns (exit_code, output_lines)."""
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    old = sys.argv
    sys.argv = ["validate.py"] + list(args)
    try:
        with redirect_stdout(buf):
            code = run()
    finally:
        sys.argv = old
    return code, buf.getvalue().splitlines()


def self_test(validator, schema):
    """Separate schema cases from rule cases and check CLI exit codes."""
    failures = []

    def check(condition, label):
        if not condition:
            failures.append(label)
            print(f"SELFTEST-FAIL {label}")

    # tests/invalid/ must already fail at the schema.
    for path in sorted(INVALID_DIR.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        schema_errors = check_schema(record, validator)
        check(bool(schema_errors), f"schema-rejects {path.name}")

    # Synthetic collection for the collection-bound rule cases.
    with tempfile.TemporaryDirectory() as tmp:
        coll_path = Path(tmp) / "collection-synth.toml"
        coll_path.write_text(
            '[collection]\ncode = "SYN"\nname = "Synthetic collection"\n'
            'synthetic = true\nrecord_id_pattern = "^[0-9]{4}-[0-9]{2}-[0-9]{2}_OHX_[0-9]{4}$"\n'
            'consent_values = ["research-only", "teaching", "public", "embargoed"]\n',
            encoding="utf-8",
        )
        collection = load_collection(str(coll_path))

        expected_rules = {
            "languages-without-language.json": {"R2"},
            "language-trailing-newline.json": {"R1"},
            "timecode-trailing-newline.json": {"R1"},
            "python-list-in-string.json": {"R3"},
            "list-with-leading-whitespace.json": {"R3"},
            "segment-end-before-start.json": {"R4"},
            "segment-order-backwards.json": {"R4"},
            "consent-not-in-collection.json": {"R6"},
            "record-id-wrong-collection-pattern.json": {"R7"},
            "blank-title.json": {"R8"},
        }
        # tests/invalid-rules/ is schema-valid and fails only via the rules.
        for path in sorted(INVALID_RULES_DIR.glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            schema_errors = check_schema(record, validator)
            errors, _warnings = check_rules(record, schema, collection)
            got = {rule for rule, _p in errors}
            check(not schema_errors, f"rules-case-schema-valid {path.name}")
            check(bool(errors), f"rules-case-fails {path.name}")
            if path.name in expected_rules:
                check(got == expected_rules[path.name], f"rules-case-exact {path.name} got={sorted(got)}")

        # Positive and warning cases in tests/tools (synthetic files only).
        for name, want_warnings in (
            ("valid-multilingual.json", set()),
            ("warn-comma.json", {"R5"}),
            ("warn-list-prefix.json", {"R3"}),
        ):
            path = TOOLS_TESTS_DIR / name
            record = json.loads(path.read_text(encoding="utf-8"))
            schema_errors = check_schema(record, validator)
            errors, warnings = check_rules(record, schema, collection)
            check(not schema_errors, f"tools-case-schema-valid {name}")
            check(not errors, f"tools-case-no-errors {name}")
            check({rule for rule, _p in warnings} == want_warnings, f"tools-case-warnings {name}")

        # Real CLI exit codes through a subprocess.
        def cli_code(*cli_args):
            proc = subprocess.run(
                [sys.executable, str(ROOT / "tools" / "validate.py"), *cli_args],
                capture_output=True,
                text=True,
                cwd=str(ROOT),
            )
            return proc.returncode, proc.stdout, proc.stderr

        valid = str(TOOLS_TESTS_DIR / "valid-multilingual.json")
        code, _out, err = cli_code(valid)
        check(code == 0 and not err, "cli-valid-exit-0")
        bad = str(INVALID_RULES_DIR / "languages-without-language.json")
        code, _out, err = cli_code(bad)
        check(code == 1 and not err, "cli-rules-exit-1")
        schema_bad = str(INVALID_DIR / "empty-title.json")
        code, _out, err = cli_code(schema_bad)
        check(code == 1 and not err, "cli-schema-exit-1")
        code, _out, err = cli_code(str(TOOLS_TESTS_DIR / "does-not-exist.json"))
        check(code == 2, "cli-missing-exit-2")
        broken = Path(tmp) / "broken.json"
        broken.write_text("{not json", encoding="utf-8")
        code, _out, err = cli_code(str(broken))
        check(code == 2 and not err, "cli-broken-exit-2")
        # A file name with control characters stays one masked console line.
        ctrl_name = Path(tmp) / "lf\nname.json"
        ctrl_name.write_text(
            json.dumps({
                "record_id": "2025-01-01_OHX_0001",
                "interview_date": "2025-01-01",
                "interviewer": "A. B.",
                "title": "   ",
                "consent_status": "public",
                "accessRights": "open",
                "language": "eng",
            }),
            encoding="utf-8",
        )
        code, out, err = cli_code(str(ctrl_name))
        check(code == 1 and not err, "cli-control-char-path-exit-1")
        check(
            len(out.splitlines()) == 1 and "R8" in out and "title" in out
            and "lf?name.json" in out,
            "cli-control-char-path-single-line",
        )
        code, _out, err = cli_code("--collection", str(Path(tmp) / "nope.toml"), valid)
        check(code == 2, "cli-bad-collection-exit-2")
        int_pattern = Path(tmp) / "int-pattern.toml"
        int_pattern.write_text(
            '[collection]\nrecord_id_pattern = 42\nconsent_values = ["public"]\n',
            encoding="utf-8",
        )
        code, _out, err = cli_code("--collection", str(int_pattern), valid)
        check(code == 2 and not err, "cli-int-pattern-exit-2")
        code, _out, err = cli_code(
            "--collection", str(coll_path), str(INVALID_RULES_DIR / "consent-not-in-collection.json")
        )
        check(code == 1, "cli-collection-rules-exit-1")

        # Examples stay valid, with and without the synthetic collection.
        for example in sorted(EXAMPLES_DIR.glob("*.json")):
            code, _out, err = cli_code(str(example))
            check(code == 0 and not err, f"cli-example-valid {example.name}")

    if failures:
        print(f"SELFTEST {len(failures)} failures")
        return 1
    print("SELFTEST OK: schema and rule cases separated; CLI codes checked.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
