#!/usr/bin/env python3
"""Offline converter: IMM-Core records to Dataverse citation JSON plus empty ZIP.

Usage:
    python tools/imm2dataverse.py check --collection FILE.toml RECORD.json [RECORD.json ...]
    python tools/imm2dataverse.py build --collection FILE.toml --out DIR RECORD.json [RECORD.json ...]
    python tools/imm2dataverse.py --self-test

``check`` evaluates locally without writing any file: BUILD means the record
can be projected, SKIP carries a fixed reason for regular withholding, FAIL
names the input file, the rule and the field path for invalid records
(never the invalid value). ``build`` runs the same check for
the whole batch first and aborts before writing anything when a record is
invalid, a ``record_id`` repeats, the configuration is unusable, a file name
is unsafe or a target file already exists. Regular SKIP records never block
the other valid records of the batch.

Per BUILD record ``build`` writes ``DS_<record_id>.json`` (exactly one root
object ``datasetVersion``) plus a valid ZIP with zero entries, and appends
one line per evaluated record to the private ``build.tsv`` log (timestamp,
record id, status, detail, SHA-256 of source record, configuration,
names file, schema, language table and generated JSON). The output
directory is created with mode 700; files get mode 600; a pre-existing
directory with other modes stops the run before writing. Nothing is ever
overwritten: existing target files stop the run before writing.

A local file is neither a release permission nor proof that a remote
instance would accept the record. This tool only checks and writes files;
it contains no remote path of any kind.

Exit 0: every evaluated record is BUILD or regular SKIP (even a fully
withheld batch). Exit 1: at least one invalid record. Exit 2: unusable
configuration or source, duplicate id, unsafe file name, existing output,
or a write error. Messages carry fixed reasons and field paths, never
field values.

Requires: Python >= 3.11, jsonschema. Offline; local files only. The only
collection configuration in this repository is the synthetic
``tools/examples/collection-OHX.toml``; real configurations, name lists
and outputs live outside the repository.
"""

import argparse
import datetime
import errno
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from tools.validate import check_rules, check_schema, display_path
except ImportError:  # run as tools/imm2dataverse.py: sibling module is on the path
    from validate import check_rules, check_schema, display_path
from jsonschema import Draft7Validator, FormatChecker
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "core.schema.json"
DEFAULT_LANGUAGES = ROOT / "tools" / "data" / "dataverse-languages.tsv"
EXAMPLE_COLLECTION = ROOT / "tools" / "examples" / "collection-OHX.toml"
TOOLS_TESTS_DIR = ROOT / "tests" / "tools"

SUBJECTS = (
    "Agricultural Sciences",
    "Arts and Humanities",
    "Astronomy and Astrophysics",
    "Business and Management",
    "Chemistry",
    "Computer and Information Science",
    "Earth and Environmental Sciences",
    "Engineering",
    "Law",
    "Mathematical Sciences",
    "Medicine, Health and Life Sciences",
    "Physics",
    "Social Sciences",
    "Other",
)

ACCESS_VALUES = ("open", "restricted")
# Only a real ORCID bracket is removed: four digit groups with a check
# character at the end. Ordinary year brackets such as (1939) stay.
ORCID_RE = re.compile(r"\s*\(\d{4}-\d{4}-\d{4}-\d{3}[\dXx]\)\s*$")
WORD_RE = re.compile(r"\w+", re.UNICODE)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


class ConfigError(Exception):
    """Unusable collection configuration; the message is a fixed reason."""


def _need(cond, reason):
    if not cond:
        raise ConfigError(reason)


def _nonempty_str(value):
    return isinstance(value, str) and bool(value.strip())


def _read_snapshot(path, reason):
    """Read a file exactly once; the returned bytes are parsed and hashed."""
    try:
        return Path(path).read_bytes()
    except OSError as exc:
        raise ConfigError(reason) from exc


def parse_names(text):
    """Split blocked person tokens into lowercase word lists."""
    entries = []
    for line in text.splitlines():
        words = WORD_RE.findall(line.lower())
        if words:
            entries.append(words)
    return entries


def load_config(path, raw=None):
    """Load and check a collection TOML file. Returns a plain dict.

    When ``raw`` holds the file bytes they are parsed directly, so the
    caller can hash exactly the bytes used here (byte snapshot).
    """
    import tomllib

    if raw is None:
        raw = _read_snapshot(path, "collection-unreadable")
    try:
        data = tomllib.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ConfigError("collection-invalid-toml") from exc
    _need(isinstance(data, dict), "collection-invalid-toml")

    try:
        coll = data["collection"]
        dvc = data["dataverse"]
    except (KeyError, TypeError) as exc:
        raise ConfigError("collection-missing-section") from exc
    _need(isinstance(coll, dict) and isinstance(dvc, dict), "collection-missing-section")

    _need(_nonempty_str(coll.get("code")), "collection-bad-code")
    _need(_nonempty_str(coll.get("name")), "collection-bad-name")
    _need(isinstance(coll.get("synthetic"), bool), "collection-bad-synthetic")
    synthetic = coll["synthetic"]
    try:
        record_id_re = re.compile(coll["record_id_pattern"])
    except (KeyError, TypeError, re.error) as exc:
        raise ConfigError("collection-bad-record-id-pattern") from exc
    consent_values = coll.get("consent_values")
    _need(
        isinstance(consent_values, list)
        and consent_values
        and all(_nonempty_str(v) for v in consent_values),
        "collection-bad-consent-values",
    )

    _need(isinstance(dvc.get("other_id_agency"), str), "collection-bad-agency")
    subjects = dvc.get("subject")
    _need(isinstance(subjects, list) and subjects, "collection-bad-subject")
    for subject in subjects:
        _need(subject in SUBJECTS, "collection-unknown-subject")
    kinds = dvc.get("kind_of_data")
    _need(isinstance(kinds, list) and kinds and all(_nonempty_str(k) for k in kinds), "collection-bad-kind-of-data")

    export_consent = dvc.get("export_consent", [])
    _need(isinstance(export_consent, list), "collection-bad-export-consent")
    for value in export_consent:
        _need(value in consent_values, "collection-export-consent-unknown")
        _need(value not in ("withdrawn", "embargoed"), "collection-export-consent-withheld")
    export_access = dvc.get("export_access", ["open"])
    _need(isinstance(export_access, list), "collection-bad-export-access")
    for value in export_access:
        _need(value in ACCESS_VALUES, "collection-export-access-closed")

    for key in ("export_record_id", "export_interviewer"):
        _need(isinstance(dvc.get(key, False), bool), f"collection-bad-{key.replace('_', '-')}")
    export_record_id = dvc.get("export_record_id", False)
    export_interviewer = dvc.get("export_interviewer", False)
    if export_record_id:
        _need(_nonempty_str(dvc["other_id_agency"]), "collection-agency-required")

    # Licence mode: only string values are checked, and the checked mode
    # is passed on explicitly. The unused alternative must stay empty;
    # whitespace or non-string values are an unusable configuration
    # (exit 2), never a silent selection by raw string truth.
    license_name = dvc.get("license_name", "")
    license_uri = dvc.get("license_uri", "")
    custom_terms = dvc.get("custom_terms_of_use", "")
    _need(
        all(isinstance(v, str) for v in (license_name, license_uri, custom_terms)),
        "collection-bad-licence-mode",
    )
    has_licence = _nonempty_str(license_name) and _nonempty_str(license_uri)
    has_terms = _nonempty_str(custom_terms)
    licence_pair_broken = _nonempty_str(license_name) != _nonempty_str(license_uri)
    _need(not licence_pair_broken, "collection-incomplete-licence")
    _need(has_licence != has_terms, "collection-bad-licence-mode")
    if has_licence:
        _need(custom_terms == "", "collection-bad-licence-mode")
        license_mode = "license"
    else:
        _need(license_name == "" and license_uri == "", "collection-bad-licence-mode")
        license_mode = "terms"

    hosts = dvc.get("allowed_hosts", [])
    _need(isinstance(hosts, list) and all(_nonempty_str(h) for h in hosts), "collection-bad-allowed-hosts")
    for host in hosts:
        _need("://" not in host and "/" not in host, "collection-bad-allowed-hosts")

    authors = dvc.get("author", dvc.get("authors", []))
    if isinstance(authors, dict):
        authors = [authors]
    _need(isinstance(authors, list) and authors, "collection-bad-authors")
    for author in authors:
        _need(isinstance(author, dict) and _nonempty_str(author.get("name")), "collection-bad-authors")
        _need(isinstance(author.get("affiliation", ""), str), "collection-bad-authors")

    try:
        contact = dvc["contact"]
    except KeyError as exc:
        raise ConfigError("collection-bad-contact") from exc
    _need(isinstance(contact, dict), "collection-bad-contact")
    _need(_nonempty_str(contact.get("name")), "collection-bad-contact")
    _need(isinstance(contact.get("email"), str) and EMAIL_RE.match(contact["email"]), "collection-bad-contact-email")

    names_file = dvc.get("names_file", "")
    _need(isinstance(names_file, str), "collection-bad-names-file")
    if not synthetic:
        try:
            approval = data["approval"]
        except KeyError as exc:
            raise ConfigError("collection-approval-required") from exc
        _need(isinstance(approval, dict), "collection-approval-required")
        _need(_nonempty_str(approval.get("role")), "collection-bad-approval")
        _need(_nonempty_str(approval.get("decision_ref")), "collection-bad-approval")
        _need(isinstance(approval.get("date"), str) and DATE_RE.match(approval["date"]), "collection-bad-approval-date")
        try:
            datetime.date.fromisoformat(approval["date"])
        except ValueError as exc:
            raise ConfigError("collection-bad-approval-date") from exc
        _need(_nonempty_str(names_file), "collection-names-file-required")
    names_bytes = b""
    names_entries = []
    if _nonempty_str(names_file):
        names_bytes = _read_snapshot(names_file, "collection-names-file-unreadable")
        try:
            names_text = names_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ConfigError("collection-names-file-unreadable") from exc
        _need(bool(names_text.strip()), "collection-names-file-empty")
        names_entries = parse_names(names_text)
        if not synthetic:
            _need(names_entries, "collection-names-file-unusable")

    return {
        "code": coll["code"],
        "name": coll["name"],
        "synthetic": synthetic,
        "record_id_pattern": coll["record_id_pattern"],
        "record_id_re": record_id_re,
        "consent_values": list(consent_values),
        "other_id_agency": dvc["other_id_agency"],
        "subject": list(subjects),
        "kind_of_data": list(kinds),
        "export_consent": list(export_consent),
        "export_access": list(export_access),
        "export_record_id": export_record_id,
        "export_interviewer": export_interviewer,
        "license_mode": license_mode,
        "license_name": license_name,
        "license_uri": license_uri,
        "custom_terms_of_use": custom_terms,
        "allowed_hosts": [h.lower() for h in hosts],
        "authors": [{"name": a["name"], "affiliation": a.get("affiliation", "")} for a in authors],
        "contact": {"name": contact["name"], "email": contact["email"]},
        "names_file": names_file,
        "names_bytes": names_bytes,
        "names_entries": names_entries,
    }


def load_languages(path, raw=None):
    """Load the pinned ISO 639-3 to English-name table. Returns a dict.

    When ``raw`` holds the file bytes they are parsed directly, so the
    caller can hash exactly the bytes used here (byte snapshot).
    """
    if raw is None:
        raw = _read_snapshot(path, "languages-unreadable")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ConfigError("languages-unreadable") from exc
    table = {}
    header_seen = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if not line or line.startswith("#"):
            continue
        if not header_seen:
            if line != "iso639_3\tname":
                raise ConfigError("languages-bad-header")
            header_seen = True
            continue
        parts = line.split("\t")
        if len(parts) != 2 or not re.fullmatch(r"[a-z]{3}", parts[0]) or not parts[1]:
            raise ConfigError("languages-bad-row")
        if parts[0] in table:
            raise ConfigError("languages-duplicate-code")
        table[parts[0]] = parts[1]
    if not header_seen or not table:
        raise ConfigError("languages-empty")
    return table


def load_names(path, raw=None):
    """Load blocked person tokens, one per line. Empty path means no list."""
    if not path:
        return []
    if raw is None:
        raw = _read_snapshot(path, "names-file-unreadable")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ConfigError("names-file-unreadable") from exc
    return parse_names(text)


def text_has_hit(text, entries):
    """Case-insensitive whole-word match of any multi-word entry."""
    words = WORD_RE.findall(text.lower())
    for entry in entries:
        size = len(entry)
        for i in range(len(words) - size + 1):
            if words[i : i + size] == entry:
                return True
    return False


def normalize_related(value, allowed_hosts):
    """Normalize one related-materials entry; None means skip it.

    Admits DOI references (``doi:`` or DOI URLs) and HTTPS URLs whose
    exactly parsed host is listed. Entries with query or fragment parts,
    with an invalid port, with user information, or on an unlisted host
    are skipped and counted, never repaired and never truncated: cutting
    ``https://doi.org/10.5555/qa?x=1`` down to its host and path would
    change the address.
    """
    raw = value.strip()
    if raw.lower().startswith("doi:"):
        raw = "https://doi.org/" + raw[4:].strip()
    try:
        parts = urlsplit(raw)
    except ValueError:
        return None
    if parts.scheme != "https":
        return None
    if parts.username or parts.password:
        return None
    # Query and fragment parts are rejected from the raw text, so an
    # empty query ("?") or fragment ("#") is skipped as well.
    if "#" in raw or "?" in raw.split("#", 1)[0]:
        return None
    host = (parts.hostname or "").lower()
    if not host or host not in allowed_hosts:
        return None
    try:
        port = parts.port
    except ValueError:
        return None
    netloc = host
    if port:
        netloc += f":{port}"
    return f"https://{netloc}{parts.path or ''}"


def split_persons(value):
    """Split a person string on '; ' and drop ORCID brackets.

    Only '; ' separates persons; a comma never splits. Returns None when
    no projectable person remains.
    """
    persons = []
    for chunk in value.split("; "):
        name = ORCID_RE.sub("", chunk).strip()
        if name:
            persons.append(name)
    return persons or None


def evaluate(record, config, languages, names):
    """Evaluate one valid record. Returns (status, detail).

    Status is BUILD or SKIP with a fixed reason. FAIL never comes from
    here: invalid records are rejected before evaluation.
    """
    if record.get("consent_status") == "withdrawn":
        return "SKIP", "withdrawn"
    if record.get("accessRights") == "closed":
        return "SKIP", "access-closed"
    if record.get("consent_status") == "embargoed":
        return "SKIP", "embargoed"
    if record.get("consent_status") not in config["export_consent"]:
        return "SKIP", "consent-not-exported"
    if record.get("accessRights") not in config["export_access"]:
        return "SKIP", "access-not-exported"
    if not isinstance(record.get("abstract"), str) or not record["abstract"].strip():
        return "SKIP", "abstract-missing"
    codes = [record["language"]]
    for code in record.get("languages", []):
        if code not in codes:
            codes.append(code)
    if any(code not in languages for code in codes):
        return "SKIP", "language-unmapped"
    texts = [record.get("title", ""), record.get("abstract", "")]
    texts.extend(record.get("keywords", []) or [])
    if isinstance(record.get("spatial"), str):
        texts.append(record["spatial"])
    for value in record.get("related_materials", []) or []:
        if isinstance(value, str):
            fixed = normalize_related(value, config["allowed_hosts"])
            if fixed:
                texts.append(fixed)
                # Check the percent-decoded mapped path as well, so an
                # encoded blocked name cannot pass through the URL check.
                texts.append(unquote(urlsplit(fixed).path))
    if config["export_interviewer"] and isinstance(record.get("interviewer"), str):
        texts.append(record["interviewer"])
    if names and any(text_has_hit(t, names) for t in texts if isinstance(t, str)):
        return "SKIP", "name-hit"
    return "BUILD", ""


def _prim(name, value, multiple=False):
    return {"typeName": name, "multiple": multiple, "typeClass": "primitive", "value": value}


def _vocab(name, values, multiple=True):
    return {"typeName": name, "multiple": multiple, "typeClass": "controlledVocabulary", "value": values}


def _compound(name, children, multiple=True):
    return {"typeName": name, "multiple": multiple, "typeClass": "compound", "value": children}


def project(record, config, languages):
    """Project one BUILD record to a datasetVersion object.

    Returns (dataset_version, related_skipped). Raises ValueError with a
    field path when the valid record cannot be projected.
    """
    codes = [record["language"]]
    for code in record.get("languages", []):
        if code not in codes:
            codes.append(code)
    fields = [
        _prim("title", record["title"]),
        _compound("dsDescription", [{"dsDescriptionValue": _prim("dsDescriptionValue", record["abstract"])}]),
        _compound(
            "dateOfCollection",
            [
                {
                    "dateOfCollectionStart": _prim("dateOfCollectionStart", record["interview_date"]),
                    "dateOfCollectionEnd": _prim("dateOfCollectionEnd", record["interview_date"]),
                }
            ],
        ),
        _vocab("language", [languages[c] for c in codes]),
    ]
    if record.get("keywords"):
        fields.append(
            _compound("keyword", [{"keywordValue": _prim("keywordValue", k)} for k in record["keywords"]])
        )
    if config["export_interviewer"]:
        persons = split_persons(record["interviewer"])
        if persons is None:
            raise ValueError("interviewer")
        fields.append(
            _compound(
                "contributor",
                [
                    {
                        "contributorName": _prim("contributorName", person),
                        "contributorType": _vocab("contributorType", "Data Collector", multiple=False),
                    }
                    for person in persons
                ],
            )
        )
    if isinstance(record.get("spatial"), str):
        fields.append(_prim("productionPlace", [record["spatial"]], multiple=True))
    if config["export_record_id"]:
        fields.append(
            _compound(
                "otherId",
                [
                    {
                        "otherIdAgency": _prim("otherIdAgency", config["other_id_agency"]),
                        "otherIdValue": _prim("otherIdValue", record["record_id"]),
                    }
                ],
            )
        )
    admitted = []
    skipped = 0
    for value in record.get("related_materials", []) or []:
        if not isinstance(value, str):
            raise ValueError("related_materials")
        fixed = normalize_related(value, config["allowed_hosts"])
        if fixed is None:
            skipped += 1
        else:
            admitted.append(fixed)
    if admitted:
        fields.append(_prim("relatedMaterial", admitted, multiple=True))
    author_children = []
    for author in config["authors"]:
        child = {"authorName": _prim("authorName", author["name"])}
        if author["affiliation"]:
            child["authorAffiliation"] = _prim("authorAffiliation", author["affiliation"])
        author_children.append(child)
    fields.append(_compound("author", author_children))
    fields.append(
        _compound(
            "datasetContact",
            [
                {
                    "datasetContactName": _prim("datasetContactName", config["contact"]["name"]),
                    "datasetContactEmail": _prim("datasetContactEmail", config["contact"]["email"]),
                }
            ],
        )
    )
    fields.append(_vocab("subject", list(config["subject"])))
    fields.append(_prim("kindOfData", list(config["kind_of_data"]), multiple=True))

    version = {
        "metadataBlocks": {
            "citation": {"displayName": "Citation Metadata", "fields": fields},
        }
    }
    # The licence mode was checked when the configuration was loaded;
    # the projection follows that checked mode only.
    if config["license_mode"] == "terms":
        version["termsOfUse"] = config["custom_terms_of_use"]
    else:
        version["license"] = {"name": config["license_name"], "uri": config["license_uri"]}
    return {"datasetVersion": version}, skipped


def _has_control_chars(value):
    """True when the string holds tabs, line breaks or other controls."""
    return any(ord(c) < 0x20 or ord(c) == 0x7F for c in value)


def safe_stem(record_id):
    """Return the file stem for a record id, or None when it is unsafe.

    The id must be usable as a single file-name part and as one log
    line: no path separator, no traversal, no control characters
    (tab, CR, LF and others), no empty string. Nothing is ever renumbered.
    """
    if not isinstance(record_id, str) or not record_id:
        return None
    if record_id in (".", ".."):
        return None
    if "/" in record_id or "\\" in record_id or "\x00" in record_id:
        return None
    if _has_control_chars(record_id):
        return None
    return f"DS_{record_id}"


def _label(record, path):
    """Console label for a record: the id only when it is display-safe.

    Invalid values never become console labels; the diagnosis then names
    the input file and the field path instead.
    """
    rid = record.get("record_id")
    if isinstance(rid, str) and rid and not _has_control_chars(rid):
        return rid
    return path


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load_batch(paths, validator, schema, collection_cfg):
    """Read and validate every record. Returns (items, tool_error).

    Items hold path, record, source bytes, errors and warnings. A tool
    error (unreadable source) aborts the batch; invalid records are
    reported per file with FAIL.
    """
    items = []
    for path in paths:
        try:
            raw = Path(path).read_bytes()
        except OSError:
            return None, f"{display_path(path)} ERROR unreadable-source"
        try:
            record = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None, f"{display_path(path)} ERROR invalid-json"
        if not isinstance(record, dict):
            items.append({"path": path, "record": {}, "raw": raw, "errors": [("SCHEMA", "(record)")], "warnings": []})
            continue
        schema_errors = check_schema(record, validator)
        if schema_errors:
            items.append({"path": path, "record": record, "raw": raw, "errors": schema_errors, "warnings": []})
            continue
        errors, warnings = check_rules(record, schema, collection_cfg)
        items.append({"path": path, "record": record, "raw": raw, "errors": errors, "warnings": warnings})
    return items, None


def load_inputs(collection_path, languages_path):
    """Read configuration, languages and schema from byte snapshots.

    Every input file is read exactly once; parsing and the protocol
    hashes use those same bytes, so a later file change can never mix
    new settings with output from old settings. Returns
    ``(config, languages, schema, validator, snapshots)`` where
    snapshots maps ``config``, ``languages`` and ``schema`` to bytes.
    Any unreadable input raises ConfigError with a fixed reason.
    """
    config_raw = _read_snapshot(collection_path, "collection-unreadable")
    config = load_config(collection_path, config_raw)
    languages_raw = _read_snapshot(languages_path, "languages-unreadable")
    languages = load_languages(languages_path, languages_raw)
    try:
        schema_raw = _read_snapshot(str(SCHEMA_PATH), "schema-unreadable")
        schema = json.loads(schema_raw.decode("utf-8"))
        Draft7Validator.check_schema(schema)
        validator = Draft7Validator(schema, format_checker=FormatChecker())
    except ConfigError:
        raise
    except SchemaError as exc:
        raise ConfigError("schema-invalid") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ConfigError("schema-unreadable") from exc
    except Exception as exc:
        raise ConfigError("schema-unreadable") from exc
    return config, languages, schema, validator, {
        "config": config_raw,
        "languages": languages_raw,
        "schema": schema_raw,
    }


def _inputs_error(args, exc):
    """Attribute an input error to its file with a fixed reason."""
    reason = str(exc)
    if reason.startswith("collection-"):
        print(f"{display_path(args.collection)} ERROR {reason}")
    elif reason.startswith("languages-") or reason.startswith("names-file-"):
        print(f"{display_path(args.languages)} ERROR {reason}")
    else:
        print(f"{display_path(SCHEMA_PATH)} ERROR {reason}")
    return 2


def _reject_unsafe_ids(items):
    """Stop before any output when an id holds control characters.

    The diagnosis names the input file and the field path; the invalid
    value itself is never printed.
    """
    for item in items:
        rid = item["record"].get("record_id")
        if isinstance(rid, str) and _has_control_chars(rid):
            print(f"ERROR unsafe-record-id {display_path(item['path'])} record_id")
            return 2
    return None


def run_check(args):
    try:
        config, languages, schema, validator, _snapshots = load_inputs(args.collection, args.languages)
    except ConfigError as exc:
        return _inputs_error(args, exc)
    names = config["names_entries"]
    collection_cfg = {
        "record_id_pattern": config["record_id_pattern"],
        "consent_values": config["consent_values"],
    }
    items, tool_error = load_batch(args.records, validator, schema, collection_cfg)
    if tool_error is not None:
        print(tool_error)
        return 2
    problem = _reject_unsafe_ids(items)
    if problem is not None:
        return problem
    seen = set()
    for item in items:
        rid = item["record"].get("record_id")
        if isinstance(rid, str):
            if rid in seen:
                print("ERROR duplicate-record-id")
                return 2
            seen.add(rid)
    exit_code = 0
    for item in items:
        label = _label(item["record"], item["path"])
        if item["errors"]:
            rule, field = item["errors"][0]
            print(f"FAIL {display_path(item['path'])} {rule} {field}")
            exit_code = 1
            continue
        status, detail = evaluate(item["record"], config, languages, names)
        print(f"{status} {label} {detail}".rstrip())
    return exit_code


def _prepare_out_dir(out):
    """Create the output directory with mode 700, or check a present one."""
    if out.exists():
        if not out.is_dir():
            return "output-not-a-directory"
        if stat.S_IMODE(out.stat().st_mode) != 0o700:
            return "output-bad-mode"
        return None
    try:
        out.mkdir(parents=True, mode=0o700)
        os.chmod(out, 0o700)
    except OSError:
        return "output-unwritable"
    return None


def _place_exclusive(path, data):
    """Stage fully built bytes, then place them exclusively at the target.

    The temporary file is completed first; ``os.link`` then fails with
    FileExistsError when the target appeared after the pre-check, and
    the foreign bytes stay untouched. No silent replacement.
    """
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=str(path.parent), prefix=".tmp-", delete=False) as handle:
            tmp = Path(handle.name)
            handle.write(data)
        os.chmod(tmp, 0o600)
        try:
            os.link(tmp, path)
        except FileExistsError:
            raise FileExistsError(errno.EEXIST, "target exists", str(path))
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def _write_file(path, data):
    """Write bytes fully via a temporary file, mode 600. Returns hex digest."""
    _place_exclusive(path, data)
    return sha256_bytes(data)


def run_build(args):
    try:
        config, languages, schema, validator, snapshots = load_inputs(args.collection, args.languages)
    except ConfigError as exc:
        return _inputs_error(args, exc)
    names = config["names_entries"]
    collection_cfg = {
        "record_id_pattern": config["record_id_pattern"],
        "consent_values": config["consent_values"],
    }
    config_bytes = snapshots["config"]
    schema_bytes = snapshots["schema"]
    languages_bytes = snapshots["languages"]
    names_bytes = config["names_bytes"]
    if not args.records:
        print("ERROR no-input-files")
        return 2
    items, tool_error = load_batch(args.records, validator, schema, collection_cfg)
    if tool_error is not None:
        print(tool_error)
        return 2

    # Whole-batch pre-check before writing anything.
    problem = _reject_unsafe_ids(items)
    if problem is not None:
        return problem
    seen = set()
    for item in items:
        rid = item["record"].get("record_id")
        if isinstance(rid, str):
            if rid in seen:
                print("ERROR duplicate-record-id")
                return 2
            seen.add(rid)
    exit_code = 0
    planned = []
    for item in items:
        rid = item["record"].get("record_id")
        label = _label(item["record"], item["path"])
        if item["errors"]:
            rule, field = item["errors"][0]
            print(f"FAIL {display_path(item['path'])} {rule} {field}")
            exit_code = 1
            continue
        status, detail = evaluate(item["record"], config, languages, names)
        print(f"{status} {label} {detail}".rstrip())
        if status == "BUILD":
            stem = safe_stem(rid)
            if stem is None:
                print(f"ERROR unsafe-record-id {item['path']} record_id")
                return 2
            planned.append((item, stem, detail))
    if exit_code == 1:
        return 1

    out = Path(args.out)
    problem = _prepare_out_dir(out)
    if problem is not None:
        print(f"ERROR {problem} {out}")
        return 2
    targets = [out / "build.tsv"]
    for _item, stem, _detail in planned:
        targets.append(out / f"{stem}.json")
        targets.append(out / f"{stem}.zip")
    for target in targets:
        if target.exists():
            print(f"ERROR output-exists {target.name}")
            return 2

    # Project everything before writing anything.
    payloads = []
    for item, stem, _detail in planned:
        try:
            payload, related_skipped = project(item["record"], config, languages)
        except ValueError as exc:
            print(f"FAIL {_label(item['record'], item['path'])} {exc}")
            return 1
        payloads.append((item, stem, payload, related_skipped))

    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    config_hex = sha256_bytes(config_bytes)
    schema_hex = sha256_bytes(schema_bytes)
    languages_hex = sha256_bytes(languages_bytes)
    names_hex = sha256_bytes(names_bytes) if names_bytes else "-"
    written = []
    rows = []
    try:
        for item, stem, payload, related_skipped in payloads:
            body = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
            json_path = out / f"{stem}.json"
            body_hex = _write_file(json_path, body)
            written.append(json_path.name)
            empty = out / f"{stem}.zip"
            tmp_zip = None
            try:
                with tempfile.NamedTemporaryFile(dir=str(out), prefix=".tmp-", delete=False) as handle:
                    tmp_zip = Path(handle.name)
                with zipfile.ZipFile(tmp_zip, "w"):
                    pass
                os.chmod(tmp_zip, 0o600)
                try:
                    os.link(tmp_zip, empty)
                except FileExistsError:
                    raise FileExistsError(errno.EEXIST, "target exists", str(empty))
            finally:
                if tmp_zip is not None and tmp_zip.exists():
                    tmp_zip.unlink()
            written.append(empty.name)
            rows.append(
                (
                    stamp,
                    item["record"]["record_id"],
                    "BUILD",
                    f"related_skipped={related_skipped}",
                    sha256_bytes(item["raw"]),
                    config_hex,
                    names_hex,
                    schema_hex,
                    languages_hex,
                    body_hex,
                )
            )
        for item in items:
            label = _label(item["record"], item["path"])
            if item["errors"]:
                continue
            status, detail = evaluate(item["record"], config, languages, names)
            if status == "SKIP":
                rows.append(
                    (
                        stamp,
                        label,
                        "SKIP",
                        detail,
                        sha256_bytes(item["raw"]),
                        config_hex,
                        names_hex,
                        schema_hex,
                        languages_hex,
                        "-",
                    )
                )
        lines = ["\t".join(["timestamp", "record_id", "status", "detail", "source_sha256",
                             "config_sha256", "names_sha256", "schema_sha256",
                             "languages_sha256", "output_sha256"])]
        lines.extend("\t".join(row) for row in rows)
        tsv_path = out / "build.tsv"
        _write_file(tsv_path, ("\n".join(lines) + "\n").encode("utf-8"))
        written.append(tsv_path.name)
    except FileExistsError as exc:
        # A target appeared after the pre-check; its bytes are kept.
        for name in written:
            print(f"PARTIAL {name}")
        print(f"ERROR output-exists {Path(str(exc.filename)).name}")
        return 2
    except OSError:
        for name in written:
            print(f"PARTIAL {name}")
        print("ERROR write-failed")
        return 2
    for name in written:
        print(f"WROTE {name}")
    return 0


def run(argv=None):
    parser = argparse.ArgumentParser(description="Check or build Dataverse citation JSON offline.")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checks.")
    sub = parser.add_subparsers(dest="command")
    check_p = sub.add_parser("check", help="Evaluate records without writing files.")
    check_p.add_argument("--collection", required=True)
    check_p.add_argument("--languages", default=str(DEFAULT_LANGUAGES))
    check_p.add_argument("records", nargs="+")
    build_p = sub.add_parser("build", help="Write Dataverse JSON plus empty ZIPs.")
    build_p.add_argument("--collection", required=True)
    build_p.add_argument("--languages", default=str(DEFAULT_LANGUAGES))
    build_p.add_argument("--out", required=True)
    build_p.add_argument("records", nargs="+")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.command == "check":
        return run_check(args)
    if args.command == "build":
        return run_build(args)
    parser.print_usage(sys.stderr)
    return 2


def _tool(args, cwd=None):
    return subprocess.run(
        [sys.executable, str(ROOT / "tools" / "imm2dataverse.py"), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd or ROOT),
    )


def self_test():
    """Check mapping, SKIP cases, config errors, exits and file handling."""
    failures = []

    def check(condition, label):
        if not condition:
            failures.append(label)
            print(f"SELFTEST-FAIL {label}")

    head, _, _tail = Path(__file__).read_text(encoding="utf-8").partition("\ndef self_test")
    lowered = head.lower()
    for token in (
        "urllib.request",
        "urllib3",
        "http.client",
        "http.server",
        "socket",
        "requests",
        "create-draft",
        "publish",
        "upload",
    ):
        check(token not in lowered, f"static-clean {token}")

    example_text = EXAMPLE_COLLECTION.read_text(encoding="utf-8")

    def config_variant(replacements):
        text = example_text
        for old, new in replacements:
            text = text.replace(old, new)
        return text

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        def write(name, content):
            path = tmp_path / name
            path.write_text(content, encoding="utf-8")
            return str(path)

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

        valid_path = write("valid.json", json.dumps(base_record()))
        coll_path = write("coll-ok.toml", example_text)

        # Configuration errors all end in exit 2 with a fixed reason.
        bad_configs = {
            "missing-section": "[collection]\ncode = \"X\"\n",
            "bad-pattern": config_variant([('record_id_pattern = "^[0-9]{4}-[0-9]{2}-[0-9]{2}_OHX_[0-9]{4}$"',
                                            'record_id_pattern = "(unclosed"')]),
            "both-licence-modes": config_variant([('names_file = ""',
                                                   'names_file = ""\ncustom_terms_of_use = "Custom terms"')]),
            "no-licence": config_variant([('license_name = "CC BY 4.0"\nlicense_uri = "http://creativecommons.org/licenses/by/4.0"',
                                           'license_name = ""\nlicense_uri = ""')]),
            "whitespace-licence": config_variant([('license_name = "CC BY 4.0"', 'license_name = "   "')]),
            "licence-plus-space-terms": config_variant([('names_file = ""',
                                                        'names_file = ""\ncustom_terms_of_use = " "')]),
            "licence-plus-numeric-terms": config_variant([('names_file = ""',
                                                          'names_file = ""\ncustom_terms_of_use = 7')]),
            "terms-plus-space-licence": config_variant([
                ('license_name = "CC BY 4.0"\nlicense_uri = "http://creativecommons.org/licenses/by/4.0"',
                 'license_name = "   "\nlicense_uri = ""\ncustom_terms_of_use = "Custom terms"')]),
            "incomplete-licence": config_variant([('license_uri = "http://creativecommons.org/licenses/by/4.0"',
                                                   'license_uri = ""')]),
            "export-consent-withheld": config_variant([('export_consent = ["public"]',
                                                        'export_consent = ["public", "withdrawn"]')]),
            "export-consent-unknown": config_variant([('export_consent = ["public"]',
                                                       'export_consent = ["public", "nope"]')]),
            "export-access-closed": config_variant([('export_access = ["open"]', 'export_access = ["closed"]')]),
            "agency-required": config_variant([('export_record_id = false', 'export_record_id = true'),
                                               ('other_id_agency = "Example Institute"', 'other_id_agency = ""')]),
            "non-bool-switch": config_variant([('export_record_id = false', 'export_record_id = "yes"')]),
            "unknown-subject": config_variant([('subject = ["Arts and Humanities"]', 'subject = ["No Such Field"]')]),
            "bad-email": config_variant([('email = "collection@example.org"', 'email = "not-an-email"')]),
            "missing-consent-values": config_variant([('consent_values = ["research-only", "teaching", "public", "embargoed"]\n', '')]),
            "synthetic-false-no-approval": config_variant([('synthetic = true', 'synthetic = false')]),
        }
        for label, text in bad_configs.items():
            path = write(f"coll-{label}.toml", text)
            proc = _tool(["check", "--collection", path, valid_path])
            check(proc.returncode == 2, f"config-error-exit-2 {label}")

        # A non-synthetic configuration without the approval data fails;
        # with approval data and a names file it evaluates.
        names_path = write("names.txt", "Harbor Master\n")
        approval_ok = config_variant([
            ('synthetic = true', 'synthetic = false'),
            ('names_file = ""', f'names_file = "{names_path}"'),
            ('[dataverse.contact]', '[approval]\nrole = "Collection steward"\ndate = "2026-10-01"\ndecision_ref = "SYN-2026-001"\n\n[dataverse.contact]'),
        ])
        approval_path = write("coll-approval.toml", approval_ok)
        proc = _tool(["check", "--collection", approval_path, valid_path])
        check(proc.returncode == 0, "config-approval-ok")

        # Missing export switches default to false; explicit non-booleans fail.
        no_switches = example_text.replace("export_record_id = false\n", "").replace(
            "export_interviewer = false\n", "")
        no_switches_path = write("coll-no-switches.toml", no_switches)
        proc = _tool(["check", "--collection", no_switches_path, valid_path])
        check(proc.returncode == 0, "config-missing-switches-default-false")
        out_switches = str(tmp_path / "out-switches")
        proc = _tool(["build", "--collection", no_switches_path, "--out", out_switches, valid_path])
        check(proc.returncode == 0, "build-missing-switches-exit-0")
        off_switches = json.loads(
            (tmp_path / "out-switches" / "DS_2025-01-01_OHX_0001.json").read_text(encoding="utf-8"))
        off_switch_names = {f["typeName"] for f in
                            off_switches["datasetVersion"]["metadataBlocks"]["citation"]["fields"]}
        check("contributor" not in off_switch_names and "otherId" not in off_switch_names,
              "mapping-missing-switches-off")

        # A real-mode configuration with zero usable name entries fails.
        bang_names = write("names-bang.txt", "!!!\n")
        bang_cfg = config_variant([
            ('synthetic = true', 'synthetic = false'),
            ('names_file = ""', f'names_file = "{bang_names}"'),
            ('[dataverse.contact]', '[approval]\nrole = "Collection steward"\ndate = "2026-10-01"\n'
             'decision_ref = "SYN-2026-001"\n\n[dataverse.contact]'),
        ])
        bang_path = write("coll-bang-names.toml", bang_cfg)
        proc = _tool(["check", "--collection", bang_path, valid_path])
        check(proc.returncode == 2, "config-unusable-names-exit-2")

        # Invalid related URLs are skipped and counted, never a traceback:
        # bad port, query, fragment, empty query, DOI with query.
        url_record = base_record(
            record_id="2025-01-01_OHX_5001",
            related_materials=[
                "https://doi.org:bad/10.5555/qa",
                "https://doi.org/10.5555/qa?x=1",
                "https://doi.org/10.5555/qa#page=2",
                "https://doi.org/10.5555/qa?",
                "doi:10.5555/qa?x=1",
                "https://doi.org/10.5555/qa",
            ],
        )
        url_path = write("urls.json", json.dumps(url_record))
        proc = _tool(["check", "--collection", coll_path, url_path])
        check(proc.returncode == 0 and "BUILD 2025-01-01_OHX_5001" in proc.stdout,
              "related-invalid-check-build")
        check("Traceback" not in proc.stdout and "Traceback" not in proc.stderr,
              "related-invalid-no-traceback")
        out_urls = str(tmp_path / "out-urls")
        proc = _tool(["build", "--collection", coll_path, "--out", out_urls, url_path])
        check(proc.returncode == 0, "related-invalid-build-exit-0")
        url_payload = json.loads(
            (tmp_path / "out-urls" / "DS_2025-01-01_OHX_5001.json").read_text(encoding="utf-8"))
        url_names = {f["typeName"]: f for f in
                     url_payload["datasetVersion"]["metadataBlocks"]["citation"]["fields"]}
        check(url_names["relatedMaterial"]["value"] == ["https://doi.org/10.5555/qa"],
              "related-invalid-admitted-only")
        url_tsv = (tmp_path / "out-urls" / "build.tsv").read_text(encoding="utf-8")
        check("related_skipped=5" in url_tsv, "related-invalid-skipped-count")

        # Percent-encoded blocked names in admitted URL paths are withheld.
        harbor_names = write("names-harbor.txt", "Harbor Master\n")
        harbor_cfg = config_variant([(f'names_file = ""', f'names_file = "{harbor_names}"'),
                                     ('allowed_hosts = ["doi.org"]',
                                      'allowed_hosts = ["doi.org", "example.org"]')])
        harbor_cfg_path = write("coll-harbor.toml", harbor_cfg)
        encoded_record = base_record(
            record_id="2025-01-01_OHX_5002",
            related_materials=["https://example.org/%48arbor%20%4daster.pdf"],
        )
        encoded_path = write("encoded.json", json.dumps(encoded_record))
        proc = _tool(["check", "--collection", harbor_cfg_path, encoded_path])
        check("SKIP 2025-01-01_OHX_5002 name-hit" in proc.stdout, "names-encoded-url-hit")

        # Control characters in ids stop the run before any output; the
        # diagnosis names the file and the field, never the value.
        with_collection_free = config_variant([(
            'record_id_pattern = "^[0-9]{4}-[0-9]{2}-[0-9]{2}_OHX_[0-9]{4}$"',
            'record_id_pattern = "^.*$"')])
        free_path = write("coll-free-pattern.toml", with_collection_free)
        ctrl_record = base_record(record_id="WALZ-1000\tQA\nSECOND")
        ctrl_path = write("ctrl.json", json.dumps(ctrl_record))
        out_ctrl = str(tmp_path / "out-ctrl")
        proc = _tool(["build", "--collection", free_path, "--out", out_ctrl, ctrl_path])
        check(proc.returncode == 2, "unsafe-id-exit-2")
        check("unsafe-record-id" in proc.stdout and "record_id" in proc.stdout,
              "unsafe-id-diagnosis")
        check("WALZ-1000\tQA" not in proc.stdout and "SECOND" not in proc.stdout.split("record_id")[0],
              "unsafe-id-no-label-leak")
        check(not (tmp_path / "out-ctrl").exists(), "unsafe-id-no-output")

        # An invalid id without control characters never becomes the
        # label either: FAIL names the file, the rule and the field.
        marker_path = write("marker.json", json.dumps(base_record(
            record_id="SYNTHETIC_PRIVATE_MARKER")))
        proc = _tool(["check", "--collection", coll_path, marker_path])
        check(proc.returncode == 1, "fail-marker-exit-1")
        check(len(proc.stdout.splitlines()) == 1
              and "FAIL" in proc.stdout and "R7" in proc.stdout
              and "record_id" in proc.stdout and "marker.json" in proc.stdout,
              "fail-marker-rule-path")
        check("SYNTHETIC_PRIVATE_MARKER" not in proc.stdout
              and "SYNTHETIC_PRIVATE_MARKER" not in proc.stderr,
              "fail-marker-no-value")
        out_marker = str(tmp_path / "out-marker")
        proc = _tool(["build", "--collection", coll_path, "--out", out_marker, marker_path])
        check(proc.returncode == 1, "fail-marker-build-exit-1")
        check("SYNTHETIC_PRIVATE_MARKER" not in proc.stdout
              and "SYNTHETIC_PRIVATE_MARKER" not in proc.stderr,
              "fail-marker-build-no-value")
        check(not (tmp_path / "out-marker").exists(), "fail-marker-build-no-output")
        proc = _tool(["check", "--collection", coll_path, valid_path])
        check(proc.returncode == 0 and "BUILD 2025-01-01_OHX_0001" in proc.stdout,
              "fail-marker-valid-keeps-label")

        # A target that appears after the pre-check is kept, not replaced.
        foreign_dir = tmp_path / "out-foreign"
        foreign_dir.mkdir()
        foreign_target = foreign_dir / "DS_2025-01-01_OHX_0001.json"
        foreign_target.write_bytes(b'{"foreign": true}')
        try:
            _write_file(foreign_target, b'{"own": true}')
            check(False, "exclusive-place-raises")
        except FileExistsError:
            pass
        check(foreign_target.read_bytes() == b'{"foreign": true}', "exclusive-foreign-kept")

        # Byte snapshot: parsing and hashing use the bytes read first.
        snap_coll = write("coll-snap.toml", example_text)
        snap_raw = Path(snap_coll).read_bytes()
        Path(snap_coll).write_text(
            example_text.replace("export_interviewer = false", "export_interviewer = true"),
            encoding="utf-8")
        snap_config = load_config(snap_coll, snap_raw)
        check(snap_config["export_interviewer"] is False, "snapshot-parses-first-bytes")
        check(hashlib.sha256(snap_raw).hexdigest() == hashlib.sha256(example_text.encode("utf-8")).hexdigest(),
              "snapshot-hashes-first-bytes")

        # Mapping: every table row with multiple and typeClass.
        full = base_record(
            record_id="2025-06-01_OHX_0042",
            interview_date="2025-06-01",
            interviewer="Jane Smith (0000-0001-2345-6789); John Doe",
            languages=["deu", "ltz"],
            spatial="Esch-sur-Alzette",
            keywords=["work", "migration"],
            related_materials=[
                "https://doi.org/10.5555/imm-example-0042",
                "https://example.org/files/transcript.pdf?download=1#page=2",
                "http://example.org/plain",
                "https://elsewhere.org/file.pdf",
                "https://user@example.org/file.pdf",
            ],
        )
        full_path = write("full.json", json.dumps(full))
        on_switches = config_variant([
            ('export_record_id = false', 'export_record_id = true'),
            ('export_interviewer = false', 'export_interviewer = true'),
            ('allowed_hosts = ["doi.org"]', 'allowed_hosts = ["doi.org", "example.org"]'),
        ])
        on_path = write("coll-on.toml", on_switches)
        out1 = str(tmp_path / "out1")
        proc = _tool(["build", "--collection", on_path, "--out", out1, full_path])
        check(proc.returncode == 0, "build-switches-exit-0")
        ds_path = tmp_path / "out1" / "DS_2025-06-01_OHX_0042.json"
        payload = json.loads(ds_path.read_text(encoding="utf-8"))
        check(set(payload) == {"datasetVersion"}, "mapping-single-root")
        version = payload["datasetVersion"]
        check("license" in version and "termsOfUse" not in version, "mapping-licence-json")
        check(version["license"] == {"name": "CC BY 4.0", "uri": "http://creativecommons.org/licenses/by/4.0"},
              "mapping-licence-values")
        by_name = {f["typeName"]: f for f in version["metadataBlocks"]["citation"]["fields"]}
        check(by_name["title"]["multiple"] is False and by_name["title"]["typeClass"] == "primitive",
              "mapping-title")
        desc = by_name["dsDescription"]
        check(desc["multiple"] is True and desc["typeClass"] == "compound", "mapping-description")
        check(desc["value"] == [{"dsDescriptionValue": {
            "typeName": "dsDescriptionValue", "multiple": False,
            "typeClass": "primitive", "value": full["abstract"]}}], "mapping-description-value")
        doc = by_name["dateOfCollection"]
        check(doc["multiple"] is True and doc["typeClass"] == "compound", "mapping-date")
        check(doc["value"] == [{"dateOfCollectionStart": {
            "typeName": "dateOfCollectionStart", "multiple": False, "typeClass": "primitive",
            "value": "2025-06-01"}, "dateOfCollectionEnd": {
            "typeName": "dateOfCollectionEnd", "multiple": False, "typeClass": "primitive",
            "value": "2025-06-01"}}], "mapping-date-value")
        lang = by_name["language"]
        check(lang["multiple"] is True and lang["typeClass"] == "controlledVocabulary", "mapping-language")
        check(lang["value"] == ["German", "Luxembourgish, Letzeburgesch"], "mapping-language-order")
        kw = by_name["keyword"]
        check(kw["multiple"] is True and kw["typeClass"] == "compound", "mapping-keyword")
        check([c["keywordValue"]["value"] for c in kw["value"]] == ["work", "migration"],
              "mapping-keyword-values")
        contrib = by_name["contributor"]
        check(contrib["multiple"] is True and contrib["typeClass"] == "compound", "mapping-contributor")
        check([c["contributorName"]["value"] for c in contrib["value"]] == ["Jane Smith", "John Doe"],
              "mapping-contributor-split-orcid")
        check(all(c["contributorType"]["value"] == "Data Collector"
                  and c["contributorType"]["typeClass"] == "controlledVocabulary"
                  for c in contrib["value"]), "mapping-contributor-type")
        check(by_name["productionPlace"]["value"] == ["Esch-sur-Alzette"]
              and by_name["productionPlace"]["multiple"] is True, "mapping-place")
        other = by_name["otherId"]
        check(other["value"] == [{"otherIdAgency": {
            "typeName": "otherIdAgency", "multiple": False, "typeClass": "primitive",
            "value": "Example Institute"}, "otherIdValue": {
            "typeName": "otherIdValue", "multiple": False, "typeClass": "primitive",
            "value": "2025-06-01_OHX_0042"}}], "mapping-other-id")
        rel = by_name["relatedMaterial"]
        check(rel["multiple"] is True and rel["typeClass"] == "primitive", "mapping-related")
        # The query/fragment URL is skipped, not truncated to host+path.
        check(rel["value"] == ["https://doi.org/10.5555/imm-example-0042"],
              "mapping-related-normalized")
        tsv1 = (tmp_path / "out1" / "build.tsv").read_text(encoding="utf-8").splitlines()
        check(any(row.split("\t")[1] == "2025-06-01_OHX_0042"
                  and "related_skipped=4" in row for row in tsv1[1:]),
              "mapping-related-skipped-count")
        check(all(len(line.split("\t")) == 10 for line in tsv1), "tsv-ten-columns")
        check(by_name["author"]["value"] == [{"authorName": {
            "typeName": "authorName", "multiple": False, "typeClass": "primitive",
            "value": "Example Project"}, "authorAffiliation": {
            "typeName": "authorAffiliation", "multiple": False, "typeClass": "primitive",
            "value": "Example Institute"}}], "mapping-author")
        check(by_name["datasetContact"]["value"] == [{"datasetContactName": {
            "typeName": "datasetContactName", "multiple": False, "typeClass": "primitive",
            "value": "Example collection contact"}, "datasetContactEmail": {
            "typeName": "datasetContactEmail", "multiple": False, "typeClass": "primitive",
            "value": "collection@example.org"}}], "mapping-contact")
        check(by_name["subject"]["typeClass"] == "controlledVocabulary"
              and by_name["subject"]["value"] == ["Arts and Humanities"], "mapping-subject")
        check(by_name["kindOfData"]["value"] == ["Oral history interview"]
              and by_name["kindOfData"]["multiple"] is True, "mapping-kind")
        check("contributor" in by_name and "otherId" in by_name, "mapping-switches-on")

        # Two configured authors share one outer author compound.
        two_authors = on_switches + '\n[[dataverse.author]]\nname = "Second Author"\naffiliation = "Second Institute"\n'
        two_path = write("coll-two-authors.toml", two_authors)
        out1b = str(tmp_path / "out1b")
        proc = _tool(["build", "--collection", two_path, "--out", out1b, valid_path])
        check(proc.returncode == 0, "build-two-authors-exit-0")
        two = json.loads((tmp_path / "out1b" / "DS_2025-01-01_OHX_0001.json").read_text(encoding="utf-8"))
        authors = [f for f in two["datasetVersion"]["metadataBlocks"]["citation"]["fields"]
                   if f["typeName"] == "author"]
        check(len(authors) == 1 and len(authors[0]["value"]) == 2, "mapping-author-single-compound")
        check([c["authorName"]["value"] for c in authors[0]["value"]] == ["Example Project", "Second Author"],
              "mapping-author-order")
        check(authors[0]["value"][1]["authorAffiliation"]["value"] == "Second Institute",
              "mapping-author-affiliation")

        # Switches off: no contributor, no otherId. Empty keywords omitted.
        minimal = base_record(record_id="2025-06-02_OHX_0043")
        minimal_path = write("minimal.json", json.dumps(minimal))
        out2 = str(tmp_path / "out2")
        proc = _tool(["build", "--collection", coll_path, "--out", out2, minimal_path])
        check(proc.returncode == 0, "build-switches-off-exit-0")
        off = json.loads((tmp_path / "out2" / "DS_2025-06-02_OHX_0043.json").read_text(encoding="utf-8"))
        off_names = {f["typeName"] for f in off["datasetVersion"]["metadataBlocks"]["citation"]["fields"]}
        check("contributor" not in off_names and "otherId" not in off_names, "mapping-switches-off")
        check("keyword" not in off_names, "mapping-keyword-omitted")

        # Custom terms mode: termsOfUse present, licence absent.
        terms_cfg = config_variant([('license_name = "CC BY 4.0"\nlicense_uri = "http://creativecommons.org/licenses/by/4.0"',
                                     'license_name = ""\nlicense_uri = ""\ncustom_terms_of_use = "Custom terms"')])
        terms_path = write("coll-terms.toml", terms_cfg)
        out3 = str(tmp_path / "out3")
        proc = _tool(["build", "--collection", terms_path, "--out", out3, minimal_path])
        check(proc.returncode == 0, "build-terms-exit-0")
        terms_v = json.loads((tmp_path / "out3" / "DS_2025-06-02_OHX_0043.json").read_text(encoding="utf-8"))["datasetVersion"]
        check(terms_v.get("termsOfUse") == "Custom terms" and "license" not in terms_v, "mapping-terms-json")

        # Every SKIP reason fires deterministically.
        table = load_languages(str(DEFAULT_LANGUAGES))
        check("zzz" not in table, "skip-unmapped-code-free")
        skip_cases = [
            ("withdrawn", base_record(record_id="2025-01-01_OHX_1001", consent_status="withdrawn",
                                      accessRights="closed"), "withdrawn"),
            ("closed", base_record(record_id="2025-01-01_OHX_1002", accessRights="closed"), "access-closed"),
            ("embargoed", base_record(record_id="2025-01-01_OHX_1003",
                                       consent_status="embargoed"), "embargoed"),
            ("consent", base_record(record_id="2025-01-01_OHX_1004",
                                     consent_status="teaching"), "consent-not-exported"),
            ("access", base_record(record_id="2025-01-01_OHX_1005",
                                    accessRights="restricted"), "access-not-exported"),
            ("abstract", base_record(record_id="2025-01-01_OHX_1006"), "abstract-missing"),
            ("names", base_record(record_id="2025-01-01_OHX_1007",
                                   title="Notes by the Harbor Master"), "name-hit"),
            ("language", base_record(record_id="2025-01-01_OHX_1008", language="zzz"), "language-unmapped"),
        ]
        skip_paths = []
        for label, record, _reason in skip_cases:
            if label == "abstract":
                record.pop("abstract")
            path = write(f"skip-{label}.json", json.dumps(record))
            skip_paths.append(path)
        names_cfg = config_variant([(f'names_file = ""', f'names_file = "{names_path}"')])
        names_cfg_path = write("coll-names.toml", names_cfg)
        proc = _tool(["check", "--collection", names_cfg_path, *skip_paths])
        check(proc.returncode == 0, "skip-batch-exit-0")
        lines = proc.stdout.splitlines()
        for (_label, record, reason) in skip_cases:
            check(f"SKIP {record['record_id']} {reason}" in lines, f"skip-reason {reason}")
        out4 = str(tmp_path / "out4")
        proc = _tool(["build", "--collection", names_cfg_path, "--out", out4, *skip_paths])
        check(proc.returncode == 0, "skip-build-exit-0")
        check(sorted(p.name for p in (tmp_path / "out4").iterdir()) == ["build.tsv"], "skip-build-tsv-only")

        # Duplicate ids and existing targets abort before any new output.
        dup_a = write("dup-a.json", json.dumps(base_record(record_id="2025-01-01_OHX_2001")))
        dup_b = write("dup-b.json", json.dumps(base_record(record_id="2025-01-01_OHX_2001")))
        out5 = str(tmp_path / "out5")
        proc = _tool(["build", "--collection", coll_path, "--out", out5, dup_a, dup_b])
        check(proc.returncode == 2, "duplicate-exit-2")
        check(not (tmp_path / "out5").exists(), "duplicate-no-output")
        out6 = str(tmp_path / "out6")
        proc = _tool(["build", "--collection", coll_path, "--out", out6, valid_path])
        check(proc.returncode == 0, "rebuild-first-ok")
        before = {p.name: p.read_bytes() for p in (tmp_path / "out6").iterdir()}
        proc = _tool(["build", "--collection", coll_path, "--out", out6, valid_path])
        check(proc.returncode == 2, "existing-target-exit-2")
        after = {p.name: p.read_bytes() for p in (tmp_path / "out6").iterdir()}
        check(before == after, "existing-target-untouched")

        # Invalid records fail the batch before writing; sources stay equal.
        broken_rec = base_record(record_id="2025-01-01_OHX_3001", title="   ")
        broken_path = write("broken-record.json", json.dumps(broken_rec))
        before_bytes = Path(valid_path).read_bytes()
        out7 = str(tmp_path / "out7")
        proc = _tool(["build", "--collection", coll_path, "--out", out7, valid_path, broken_path])
        check(proc.returncode == 1, "invalid-batch-exit-1")
        check(not (tmp_path / "out7").exists(), "invalid-batch-no-output")
        check(Path(valid_path).read_bytes() == before_bytes, "sources-byte-identical")

        # ZIP files are valid and empty; hashes match; builds are identical.
        out8a = str(tmp_path / "out8a")
        out8b = str(tmp_path / "out8b")
        proc = _tool(["build", "--collection", on_path, "--out", out8a, full_path])
        check(proc.returncode == 0, "determinism-first-ok")
        proc = _tool(["build", "--collection", on_path, "--out", out8b, full_path])
        check(proc.returncode == 0, "determinism-second-ok")
        stem = "DS_2025-06-01_OHX_0042"
        body_a = (tmp_path / "out8a" / f"{stem}.json").read_bytes()
        body_b = (tmp_path / "out8b" / f"{stem}.json").read_bytes()
        check(body_a == body_b, "determinism-identical-json")
        with zipfile.ZipFile(tmp_path / "out8a" / f"{stem}.zip") as zf:
            check(zf.infolist() == [], "zip-zero-entries")
        tsv_lines = (tmp_path / "out8a" / "build.tsv").read_text(encoding="utf-8").splitlines()
        check(tsv_lines[0].split("\t") == ["timestamp", "record_id", "status", "detail", "source_sha256",
                                            "config_sha256", "names_sha256", "schema_sha256",
                                            "languages_sha256", "output_sha256"], "tsv-header")
        row = tsv_lines[1].split("\t")
        check(row[1] == "2025-06-01_OHX_0042" and row[2] == "BUILD", "tsv-build-row")
        check(row[4] == hashlib.sha256(Path(full_path).read_bytes()).hexdigest(), "tsv-source-hash")
        check(row[9] == hashlib.sha256(body_a).hexdigest(), "tsv-output-hash")
        check(row[9] == hashlib.sha256((tmp_path / "out8b" / f"{stem}.json").read_bytes()).hexdigest(),
              "tsv-output-hash-stable")
        out_dir = tmp_path / "out8a"
        check(stat.S_IMODE(out_dir.stat().st_mode) == 0o700, "out-dir-700")
        for name in (f"{stem}.json", f"{stem}.zip", "build.tsv"):
            check(stat.S_IMODE((out_dir / name).stat().st_mode) == 0o600, f"out-file-600 {name}")
        odd = tmp_path / "out-odd"
        odd.mkdir()
        os.chmod(odd, 0o755)
        proc = _tool(["build", "--collection", coll_path, "--out", str(odd), valid_path])
        check(proc.returncode == 2, "out-bad-mode-exit-2")
        check(list(odd.iterdir()) == [], "out-bad-mode-untouched")

        # No blocked names, internal references or source texts leak.
        secret = base_record(
            record_id="2025-01-01_OHX_4001",
            title="Evening with the Harbor Master",
            interviewee_display="Harbor Master",
            governance_ref="urn:example:governance:secret-1",
        )
        secret_path = write("secret.json", json.dumps(secret))
        out9 = str(tmp_path / "out9")
        proc = _tool(["build", "--collection", names_cfg_path, "--out", out9, secret_path])
        check(proc.returncode == 0, "leak-batch-skipped")
        logged = (tmp_path / "out9" / "build.tsv").read_text(encoding="utf-8")
        for token in ("Harbor Master", "harbor", "urn:example:governance:secret-1"):
            check(token not in logged and token not in proc.stdout and token not in proc.stderr,
                  f"no-leak {token}")

        # Exit codes: missing source and missing collection are exit 2.
        proc = _tool(["check", "--collection", coll_path, str(tmp_path / "absent.json")])
        check(proc.returncode == 2, "missing-source-exit-2")
        proc = _tool(["check", "--collection", str(tmp_path / "absent.toml"), valid_path])
        check(proc.returncode == 2, "missing-collection-exit-2")
        proc = _tool(["build", "--collection", coll_path, "--out", str(tmp_path / "out10"), valid_path])
        check(proc.returncode == 0 and "WROTE build.tsv" in proc.stdout, "build-reports-files")

    if failures:
        print(f"SELFTEST {len(failures)} failures")
        return 1
    print("SELFTEST OK: mapping, SKIP cases, config errors, exits and files checked.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
