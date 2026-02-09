import numpy as np
from itertools import combinations

#Initialization of Vocab_size, start and end of the unicodes related to Telugu Language
Unicode_start = 0x0C00
Unicode_end  = 0x0C7F
Vocab_size = Unicode_end - Unicode_start + 1

#Word -> Unicode
def word_to_codepoints(word):
    return [ord(ch) for ch in word]
#char-Unicode 'అ'->0x0c00
def char_to_onehot(ch):
    code=ord(ch)
    vec=np.zeros(Vocab_size,dtype=np.int8)
    if Unicode_start<=code<=Unicode_end:
        vec[code-Unicode_start]=1
    
        return vec
    else:
        return None
#word->unicode 
def word_to_unicode_sequence(word):
    seq=[]
    for ch in word:
        vec = char_to_onehot(ch)
        if vec is None:
            return []
        seq.append(vec)
        
    return seq
#Levishtein Distance
def levenshtein(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0]*(n+1) for _ in range(m+1)]

    for i in range(m+1):
        dp[i][0] = i
    for j in range(n+1):
        dp[0][j] = j

    for i in range(1, m+1):
        for j in range(1, n+1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )
    return dp[m][n]

def build_unicode_table(words):
    table = {}
    for w in words:
        table[w] = word_to_unicode_sequence(w)
    return table
def build_dataset(words, max_pairs=500):
    unicode_table = build_unicode_table(words)
    pairs = list(combinations(words, 2))
    pairs = pairs[:max_pairs]

    dataset = []
    for w1, w2 in pairs:
        x1 = unicode_table[w1]
        x2 = unicode_table[w2]
        y  = levenshtein(w1, w2)
        dataset.append((x1, x2, y))

    return dataset

if __name__ == "__main__":
    # demo characters and word
    demo_word = "అమల"
    print("Word:", demo_word)

    print("\nCharacter -> Unicode -> One-hot index")
    for ch in demo_word:
        code = ord(ch)
        idx = code - Unicode_start
        print(f"{ch} -> {hex(code)} -> {idx}")
    
    print("\nWord -> Unicode sequence")
    print([hex(u) for u in word_to_codepoints(demo_word)])

    print("\nWord -> One-hot sequence shape")
    onehot_seq = word_to_unicode_sequence(demo_word)
    print(f"Length: {len(onehot_seq)}, One-hot dim: {Vocab_size}")
    
    



