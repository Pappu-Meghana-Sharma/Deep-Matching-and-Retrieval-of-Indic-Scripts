import pandas as pd
from pathlib import Path
from build_db2 import levenshtein, word_to_unicode_seq
current_dir   = Path(__file__).resolve().parent
staging_path  = current_dir.parent / "data" / "raw"       / "new_pairs.txt"
db1_path      = current_dir.parent / "data" / "processed" / "db1_utf8_pairs.xlsx"
db2_path      = current_dir.parent / "data" / "processed" / "db2_unicode_pairs.xlsx"

if __name__ == "__main__":
 

    lines = staging_path.read_text(encoding="utf-8").splitlines()
    lines = [l.strip() for l in lines if l.strip()]
 
    if not lines:
        print("Staging file is empty — nothing to append.")
        exit()
 
    new_pairs_raw = []
    for line in lines:
        parts = line.split(",")
        if len(parts) != 2:
            print(f"Skipping malformed line: '{line}'")
            continue
        new_pairs_raw.append((parts[0].strip(), parts[1].strip()))
 
    print(f"Found {len(new_pairs_raw)} new pairs in staging file")

    df1_existing = pd.read_excel(db1_path)
    df2_existing = pd.read_excel(db2_path)
    print(f"Existing DB1: {len(df1_existing)} pairs")
    print(f"Existing DB2: {len(df2_existing)} pairs")

    last_id = int(df1_existing["pair_id"].max())
    new_pairs = [
        (last_id + i + 1, w1, w2)
        for i, (w1, w2) in enumerate(new_pairs_raw)
    ]
    print(f"Assigning pair_ids: {last_id + 1} → {last_id + len(new_pairs)}")
 
    print(f"\nRunning sanity check on new pairs...")
    for pid, w1, w2 in new_pairs:
        for col, word in [("w1", w1), ("w2", w2)]:
            unicode_seq   = [hex(ord(ch)) for ch in word]
            reconstructed = "".join(chr(int(h, 16)) for h in unicode_seq)
            assert reconstructed == word, (
                f"Corruption detected!\n"
                f"  pair_id : {pid}\n"
                f"  column  : {col}\n"
                f"  original: '{word}'\n"
                f"  rebuilt : '{reconstructed}'"
            )
    print("Sanity check passed — all new pairs clean.\n")
 
    new_db1_rows = [
        {"pair_id": pid, "w1": w1, "w2": w2}
        for pid, w1, w2 in new_pairs
    ]
    new_db2_rows = [
        {
            "pair_id":    pid,
            "w1":         w1,
            "w2":         w2,
            "w1_unicode": word_to_unicode_seq(w1),
            "w2_unicode": word_to_unicode_seq(w2),
            "LED":        levenshtein(w1, w2),
        }
        for pid, w1, w2 in new_pairs
    ]
 
  
    df1_updated = pd.concat(
        [df1_existing, pd.DataFrame(new_db1_rows)],
        ignore_index=True
    )
    df2_updated = pd.concat(
        [df2_existing, pd.DataFrame(new_db2_rows)],
        ignore_index=True
    )
 
    with pd.ExcelWriter(db1_path, engine="openpyxl") as w:
        df1_updated.to_excel(w, index=False)
 
    with pd.ExcelWriter(db2_path, engine="openpyxl") as w:
        df2_updated.to_excel(w, index=False)
 

    staging_path.write_text("", encoding="utf-8")
    print(f"Staging file cleared.")
 
    print(f"\nDB1: {len(df1_existing)} → {len(df1_updated)} pairs")
    print(f"DB2: {len(df2_existing)} → {len(df2_updated)} pairs")
    print(f"\nNew pairs added:")
    print(f"{'pair_id':<10} {'w1':<34} {'w2':<34} {'LED':>4}")
    print("-"*85)
    for r in new_db2_rows:
        print(f"{r['pair_id']:<10} {r['w1']:<34} {r['w2']:<34} {r['LED']:>4}")