import argparse
import csv
import json
import struct
from pathlib import Path


def read_i32(data, pos):
    return struct.unpack_from("<i", data, pos)[0], pos + 4


def read_u32(data, pos):
    return struct.unpack_from("<I", data, pos)[0], pos + 4


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


def write_fstring(value):
    if any(ord(ch) > 0x7F for ch in value):
        raw = value.encode("utf-16le") + b"\x00\x00"
        return struct.pack("<i", -(len(raw) // 2)) + raw
    raw = value.encode("utf-8") + b"\x00"
    return struct.pack("<i", len(raw)) + raw


def parse_locres(path):
    data = Path(path).read_bytes()
    if data[:16] == bytes.fromhex("0e147475674a03fc4a15909dc3377f1b"):
        return parse_compact_locres(data)
    pos = 0
    namespace_count, pos = read_i32(data, pos)
    namespaces = []
    for _ in range(namespace_count):
        namespace, pos = read_fstring(data, pos)
        entry_count, pos = read_u32(data, pos)
        entries = []
        for _ in range(entry_count):
            key, pos = read_fstring(data, pos)
            source_hash, pos = read_u32(data, pos)
            text, pos = read_fstring(data, pos)
            entries.append(
                {
                    "namespace": namespace,
                    "key": key,
                    "source_hash": source_hash,
                    "text": text,
                }
            )
        namespaces.append({"namespace": namespace, "entries": entries})
    if pos != len(data):
        raise ValueError(f"Trailing bytes after parse: {len(data) - pos}")
    return namespaces


def parse_compact_locres(data):
    pos = 16
    version = data[pos]
    pos += 1
    string_array_offset = struct.unpack_from("<q", data, pos)[0]
    pos += 8

    strings = []
    if string_array_offset != -1:
        string_pos = string_array_offset
        string_count, string_pos = read_u32(data, string_pos)
        for _ in range(string_count):
            text, string_pos = read_fstring(data, string_pos)
            ref_count, string_pos = read_i32(data, string_pos)
            strings.append({"text": text, "ref_count": ref_count})
        if string_pos != len(data):
            raise ValueError(f"Trailing bytes after string pool: {len(data) - string_pos}")

    entries_count, pos = read_u32(data, pos)
    namespace_count, pos = read_u32(data, pos)
    namespaces = []
    for _ in range(namespace_count):
        namespace_hash, pos = read_u32(data, pos)
        namespace, pos = read_fstring(data, pos)
        entry_count, pos = read_u32(data, pos)
        entries = []
        for _ in range(entry_count):
            key_hash, pos = read_u32(data, pos)
            key, pos = read_fstring(data, pos)
            source_hash, pos = read_u32(data, pos)
            localized_index, pos = read_i32(data, pos)
            entries.append(
                {
                    "namespace": namespace,
                    "namespace_hash": namespace_hash,
                    "key": key,
                    "key_hash": key_hash,
                    "source_hash": source_hash,
                    "localized_index": localized_index,
                    "text": "",
                }
            )
        namespaces.append({"namespace": namespace, "entries": entries})

    if pos != string_array_offset:
        raise ValueError(f"Entry section ended at {pos}, expected string pool at {string_array_offset}")

    for entry in flatten(namespaces):
        if 0 <= entry["localized_index"] < len(strings):
            entry["text"] = strings[entry["localized_index"]]["text"]

    return {
        "format": "compact",
        "version": version,
        "entries_count": entries_count,
        "strings": strings,
        "namespaces": namespaces,
    }


def normalize(parsed):
    if isinstance(parsed, dict):
        return parsed["namespaces"]
    return parsed


def build_locres(namespaces):
    if isinstance(namespaces, dict):
        return build_compact_locres(namespaces)
    out = bytearray()
    out += struct.pack("<i", len(namespaces))
    for group in namespaces:
        out += write_fstring(group["namespace"])
        out += struct.pack("<I", len(group["entries"]))
        for entry in group["entries"]:
            out += write_fstring(entry["key"])
            out += struct.pack("<I", int(entry["source_hash"]))
            out += write_fstring(entry["text"])
    return bytes(out)


def build_compact_locres(parsed):
    out = bytearray()
    out += bytes.fromhex("0e147475674a03fc4a15909dc3377f1b")
    out += bytes([parsed["version"]])
    offset_pos = len(out)
    out += b"\x00" * 8
    out += struct.pack("<I", sum(len(group["entries"]) for group in parsed["namespaces"]))
    out += struct.pack("<I", len(parsed["namespaces"]))
    for group in parsed["namespaces"]:
        first = group["entries"][0] if group["entries"] else {}
        out += struct.pack("<I", int(first.get("namespace_hash", 0)))
        out += write_fstring(group["namespace"])
        out += struct.pack("<I", len(group["entries"]))
        for entry in group["entries"]:
            out += struct.pack("<I", int(entry.get("key_hash", 0)))
            out += write_fstring(entry["key"])
            out += struct.pack("<I", int(entry["source_hash"]))
            out += struct.pack("<i", int(entry["localized_index"]))
    string_array_offset = len(out)
    out[offset_pos : offset_pos + 8] = struct.pack("<q", string_array_offset)
    out += struct.pack("<I", len(parsed["strings"]))
    for item in parsed["strings"]:
        out += write_fstring(item["text"])
        out += struct.pack("<i", int(item["ref_count"]))
    return bytes(out)


def flatten(namespaces):
    namespaces = normalize(namespaces)
    for group in namespaces:
        for entry in group["entries"]:
            yield entry


def export_csv(args):
    parsed = parse_locres(args.input)
    rows = list(flatten(parsed))
    with Path(args.output).open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["namespace", "key", "source_hash", "text", "translation"],
            extrasaction="ignore",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "translation": row["text"]})
    print(f"exported {len(rows)} rows to {args.output}")


def export_json(args):
    parsed = parse_locres(args.input)
    namespaces = normalize(parsed)
    Path(args.output).write_text(
        json.dumps(namespaces, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"exported {sum(len(g['entries']) for g in namespaces)} rows to {args.output}")


def import_csv(args):
    parsed = parse_locres(args.template)
    translations = {}
    with Path(args.input).open("r", newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            translations[(row["namespace"], row["key"])] = row.get("translation") or row["text"]
    if isinstance(parsed, dict):
        for entry in flatten(parsed):
            key = (entry["namespace"], entry["key"])
            if key in translations:
                parsed["strings"][entry["localized_index"]]["text"] = translations[key]
    else:
        for entry in flatten(parsed):
            key = (entry["namespace"], entry["key"])
            if key in translations:
                entry["text"] = translations[key]
    Path(args.output).write_bytes(build_locres(parsed))
    print(f"wrote {args.output}")


def stats(args):
    parsed = parse_locres(args.input)
    namespaces = normalize(parsed)
    rows = list(flatten(parsed))
    cn = sum(any("\u4e00" <= ch <= "\u9fff" for ch in row["text"]) for row in rows)
    placeholder = sum("占位文本" in row["text"] for row in rows)
    ascii_only = sum(all(ord(ch) < 128 for ch in row["text"]) for row in rows)
    print(f"file: {args.input}")
    if isinstance(parsed, dict):
        print(f"format: compact v{parsed['version']}")
        print(f"string pool: {len(parsed['strings'])}")
    else:
        print("format: direct")
    print(f"namespaces: {len(namespaces)}")
    print(f"rows: {len(rows)}")
    print(f"unique keys: {len({row['key'] for row in rows})}")
    print(f"contains Chinese: {cn}")
    print(f"placeholder rows: {placeholder}")
    print(f"ASCII-only rows: {ascii_only}")
    for group in namespaces:
        print(f"  {group['namespace']!r}: {len(group['entries'])}")


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

    p = sub.add_parser("export-json")
    p.add_argument("input")
    p.add_argument("output")
    p.set_defaults(func=export_json)

    p = sub.add_parser("import-csv")
    p.add_argument("template")
    p.add_argument("input")
    p.add_argument("output")
    p.set_defaults(func=import_csv)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
