"""Check that tap/core.csv and schema/core.schema.json agree, and that the
examples validate.

tap/core.csv is the single source of truth; this script reports every place
where the derived JSON Schema says something different. It also validates
examples/*.json (must pass) and tests/invalid/*.json (must fail).

Usage: python scripts/check_consistency.py   (exit code 0 = consistent)
Requires: jsonschema (pip install jsonschema)
"""
import csv
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
TAP = ROOT / "tap" / "core.csv"
SCHEMA = ROOT / "schema" / "core.schema.json"


def check_tap_vs_schema(rows, schema):
    errors = []
    props = schema["properties"]
    required = set(schema.get("required", []))
    tap_ids = [r["propertyID"] for r in rows]

    for missing in sorted(set(props) - set(tap_ids)):
        errors.append(f"{missing}: in schema but not in TAP")
    for r in rows:
        pid = r["propertyID"]
        if pid not in props:
            errors.append(f"{pid}: in TAP but not in schema")
            continue
        p = props[pid]
        mandatory = r["mandatory"].strip().upper() == "TRUE"
        repeatable = r["repeatable"].strip().upper() == "TRUE"
        if mandatory != (pid in required):
            errors.append(f"{pid}: mandatory={mandatory} in TAP, required={pid in required} in schema")
        if repeatable != (p.get("type") == "array"):
            errors.append(f"{pid}: repeatable={repeatable} in TAP, type={p.get('type')} in schema")
        target = p["items"] if p.get("type") == "array" else p
        if (r["pattern"] or None) != target.get("pattern"):
            errors.append(f"{pid}: pattern {r['pattern']!r} in TAP, {target.get('pattern')!r} in schema")
        tap_enum = r["enum"].split("|") if r["enum"] else None
        if tap_enum != target.get("enum"):
            errors.append(f"{pid}: enum {tap_enum} in TAP, {target.get('enum')} in schema")
        if not p.get("description", "").startswith(f"Block {r['block']}."):
            errors.append(f"{pid}: block {r['block']} in TAP, schema description does not start with 'Block {r['block']}.'")
    return errors


def check_records(validator):
    errors = []
    for path in sorted((ROOT / "examples").glob("*.json")):
        for e in validator.iter_errors(json.loads(path.read_text(encoding="utf-8"))):
            errors.append(f"{path.relative_to(ROOT)}: should be valid, but {e.message}")
    for path in sorted((ROOT / "tests" / "invalid").glob("*.json")):
        if not list(validator.iter_errors(json.loads(path.read_text(encoding="utf-8")))):
            errors.append(f"{path.relative_to(ROOT)}: should be invalid, but passes")
    return errors


def main():
    with TAP.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    validator = Draft7Validator(schema, format_checker=FormatChecker())

    errors = check_tap_vs_schema(rows, schema) + check_records(validator)
    for e in errors:
        print("ERROR  " + e)
    if errors:
        return 1
    print(f"OK: {len(rows)} TAP rows match the schema; examples valid; invalid fixtures rejected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
