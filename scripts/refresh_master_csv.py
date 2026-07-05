from translation_pipeline import MASTER_CSV, build_master_rows, write_csv


def main():
    rows = build_master_rows()
    write_csv(MASTER_CSV, rows)
    print(f"wrote {len(rows)} rows to {MASTER_CSV}")


if __name__ == "__main__":
    main()

