import binascii
import struct
import re


def template():
    a = 255
    with open('d.hex', 'wb') as f:
        # 写入 0xffff 的字节数据 262140 次
        i = 1
        c = 262144
        a_byte = struct.pack('B', a)
        while (i <= c):
            f.write(a_byte)
            i = i + 1


def open_word_mod():
    path = "字模表.txt"
    file = open(path, "r", encoding='utf-8')
    data_word_mod = file.read()
    return data_word_mod


def open_addr_main():
    path = "地址.txt"
    file = open(path, "r", encoding='utf-8')
    data_addr = file.read()
    return data_addr


def open_comparison_table():
    path = "对照表.txt"
    file = open(path, 'r', encoding='utf-8')
    data_comparison = file.read()
    return data_comparison


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


def handle_comparison(data):
    while("/*" in data):
        s_index = data.index("/*")
        e_index = s_index + 7
        data = data.replace(data[s_index:e_index], "")
    data = data.replace("\t.", "").replace("\n", "").replace(".", "").replace(" ", "")
    dict_list = []
    for item in data.split(','):
        dict_item = {}
        for kv_pair in re.findall(r'(\w+)=(\w+)', item):
            dict_item[kv_pair[0]] = int(kv_pair[1])
        dict_list.append(dict_item)
    new_list = []
    for i in range(0, len(dict_list), 6):
        new_dict = {}
        for j in range(i, i + 6):
            new_dict.update(dict_list[j])
        new_list.append(new_dict)
    new_list = new_list[2:]
    return new_list


def write_word_mod(data, fp):
    list_addr = []
    if "\ufeff" in data[0]:
        data[0] = data[0].replace("\ufeff", "")
    data_list = [int(x, 16) for x in data]

    comparison_list = handle_comparison(open_comparison_table())
    comparison_list_len = len(comparison_list)

    bitmap_start = 0

    fp.seek(0)
    for i in range(0, comparison_list_len):

        adv_w = hex(comparison_list[i]["adv_w"])
        box_h = hex(comparison_list[i]["box_h"])
        box_w = hex(comparison_list[i]["box_w"])
        ofs_x = hex(comparison_list[i]["ofs_x"])
        ofs_y = hex(comparison_list[i]["ofs_y"])
        if comparison_list[i] != comparison_list[-1]:
            size = hex(5)
            if comparison_list[i] != comparison_list[i + 1]:
                size = hex(comparison_list[i + 1]["bitmap_index"] - comparison_list[i]["bitmap_index"])
        else:
            size = hex(int((comparison_list[i]["box_h"] * comparison_list[i]["adv_w"]) / 2))
        mes_size = struct.pack('H', int(size, 16))
        mes_adv_w = struct.pack('B', int(adv_w, 16))
        mes_box_h = struct.pack('B', int(box_h, 16))
        mes_box_w = struct.pack('B', int(box_w, 16))
        mes_ofs_x = struct.pack('B', int(ofs_x, 16))
        mes_ofs_y = struct.pack('B', int(ofs_y, 16))

        fp.write(mes_size)
        fp.write(mes_adv_w)
        fp.write(mes_box_h)
        fp.write(mes_box_w)
        fp.write(mes_ofs_x)
        fp.write(mes_ofs_y)

        if comparison_list[i] != comparison_list[-1]:
            bitmap_index_ii = comparison_list[i]["bitmap_index"]
            bitmap_index = comparison_list[i + 1]["bitmap_index"]

            address = bitmap_index_ii + 7 * i + 262144

            # print("117bitmap_index", bitmap_index, "bitmap_start", bitmap_start, len(data_list))
        else:
            bitmap_index_ii = comparison_list[i]["bitmap_index"] + (comparison_list[i]["box_h"] * comparison_list[i]["adv_w"]) / 2 + 7 * i
            address = bitmap_index_ii + 0
            bitmap_index = bitmap_index_ii
        list_addr.append(address)
        if comparison_list[i] == comparison_list[-1]:
            continue
        if comparison_list[i] == comparison_list[i + 1]:
            continue
        for j in range(bitmap_start, len(data_list)):
            if j < bitmap_start:
                continue

            if bitmap_index > j >= bitmap_start:
                mes = struct.pack('B', data_list[j])
                fp.write(mes)

            if j >= bitmap_index:

                bitmap_start = bitmap_index
                break
    write_addr(list_addr)


def write_addr(buf_list):
    data_address_list = handle_addr(open_addr_main())
    data_address_list = data_address_list[2:]
    buf_list[-1] = int(buf_list[-1])
    print(buf_list)
    with open("d.hex", "r+b") as file:

        for i in range(0, len(buf_list)):

            ops = int(data_address_list[i], 16) * 4

            packed_int = struct.pack('i', buf_list[i])
            file.seek(ops)
            file.write(packed_int)


if __name__ == '__main__':
    template()
    handle_comparison(open_comparison_table())

    data_font_mod = handle_cut(open_word_mod())
    with open("d.hex", "r+b") as fp:

        write_word_mod(data_font_mod, fp)

    fp.close()
    # comparison_list = handle_comparison(open_comparison_table())
    #
    # for i in range(0, len(comparison_list)):
    #     if comparison_list[i] != comparison_list[-1]:
    #         if comparison_list[i] == comparison_list[i+1]:
    #             print(i, comparison_list[i])

