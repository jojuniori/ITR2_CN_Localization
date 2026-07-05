import argparse
import csv
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MASTER_CSV = ROOT / "translation" / "ITR2_CN_master.csv"
REPORT_DIR = ROOT / "build" / "reports"

NOISE_RE = re.compile(r"^[A-Za-z0-9_./\\:()'\"{}\[\],+*<>=!? -]{3,}$")
GUID_RE = re.compile(r"^[0-9A-F]{32}$")

IGNORE_PATTERNS = (
    "CallFunc_",
    "K2Node_",
    "Default__",
    "UberGraph",
    "Property",
    "Blueprint",
    "Component",
    "GameTraceChannel",
    "EngineTraceChannel",
    "WorldDynamic",
    "WorldStatic",
    "ObjectProperty",
    "StructProperty",
    "BoolProperty",
    "IntProperty",
    "FloatProperty",
    "ByteProperty",
    "ArrayProperty",
    "Delegate",
    "ExecuteUbergraph",
    "Temp_",
    "ReturnValue",
    "None",
)

SINGLE_WORD_UI_LABELS = {
    "Finish",
    "Grip",
    "Imperial",
    "Measurement",
    "Metric",
    "Pass",
    "Show",
    "Skip",
    "Start",
    "Trigger",
}


def read_csv(path):
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def meaningful(text):
    text = (text or "").strip()
    if len(text) < 4:
        return False
    if GUID_RE.match(text):
        return False
    if any(pattern in text for pattern in IGNORE_PATTERNS):
        return False
    if "/" in text or "\\" in text:
        return False
    if not any(ch.isalpha() for ch in text):
        return False
    if not NOISE_RE.match(text):
        return False
    if " " not in text and not any(ch in text for ch in ".:!?"):
        if text in SINGLE_WORD_UI_LABELS:
            return True
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", default=str(MASTER_CSV))
    parser.add_argument("--reports", default=str(REPORT_DIR))
    parser.add_argument(
        "--output",
        default=str(REPORT_DIR / "raw_asset_uncovered_candidates.csv"),
    )
    parser.add_argument("--include-levels", action="store_true")
    parser.add_argument("--top", type=int, default=0)
    args = parser.parse_args()

    master_rows = read_csv(Path(args.master))
    covered_key_text = {(row["key"], row["text"]) for row in master_rows}
    covered_text = {row["text"] for row in master_rows}

    candidates = {}
    counts = Counter()
    for report in sorted(Path(args.reports).glob("raw_asset_visible_text_*_detailed.csv")):
        if not args.include_levels and "_levels_" in report.name:
            continue
        for row in read_csv(report):
            text = row.get("text", "")
            key = row.get("nearby_guid", "")
            if not meaningful(text):
                continue
            if row.get("source_file", "").endswith("EnglishSource.uasset"):
                continue
            if key and (key, text) in covered_key_text:
                continue
            if not key and text in covered_text:
                continue
            candidate_key = (key, text)
            counts[candidate_key] += 1
            candidates.setdefault(
                candidate_key,
                {
                    "nearby_guid": key,
                    "text": text,
                    "encoding": row.get("encoding", ""),
                    "first_source_file": row.get("source_file", ""),
                    "first_offset": row.get("offset", ""),
                    "report": report.name,
                },
            )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "nearby_guid",
                "text",
                "occurrences",
                "encoding",
                "first_source_file",
                "first_offset",
                "report",
            ],
        )
        writer.writeheader()
        for key, count in counts.most_common():
            writer.writerow({**candidates[key], "occurrences": count})

    print(f"wrote {len(candidates)} candidates to {output}")
    if args.top:
        skip_re = re.compile(
            r"ERROR|Debug|TODO|Not Found|not found|Call|Default|Property|Component|"
            r"Blueprint|Graph|Function|Variable|Warning|Example|Smoke|Pass|Skip|"
            r"Render Action|Focus on LKP|Enemy Is Set|Looking for servers|"
            r"ScreenPercentage|Received StackComponent|GameplayTag|ObjectProperty|"
            r"ReturnValue|Temp_|K2Node",
            re.IGNORECASE,
        )
        shown = 0
        print("nearby_guid,text,occurrences,encoding,source")
        for key, count in counts.most_common():
            row = candidates[key]
            if not row["nearby_guid"] or len(row["text"]) <= 8 or skip_re.search(row["text"]):
                continue
            print(
                ",".join(
                    [
                        row["nearby_guid"],
                        row["text"].replace("\n", "\\n")[:120],
                        str(count),
                        row["encoding"],
                        row["first_source_file"],
                    ]
                )
            )
            shown += 1
            if shown >= args.top:
                break


if __name__ == "__main__":
    main()
