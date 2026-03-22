import pandas as pd
from pathlib import Path
current_dir = Path(__file__).resolve().parent
db1_path    = current_dir.parent / "data" / "processed" / "db1_utf8_pairs.xlsx"
db2_path    = current_dir.parent / "data" / "processed" / "db2_unicode_pairs.xlsx"

def levenshtein(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )
    return dp[m][n]

def word_to_unicode_seq(word):
    return str([hex(ord(ch)) for ch in word])


if __name__ == "__main__":
    df1 = pd.read_excel(db1_path)
    print(f"Loaded DB1: {len(df1)} pairs from {db1_path}")
    
    print("Running sanity check on DB1...")
    for _, row in df1.iterrows():
        for col in ["w1", "w2"]:
            word = str(row[col])
            # forward: word → unicode sequence
            unicode_seq = [hex(ord(ch)) for ch in word]
            # reverse: unicode sequence → word
            reconstructed = "".join(chr(int(h, 16)) for h in unicode_seq)
            # compare
            assert reconstructed == word, (
                f"Corruption detected!\n"
                f"  pair_id : {row['pair_id']}\n"
                f"  column  : {col}\n"
                f"  original: '{word}'\n"
                f"  rebuilt : '{reconstructed}'"
            )
    print("Sanity check passed — all words clean.\n")
    
    rows = []
    for _, row in df1.iterrows():
        w1  = str(row["w1"])
        w2  = str(row["w2"])
        led = levenshtein(w1, w2)
        rows.append({
            "pair_id":    int(row["pair_id"]),
            "w1":         w1,
            "w2":         w2,
            "w1_unicode": word_to_unicode_seq(w1),
            "w2_unicode": word_to_unicode_seq(w2),
            "LED":        led,
        })
        
    df2 = pd.DataFrame(rows)
    
    with pd.ExcelWriter(db2_path, engine="openpyxl") as writer:
        df2.to_excel(writer, index=False)
 
    print(f"Written DB2: {len(df2)} pairs to {db2_path}")
    print(f"\nSample output:")
    print(df2[["pair_id", "w1", "w2", "LED"]].head(10).to_string(index=False))
    print(f"\nLED stats:")
    print(f"  min : {df2['LED'].min()}")
    print(f"  max : {df2['LED'].max()}")
    print(f"  mean: {df2['LED'].mean():.2f}")