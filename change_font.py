import re


def read_file():
    with open("right.c", 'r', encoding='utf-8') as f:
        content = f.read()

    with open('glyph_bitmap.txt', 'w', encoding='utf-8') as f:
        start = content.find('glyph_bitmap[]')
        end = content.find('};', start)
        data = content[start:end]
        f.write(data)


if __name__ == '__main__':
    read_file()
    with open("glyph_bitmap.txt", 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'//.*', '', content)
    print(content)
