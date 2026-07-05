import argparse
import csv
import struct
from pathlib import Path


def read_i32(data, pos):
    return struct.unpack_from("<i", data, pos)[0], pos + 4


def read_fstring(data, pos):
    length, pos = read_i32(data, pos)
    if length == 0:
        return "", pos
    if length > 0:
        raw = data[pos : pos + length]
        pos += length
        return raw[:-1].decode("utf-8", "replace"), pos
    length = -length
    raw = data[pos : pos + length * 2]
    pos += length * 2
    return raw[:-2].decode("utf-16le", "replace"), pos


def parse_entries(data, start):
    namespace, pos = read_fstring(data, start)
    count, pos = read_i32(data, pos)
    if namespace != "EnglishSource" or count <= 0 or count > 100000:
        raise ValueError("Not an EnglishSource table")
    rows = []
    for _ in range(count):
        key, pos = read_fstring(data, pos)
        text, pos = read_fstring(data, pos)
        rows.append({"key": key, "text": text, "translation": text})
    return rows, pos


def find_table(data):
    needle = b"\x0e\x00\x00\x00EnglishSource\x00"
    starts = []
    pos = 0
    while True:
        pos = data.find(needle, pos)
        if pos < 0:
            break
        starts.append(pos)
        pos += 1
    for start in starts:
        try:
            rows, end = parse_entries(data, start)
        except Exception:
            continue
        if len(rows) > 100:
            return rows, start, end
    raise RuntimeError("Could not locate EnglishSource table")


def export_csv(args):
    data = Path(args.input).read_bytes()
    rows, start, end = find_table(data)
    with Path(args.output).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["key", "text", "translation"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"exported {len(rows)} rows to {args.output}")
    print(f"table offset: {start}, end: {end}")


def stats(args):
    data = Path(args.input).read_bytes()
    rows, start, end = find_table(data)
    ascii_only = sum(all(ord(ch) < 128 for ch in row["text"]) for row in rows)
    placeholders = sum("Placeholder text" in row["text"] for row in rows)
    print(f"rows: {len(rows)}")
    print(f"unique keys: {len({row['key'] for row in rows})}")
    print(f"ASCII-only rows: {ascii_only}")
    print(f"placeholder rows: {placeholders}")
    print(f"table offset: {start}")
    print(f"table end: {end}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("stats")
    p.add_argument("input")
    p.set_defaults(func=stats)

    p = sub.add_parser("export-csv")
    p.add_argument("input")
    p.add_argument("output")
    p.set_defaults(func=export_csv)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
