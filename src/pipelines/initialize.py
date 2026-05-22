import pandas as pd
from pathlib import Path
from src.core.preprocessing import levenshtein, word_to_decimal_unicode

# Path configurations (resolved relative to the project root directory)
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent

db1_csv_path = project_root / "data" / "processed" / "db1_utf8_pairs.csv"
vocab_xlsx_path = project_root / "data" / "raw" / "vocab_database.xlsx"

# Processed output paths
db2_csv_path = project_root / "data" / "processed" / "db2_unicode_integers.csv"
db2_xlsx_path = project_root / "data" / "processed" / "db2_unicode_pairs.xlsx"
db3_csv_path = project_root / "data" / "processed" / "db3_processed.csv"

def word_to_hex_seq(word):
    """Converts a word to a string representation of a list of hexadecimal Unicode values."""
    if not isinstance(word, str):
        return "[]"
    return str([hex(ord(ch)) for ch in word])

def main():
    if not db1_csv_path.exists():
        print(f"Error: {db1_csv_path} not found.")
        return

    # Load Telugu word pairs (UTF-8 BOM compatible)
    df1 = pd.read_csv(db1_csv_path, encoding='utf-8-sig')
    print(f"Loaded {len(df1)} pairs from {db1_csv_path.name}")

    # Load vocabulary mapping for mapping characters to indices
    if not vocab_xlsx_path.exists():
        print(f"Error: {vocab_xlsx_path} not found. Cannot build database 3.")
        return
    df_vocab = pd.read_excel(vocab_xlsx_path)
    df_vocab['unicode_int'] = df_vocab['hex'].apply(lambda x: int(str(x), 16))
    vocab_map = dict(zip(df_vocab['unicode_int'], df_vocab['index']))

    def map_word_to_indices(word):
        """Converts a word to a semicolon-separated string of vocabulary index values."""
        if not isinstance(word, str):
            return ""
        return ";".join(str(vocab_map.get(ord(ch), "?")) for ch in word)

    records = []
    for _, row in df1.iterrows():
        w1 = str(row["w1"])
        w2 = str(row["w2"])
        led = levenshtein(w1, w2)

        records.append({
            "pair_id": int(row["pair_id"]),
            "w1": w1,
            "w2": w2,
            "w1_unicode_hex": word_to_hex_seq(w1),
            "w2_unicode_hex": word_to_hex_seq(w2),
            "w1_unicode_dec": word_to_decimal_unicode(w1),
            "w2_unicode_dec": word_to_decimal_unicode(w2),
            "w1_vocab_indices": map_word_to_indices(w1),
            "w2_vocab_indices": map_word_to_indices(w2),
            "LED": led,
        })

    df_full = pd.DataFrame(records)

    # 1. Export Excel workbook for manual visualization
    df_xlsx = df_full[["pair_id", "w1", "w2", "w1_unicode_hex", "w2_unicode_hex", "LED"]]
    df_xlsx.columns = ["pair_id", "w1", "w2", "w1_unicode", "w2_unicode", "LED"]
    with pd.ExcelWriter(db2_xlsx_path, engine="openpyxl") as writer:
        df_xlsx.to_excel(writer, index=False)
    print(f"Generated Excel workbook: {db2_xlsx_path.name}")

    # 2. Export DB2 CSV (Unicode codepoints: comma-delimited, semicolon-list-separated)
    df_db2 = df_full[["pair_id", "w1_unicode_dec", "w2_unicode_dec", "LED"]]
    df_db2.columns = ["pair_id", "w1", "w2", "LED"]
    df_db2.to_csv(db2_csv_path, sep=',', index=False)
    print(f"Generated DB2 (Unicode Codepoints): {db2_csv_path.name}")

    # 3. Export DB3 CSV (Vocabulary indices: comma-delimited, semicolon-list-separated)
    df_db3 = df_full[["pair_id", "w1_vocab_indices", "w2_vocab_indices", "LED"]]
    df_db3.columns = ["pair_id", "w1", "w2", "LED"]
    df_db3.to_csv(db3_csv_path, sep=',', index=False)
    print(f"Generated DB3 (Vocabulary Indices): {db3_csv_path.name}")

if __name__ == "__main__":
    main()
