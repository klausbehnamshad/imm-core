# Implementing IMM-Core: export rules, collection configuration, tool calls

This page is for collection operators. It states the export rules behind
the tools, the shape of a collection configuration, and the exact tool
calls. Everything here works offline on local files with synthetic data.
The only collection configuration in this repository,
`tools/examples/collection-OHX.toml`, is invented; real configurations,
name lists and outputs live outside the repository.

## Export rules

- Lists stay JSON arrays. A serialised list inside a string (for example
  `"['a', 'b']"`) is a rule violation (R3), not a second encoding.
- Empty required content means no export. A blank string passes the
  schema shape but fails rule R8; a missing or blank `abstract` withholds
  the Dataverse projection (SKIP `abstract-missing`).
- The `record_id` is assigned once by the system that holds the
  collection. Exports carry it unchanged and never generate a new one;
  reimport never renumbers. Only `; ` separates persons in `interviewer`
  and `interviewee_display`; a comma alone proves no person list (R5
  warns only). `interviewee_display` is never filled automatically from
  a real name.
- Language codes stay ISO 639-3 in the record. BCP 47 (shortest tag) is
  used only at the rim: WebVTT, player, Schema.org, Dublin Core. The
  Dataverse projection maps codes to the exact English names of the
  pinned table.
- `timecoded_segments` holds chapter marks: labels describe a section,
  never a subtitle line. Subtitles and transcripts go as WebVTT per
  language via `related_materials`. Timecodes with frames are truncated
  to seconds by the producing system, never repaired by the checker.
  Minutes and seconds range 00–59.
- Consumers that validate with the raw schema only MUST still enforce
  the cross-field rule: when `languages` is present it contains
  `language`. The schema cannot express it; `tools/validate.py` (R2) is
  the reference.

## Collection configuration

A collection keeps its permitted consent values and its identifier
pattern in tool configuration, not in the Core. Layout (TOML):

- `[collection]`: `code`, `name`, `synthetic` (explicitly `true` or
  `false`), `record_id_pattern` (must compile; an existing collection
  keeps its pattern, for example `^WALZ-[0-9]{4}$`), `consent_values`
  (non-empty; always usable with `withdrawn` at the checker).
- `[dataverse]`: `other_id_agency`, `subject` (the 14 pinned citation
  values), `kind_of_data`, `export_consent` (subset of
  `consent_values`, never `withdrawn` or `embargoed`),
  `export_access` (`open` and/or `restricted`, never `closed`;
  missing means `open` only), `export_record_id` and
  `export_interviewer` (real booleans, missing means `false`),
  exactly one licence mode (`license_name` plus `license_uri`, or
  `custom_terms_of_use`), `allowed_hosts`, `names_file` (empty means
  no list), one or more `author` entries, one `contact` with a role or
  project address. The checked licence mode is passed on to the
  projection; a whitespace or non-string leftover in the unused
  alternative is a configuration error (exit 2), never a silent choice.
- `[approval]` (only when `synthetic = false`): `role`, ISO `date`,
  `decision_ref`, plus a present, readable, non-empty `names_file`.
  The block documents the institutional decision on the full
  projection, consent selection and licence; it is no checked
  signature proof. No real configuration is created or approved in
  this release.

Which licence fits is decided by the responsible body from the
existing rights; there is no default licence fallback. The example
licence in the synthetic configuration is no recommendation for real
interviews, and a synthetic configuration must never trigger a real
write (the tools of this release contain no write path at all).

## Tool calls

Check records (schema plus rules R1–R8):

```bash
python tools/validate.py RECORD.json [RECORD.json ...]
python tools/validate.py --collection tools/examples/collection-OHX.toml RECORD.json
python tools/validate.py --self-test
```

Exit 0: every record valid (warnings allowed). Exit 1: at least one
invalid record. Exit 2: configuration, file, JSON reading or tool run
not evaluable. Output lines name only the file, the rule and the
field path. `--self-test` separates schema cases (`tests/invalid/`)
from rule-only cases (`tests/invalid-rules/`) and checks the real CLI
exit codes.

Project to Dataverse citation JSON (check first, then optionally build):

```bash
python tools/imm2dataverse.py check --collection FILE.toml RECORD.json [RECORD.json ...]
python tools/imm2dataverse.py build --collection FILE.toml --out DIR RECORD.json [RECORD.json ...]
python tools/imm2dataverse.py --self-test
```

`check` writes nothing: BUILD (projectable), SKIP (fixed reason),
FAIL (field path). `build` pre-checks the whole batch and aborts
before writing on invalid records, duplicate ids, unusable
configuration, unsafe file names or existing targets. Unsafe names
include control characters (tab, CR, LF and others) in `record_id`;
that diagnosis names the input file and the field path, never the
value. Per BUILD record it writes `DS_<record_id>.json` (single root
`datasetVersion`) and a valid ZIP with zero entries, plus the private
`build.tsv` log (timestamp, record id, status, detail, SHA-256 of
source record, configuration, names file, schema, language table and
generated JSON). Every input file is read once and parsed and hashed
from those same bytes. JSON, ZIP and TSV are staged fully and placed
exclusively: a target that appeared after the pre-check stops the run
and keeps its bytes. The output directory gets mode 700, files get
mode 600; a present directory with other modes stops the run.
Related entries with query or fragment parts (including empty ones),
invalid ports or user information are skipped and counted, never
truncated. A `synthetic = false` configuration needs at least one
usable name entry. Exit 0 covers a fully withheld batch; exit 1
means an invalid record; exit 2 means an unevaluable source or
configuration, duplicate id, unsafe name, existing output or write
error.

## Release packaging

The release bundle carries the model, the tools with their fixtures,
and the existing licence notes, including the bundled Dataverse source
licence `tools/data/LICENSE-dataverse.md`:

```bash
zip -r imm-core-v1.2.0.zip \
  README.md LICENSE CITATION.cff CHANGELOG.md \
  tap/core.csv schema/core.schema.json \
  vocabs/ profiles/ crosswalks/ \
  examples/core-generic.json examples/core-oral-history.json examples/core-minimal.json \
  methodological-positions/ docs/ \
  tools/ scripts/ tests/ \
  -x '*/__pycache__/*'
```

Build the archive exactly from the accepted Git state, never from a
working tree with generated files; generated `__pycache__` directories
stay out of the bundle. `.zenodo.json` and the publishing guide stay
out of the bundle. The detailed release steps (reserve the DOI before
freezing the source state, fix the metadata before building the
archive, version field, dates, tag) are in
`ZENODO-PUBLISHING-GUIDE.md`; the release itself is a separate task
and is not executed here.
