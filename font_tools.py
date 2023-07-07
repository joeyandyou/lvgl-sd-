import struct


def open_addr_main():
    path = "地址.txt"
    file = open(path, "r", encoding='utf-8')
    data_addr = file.read()
    return data_addr


def handle_addr(data_addr):
    while("/*" in data_addr):
        s_index = data_addr.index("/*")
        e_index = s_index + 7
        data_addr = data_addr.replace(data_addr[s_index:e_index], "")

    data_addr = data_addr.replace(" ", "").replace("\n", "").replace("\t", "")
    data_list = data_addr.split(",")
    if "\ufeff" in data_list[0]:
        data_list[0] = data_list[0].replace("\ufeff", "")
    data_list.remove(data_list[-1])

    return data_list


def write_addr():
    list1 = handle_addr(open_addr_main())
    list1.pop()

    list2 = []
    for i in range(0, 65536):
        list2.append("0xffff")

    for i in range(0, len(list1)):
        num = int(list1[i], 16)
        list2[num] = i
    print(list2)
    with open("复制其中内容进入文件.txt", "w") as file:
        file.write("{" + ", ".join(str(x) for x in list2) + "}")
    file.close()


def handle_cut(a):
    while("/*" in a):
        s_index = a.index("/*")
        e_index = s_index + 7
        a = a.replace(a[s_index:e_index], "")
    list1 = ["/", ".", "%", "@", "+"]
    new_a = "".join([char for char in a if char not in list1])
    new_a = new_a.replace(" ", "").replace("\n", "")
    data_list = new_a.split(",")
    data_list.remove(data_list[-1])
    return data_list


def open_word_mod():
    path = "字模表.txt"
    file = open(path, "r", encoding='utf-8')
    data_word_mod = file.read()
    return data_word_mod


def write_word_mod(data, fp):

    if "\ufeff" in data[0]:
        data[0] = data[0].replace("\ufeff", "")
    data_list = [int(x, 16) for x in data]
    fp.seek(0)
    for i in data_list:
        mes = struct.pack('B', i)
        fp.write(mes)


if __name__ == "__main__":
    write_addr()
    data_font_mod = handle_cut(open_word_mod())
    with open("将此文件放入sd卡.hex", "a+b") as fp:
        fp.seek(0)
        write_word_mod(data_font_mod, fp)

    fp.close()
