import sys
import pandas as pd
from pathlib import Path
from src.core.preprocessing import levenshtein, word_to_decimal_unicode

# Configure stdout to support UTF-8 encoding in Windows terminals
sys.stdout.reconfigure(encoding='utf-8')

# Path configurations (resolved relative to the project root directory)
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent

staging_path = project_root / "data" / "raw" / "new_pairs.txt"
vocab_xlsx_path = project_root / "data" / "raw" / "vocab_database.xlsx"

# Master database files
db1_csv_path  = project_root / "data" / "processed" / "db1_utf8_pairs.csv"
db2_csv_path  = project_root / "data" / "processed" / "db2_unicode_integers.csv"
db2_xlsx_path = project_root / "data" / "processed" / "db2_unicode_pairs.xlsx"
db3_csv_path  = project_root / "data" / "processed" / "db3_processed.csv"

def word_to_hex_seq(word):
    """Converts a word to a string representation of a list of hexadecimal Unicode values."""
    if not isinstance(word, str):
        return "[]"
    return str([hex(ord(ch)) for ch in word])

def main():
    if not staging_path.exists():
        print(f"Error: Staging file {staging_path.name} not found.")
        return

    # 1. Read and parse raw new word pairs from staging
    lines = staging_path.read_text(encoding="utf-8").splitlines()
    lines = [l.strip() for l in lines if l.strip()]

    if not lines:
        print("Staging file is empty — nothing to append.")
        return

    new_pairs_raw = []
    for line in lines:
        parts = line.split(",")
        if len(parts) != 2:
            print(f"Skipping malformed line: '{line}'")
            continue
        new_pairs_raw.append((parts[0].strip(), parts[1].strip()))

    print(f"Found {len(new_pairs_raw)} raw pairs in staging file.")

    # 2. Load existing master files
    df1 = pd.read_csv(db1_csv_path, encoding='utf-8-sig')
    df2_csv = pd.read_csv(db2_csv_path, sep=',')
    df2_xlsx = pd.read_excel(db2_xlsx_path)
    df3_csv = pd.read_csv(db3_csv_path, sep=',')

    # Load vocabulary mapping for mapping characters to indices
    if not vocab_xlsx_path.exists():
        print(f"Error: {vocab_xlsx_path} not found. Cannot update database 3.")
        return
    df_vocab = pd.read_excel(vocab_xlsx_path)
    df_vocab['unicode_int'] = df_vocab['hex'].apply(lambda x: int(str(x), 16))
    vocab_map = dict(zip(df_vocab['unicode_int'], df_vocab['index']))

    def map_word_to_indices(word):
        """Converts a word to a semicolon-separated string of vocabulary index values."""
        if not isinstance(word, str):
            return ""
        return ";".join(str(vocab_map.get(ord(ch), "?")) for ch in word)

    # Perform redundancy check (checking both order variants)
    existing_pairs = set()
    for _, row in df1.iterrows():
        existing_pairs.add((str(row["w1"]), str(row["w2"])))
        existing_pairs.add((str(row["w2"]), str(row["w1"])))

    unique_new_pairs = []
    for w1, w2 in new_pairs_raw:
        if (w1, w2) in existing_pairs:
            print(f"Skipping duplicate pair: {w1}, {w2}")
            continue
        unique_new_pairs.append((w1, w2))
        existing_pairs.add((w1, w2))
        existing_pairs.add((w2, w1))

    if not unique_new_pairs:
        print("No new unique pairs to add.")
        staging_path.write_text("", encoding="utf-8")
        return

    print(f"Processing and appending {len(unique_new_pairs)} unique pairs...")

    # 3. Create records for new entries
    last_id = int(df1["pair_id"].max()) if not df1.empty else 0

    new_db1_data = []
    new_db2_csv_data = []
    new_db2_xlsx_data = []
    new_db3_csv_data = []

    for i, (w1, w2) in enumerate(unique_new_pairs):
        pid = last_id + i + 1
        led = levenshtein(w1, w2)

        new_db1_data.append({"pair_id": pid, "w1": w1, "w2": w2})

        new_db2_csv_data.append({
            "pair_id": pid,
            "w1": word_to_decimal_unicode(w1),
            "w2": word_to_decimal_unicode(w2),
            "LED": led
        })

        new_db2_xlsx_data.append({
            "pair_id": pid,
            "w1": w1,
            "w2": w2,
            "w1_unicode": word_to_hex_seq(w1),
            "w2_unicode": word_to_hex_seq(w2),
            "LED": led
        })

        new_db3_csv_data.append({
            "pair_id": pid,
            "w1": map_word_to_indices(w1),
            "w2": map_word_to_indices(w2),
            "LED": led
        })

    # 4. Concatenate and write back to files
    df1_updated = pd.concat([df1, pd.DataFrame(new_db1_data)], ignore_index=True)
    df2_csv_updated = pd.concat([df2_csv, pd.DataFrame(new_db2_csv_data)], ignore_index=True)
    df2_xlsx_updated = pd.concat([df2_xlsx, pd.DataFrame(new_db2_xlsx_data)], ignore_index=True)
    df3_csv_updated = pd.concat([df3_csv, pd.DataFrame(new_db3_csv_data)], ignore_index=True)

    # Save CSVs
    df1_updated.to_csv(db1_csv_path, index=False, encoding='utf-8-sig')
    df2_csv_updated.to_csv(db2_csv_path, sep=',', index=False)
    df3_csv_updated.to_csv(db3_csv_path, sep=',', index=False)

    # Save XLSX
    with pd.ExcelWriter(db2_xlsx_path, engine="openpyxl") as writer:
        df2_xlsx_updated.to_excel(writer, index=False)

    # 5. Clear staging file
    staging_path.write_text("", encoding="utf-8")

    print(f"Successfully appended {len(unique_new_pairs)} pairs to files.")
    print(f"Total entries in master database: {len(df1_updated)}")

if __name__ == "__main__":
    main()
