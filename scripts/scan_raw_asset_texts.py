import argparse
import csv
import re
from bisect import bisect_left
from collections import Counter, defaultdict
from pathlib import Path


ASCII_RE = re.compile(rb"[\x20-\x7e]{3,}")
UTF16LE_RE = re.compile(rb"(?:[\x09\x0a\x0d\x20-\x7e]\x00|[\x14]\x20){3,}")
GUID_RE = re.compile(r"^[0-9A-F]{32}$")
VISIBLE_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9'.,:;!?(){}\[\]<>/\\ \n\r\t+-]*")

INTERNAL_PREFIXES = (
    "/Game/",
    "/Script/",
    "/Engine/",
    "BP_",
    "BPC_",
    "DA_",
    "DT_",
    "E_",
    "F_",
    "K2Node_",
    "CallFunc_",
    "Temp_",
    "UberGraph",
    "Default__",
    "SKEL_",
    "REINST_",
)

INTERNAL_SUBSTRINGS = (
    "StructProperty",
    "ObjectProperty",
    "NameProperty",
    "TextProperty",
    "ArrayProperty",
    "BoolProperty",
    "FloatProperty",
    "IntProperty",
    "ByteProperty",
    "SoftObjectProperty",
    "MulticastInlineDelegateProperty",
    "EdGraph",
    "Blueprint",
    "GameplayTag",
    "GameplayCue",
    "PersistentLevel",
    "DefaultSceneRoot",
)


def iter_ascii_strings(data):
    for match in ASCII_RE.finditer(data):
        text = match.group().decode("utf-8", "replace")
        yield match.start(), text, "ascii"


def iter_utf16le_strings(data):
    for match in UTF16LE_RE.finditer(data):
        text = match.group().decode("utf-16le", "replace")
        yield match.start(), text, "utf16le"


def iter_strings(data):
    yield from iter_ascii_strings(data)
    yield from iter_utf16le_strings(data)


def looks_internal(text):
    if not text:
        return True
    if GUID_RE.match(text):
        return True
    if any(text.startswith(prefix) for prefix in INTERNAL_PREFIXES):
        return True
    if any(part in text for part in INTERNAL_SUBSTRINGS):
        return True
    if "\\" in text or "/" in text:
        return True
    if "_" in text and " " not in text:
        return True
    if "." in text and " " not in text:
        return True
    if text.isupper() and "_" in text:
        return True
    return False


def looks_visible_text(text):
    if looks_internal(text):
        return False
    stripped = text.strip()
    if len(stripped) < 3:
        return False
    if not VISIBLE_WORD_RE.fullmatch(stripped):
        return False
    if " " in stripped:
        return True
    if stripped in {"Start", "Finish", "None", "Metric", "Imperial", "Measurement"}:
        return True
    if stripped.istitle() and len(stripped) >= 4:
        return True
    return False


def nearby_guid(guid_strings, offset):
    if not guid_strings:
        return ""
    offsets = [item[0] for item in guid_strings]
    index = bisect_left(offsets, offset)
    candidate_index = index - 1
    if candidate_index < 0:
        return ""
    guid_offset, guid = guid_strings[candidate_index]
    if 0 <= offset - guid_offset <= 512:
        return guid
    return ""


def scan(root, targets):
    target_set = set(targets)
    rows = []
    counts = Counter()
    examples = defaultdict(list)
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in {".uasset", ".uexp", ".umap"}:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        strings = list(iter_strings(data))
        guid_strings = [(offset, text) for offset, text, _ in strings if GUID_RE.match(text)]
        visible = []
        string_kind = {}
        for offset, text, kind in strings:
            if text in target_set or looks_visible_text(text):
                visible.append((offset, text))
                string_kind[offset] = kind
        if not visible:
            continue
        guid_by_offset = {offset: nearby_guid(guid_strings, offset) for offset, _ in visible}
        for offset, text in visible:
            counts[text] += 1
            if len(examples[text]) < 8:
                examples[text].append(str(path))
            rows.append(
                {
                    "text": text,
                    "source_file": str(path),
                    "offset": offset,
                    "nearby_guid": guid_by_offset[offset],
                    "encoding": string_kind.get(offset, ""),
                    "is_requested_target": "yes" if text in target_set else "",
                }
            )
    return rows, counts, examples


def write_reports(rows, counts, examples, detailed_out, summary_out):
    detailed_out.parent.mkdir(parents=True, exist_ok=True)
    with detailed_out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "text",
                "source_file",
                "offset",
                "nearby_guid",
                "encoding",
                "is_requested_target",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    with summary_out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["text", "occurrences", "example_files"],
        )
        writer.writeheader()
        for text, count in counts.most_common():
            writer.writerow(
                {
                    "text": text,
                    "occurrences": count,
                    "example_files": " | ".join(examples[text]),
                }
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        default="extract/iostore_unpacked_probe/IntoTheRadius2/Content/ITR2",
    )
    parser.add_argument(
        "--detailed-out",
        default="build/reports/raw_asset_visible_text_detailed.csv",
    )
    parser.add_argument(
        "--summary-out",
        default="build/reports/raw_asset_visible_text_summary.csv",
    )
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        help="Visible text that must be included even if it looks generic.",
    )
    args = parser.parse_args()

    rows, counts, examples = scan(Path(args.root), args.target)
    write_reports(
        rows,
        counts,
        examples,
        Path(args.detailed_out),
        Path(args.summary_out),
    )
    print(f"wrote {len(rows)} detailed rows")
    print(f"wrote {len(counts)} unique visible text candidates")


if __name__ == "__main__":
    main()
