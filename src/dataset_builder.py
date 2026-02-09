from byte_pipeline import extract_words_from_bin
from telugu_word_extractor import extract_telugu_words_unicode
from pathlib import Path
import pandas as pd
def levenshtein(a,b):
    n, m = len(a),len(b)
    dp = [[0]*(m+1) for _ in range(n+1)]

    for i in range(n+1):
        dp[i][0] = i
    for j in range(m+1):
        dp[0][j] = j

    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,      # deletion
                dp[i][j-1] + 1,      # insertion
                dp[i-1][j-1] + cost  # substitution
            )
    return dp[n][m]


def is_valid_telugu_bytes(b):
    try:
        s = b.decode("utf-8")
    except:
        return None

    for ch in s:
        if not (0x0C00 <= ord(ch) <= 0x0C7F):
            return None

    return s


def build_dataset(bin_file):
    raw_byte_words = extract_words_from_bin(bin_file)

    valid = []
    for bw in raw_byte_words:
        u = is_valid_telugu_bytes(bw)
        if u is not None:
            valid.append((bw, u))

    dataset = []
    for i in range(len(valid)):
        for j in range(i + 1, len(valid)):
            b1, u1 = valid[i]
            b2, u2 = valid[j]

            dataset.append({
		"word1": u1,
                "word2": u2,
                "w1_bytes": list(b1),
                "w2_bytes": list(b2),
                "target_distance": levenshtein(list(u1), list(u2))
            })

    return dataset, valid


if __name__ == "__main__":
    current_dir= Path(__file__).resolve().parent  
    file= current_dir.parent / "data" / "processed" / "dataset.bin"

    dataset,valid_words=build_dataset(file)
    print("\nValid words from binary pipeline: ")
    for _,u in valid_words[:10]:
        print(u)
    print("\nWords from Telugu Extractor (for comparision): ")
    telugu_words = extract_telugu_words_unicode(file)
    for w in telugu_words[:10]:
        print(w)
    df=pd.DataFrame(dataset)
    print("\n Dataset Sample: ")
    print(df.iloc[0,:])
