import numpy as np

# Telugu Unicode range definitions
Unicode_start = 0x0C00
Unicode_end  = 0x0C7F
Vocab_size = Unicode_end - Unicode_start + 1

def is_telugu_char(ch):
    """Checks if a character belongs to the Telugu Unicode range."""
    return Unicode_start <= ord(ch) <= Unicode_end

def word_to_codepoints(word):
    """Converts a string word into a list of integer Unicode codepoints."""
    return [ord(ch) for ch in word]

def word_to_decimal_unicode(word):
    """Converts a word to a semicolon-separated string of Unicode decimal integers."""
    if not word or not isinstance(word, str):
        return ""
    return ";".join(str(ord(ch)) for ch in word)

def char_to_onehot(ch):
    """Converts a single character to its one-hot vector representation within Telugu vocabulary."""
    code = ord(ch)
    vec = np.zeros(Vocab_size, dtype=np.int8)
    if Unicode_start <= code <= Unicode_end:
        vec[code - Unicode_start] = 1
        return vec
    return None

def word_to_unicode_sequence(word):
    """Converts a word to a sequence of one-hot vectors."""
    seq = []
    for ch in word:
        vec = char_to_onehot(ch)
        if vec is None:
            return []
        seq.append(vec)
    return seq

def levenshtein(s1, s2):
    """Calculates the Levenshtein distance between two strings."""
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
