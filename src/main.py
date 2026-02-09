import pandas as pd
from preprocessing import word_to_codepoints,build_dataset
from pathlib import Path
def read_words(path, max_words=500):
    words = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            w = line.strip()
            if w:
                words.append(w)
            if len(words) == max_words:
                break
    return words

if __name__ == "__main__":
    current_dir= Path(__file__).resolve().parent  
    path = current_dir.parent / "data" / "raw" / "telugu_words_500.txt"

    words = read_words(path, max_words=500)

    # Unicode table
    unicode_rows = []
    for w in words:
        unicode_rows.append({
            "word": w,
            "unicode_sequence": [hex(u) for u in word_to_codepoints(w)]
        })
    df_unicode = pd.DataFrame(unicode_rows)
    df_unicode.to_excel("word_unicode_table.xlsx", index=False)

    # Pairwise dataset (x1, x2, y)
    dataset = build_dataset(words, max_pairs=500)

    pair_rows = []
    for i, (x1, x2, y) in enumerate(dataset):
        pair_rows.append({
            "pair_id": i,
            "x1": x1,
            "x2": x2,
            "y_levenshtein": y
        })
    df_pairs = pd.DataFrame(pair_rows)
    df_pairs.to_excel("string_pair_dataset.xlsx", index=False)