def is_separator(b):
    # ASCII bytes as separators (space, newline, punctuation, etc.)
    return b < 128


def extract_words_from_bin(file_path):
    with open(file_path, "rb") as f:
        data = f.read()

    words = []
    curr = []

    for b in data:
        if is_separator(b):
            if curr:
                words.append(bytes(curr))
                curr = []
        else:
            curr.append(b)

    if curr:
        words.append(bytes(curr))

    return words


if __name__ == "__main__":
    from pathlib import Path

    current_dir= Path(__file__).resolve().parent  
    path = current_dir.parent / "data" / "processed" / "dataset.bin"

    words = extract_words_from_bin(path)

    for w in words:
        print(list(w))
