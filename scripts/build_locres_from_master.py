import argparse
from pathlib import Path

from locres_tool import build_locres
from translation_pipeline import MASTER_CSV, read_csv


def load_entries(path):
    rows = read_csv(Path(path))
    entries = []
    for row in rows:
        text = row.get("new_translation") or row["text"]
        entries.append(
            {
                "key": row["key"],
                "source_hash": int(row["source_hash"]),
                "text": text,
            }
        )
    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", default=str(MASTER_CSV))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    entries = load_entries(args.master)
    namespaces = []
    for namespace in ("", "EnglishSource"):
        namespaces.append(
            {
                "namespace": namespace,
                "entries": [{**entry, "namespace": namespace} for entry in entries],
            }
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(build_locres(namespaces))
    print(f"wrote {output} with {len(entries)} keys / {len(entries) * 2} rows")


if __name__ == "__main__":
    main()
