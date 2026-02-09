
def is_telugu_char(ch):
    return 0x0C00 <= ord(ch) <= 0x0C7F


def extract_telugu_words_unicode(bin_file):
    with open(bin_file, "rb") as f:
        text = f.read().decode("utf-8", errors="ignore")

    words = []
    current = []

    for ch in text:
        if is_telugu_char(ch):
            current.append(ch)
        else:
            if current:
                words.append("".join(current))
                current = []

    if current:
        words.append("".join(current))

    return words


def extract_telugu_words_bytes(bin_file):
    words_unicode = extract_telugu_words_unicode(bin_file)
    return [list(word.encode("utf-8")) for word in words_unicode]


if __name__ == "__main__":
    file = input("Enter the name of the binary file (.bin): ")
    words = extract_telugu_words_unicode(file)
    print(words)

