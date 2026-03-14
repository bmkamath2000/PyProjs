def justify_text(words, maxWidth):
    result = []
    line = []
    line_length = 0

    for word in words:
        if line_length + len(word) + len(line) > maxWidth:
            total_spaces = maxWidth - line_length
            if len(line) == 1:
                result.append(line[0] + ' ' * total_spaces)
            else:
                even_space = total_spaces // (len(line) - 1)
                extra_space = total_spaces % (len(line) - 1)
                line_str = ''
                for i in range(len(line)):
                    line_str += line[i]
                    if i < len(line) - 1:
                        line_str += ' ' * (even_space + (1 if i < extra_space else 0))
                result.append(line_str)
            line = []
            line_length = 0

        line.append(word)
        line_length += len(word)
        
    last_line = ' '.join(line)
    last_line += ' ' * (maxWidth - len(last_line))
    result.append(last_line)
    return result

input_text = input("Enter the text you want to justify: ")
words = input_text.strip().split()
maxWidth = int(input("Enter max line width: "))
output = justify_text(words, maxWidth)
for line in output:
    print('|' + line + '|')
