import sys

def splitLine(words: list, maxWidth: int) -> list[str]:
    result = []
    current_line = []
    current_line_length = 0

    for word in words:
        word_length = len(word)
        # If adding this word exceeds maxWidth
        if current_line_length + word_length + len(current_line) > maxWidth:
            result.append(" ".join(current_line))
            current_line = []
            current_line_length = 0
        current_line.append(word)
        current_line_length += word_length

    # Add the last line if it has words
    if current_line:
        result.append(" ".join(current_line))

    return result


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) < 2:
        print("Usage: python script.py <maxWidth> <word1> <word2> ...")
        sys.exit(1)

    maxWidth = int(argv[1])
    words = argv[2:]

    lines = splitLine(words, maxWidth)
    for line in lines:
        print(f'"{line}"')
