import re
import struct
import numpy as np
import threading
import os

max_buf = 0
data_list_address_f = []
data_word_mod_f = []
bitmap_data_list = []
font_w_h_s = []
bitmap_data_list_cal = []
zero_num = 0
content_all_text = ""


def change_file(max_num):
    with open("font_change_c.c", 'r', encoding='utf-8') as f:
        content = f.read()
    start = content.find('glyph_bitmap[]')
    end = content.find('};', start)
    str_mod = content[start:end+2]
    content = content.replace(str_mod, "glyph_bitmap[] = {};")

    start = content.find('glyph_dsc[]')
    end = content.find('};', start)
    bitmap = content[start: end+2]

    str1 = 'glyph_dsc[] ={};\n' + f'static int32_t bitmap_list[] = {{{", ".join(map(str, bitmap_data_list_cal))}}};'
    content = content.replace(bitmap, str1)

    start = content.find('uint16_t unicode_list_1[]')
    end = content.find('};', start)
    str_address = content[start:end+1]

    content_address = "uint16_t unicode_list_1[] = {{{}}}".format(", ".join(data_list_address_f))
    content = content.replace(str_address, content_address)

    start = content.find('lv_font_fmt_txt_dsc_t font_dsc')
    end = content.find('}', start)
    str_font_dsc = content[start:end+1]
    new_str_font_dsc = str_font_dsc + (";\nstatic FILE *font_fp = 0;\nstatic uint8_t __g_font_buf[MAX_BUF + 5];\nstatic u8 bin_font_size;\nstatic u8 *font_fp_buf=0")
    content = content.replace(str_font_dsc, new_str_font_dsc)

    start = content.find('static const uint8_t * __user_font_get_bitmap(const lv_font_t * font, uint32_t unicode_letter) {')
    end = content.find('return NULL;', start)
    end_2 = content.find('return &fdsc->glyph_bitmap[gdsc->bitmap_index];', start)
    str_add_text = content[start:end]
    str_add_text_add = content[start:end_2] + "return font_fp_buf;\n    }\n    "
    content = content.replace(str_add_text, str_add_text_add)

    start = content.find('dsc_out->adv_w = gdsc->adv_w;')
    end = content.find('dsc_out->bpp   = fdsc->bpp;', start)
    bitmap_text = content[start:end]

    str1 = 'if(!font_fp){\n            font_fp = fopen("storage/sd1/C/font/font.bin", "r");\n        }\n        if(font_fp){\n            int ret = fseek(font_fp, bitmap_list[i], SEEK_SET);\n            if(i == fdsc->cmaps[0].list_length - 1)\n                int len = fread(font_fp, __g_font_buf, FILE_SIZE - bitmap_list[i]);\n            else\n                int len  = fread(font_fp, __g_font_buf, bitmap_list[i + 1] - bitmap_list[i]);\n            font_fp_buf = &__g_font_buf[5];\n         }\n        dsc_out->adv_w = __g_font_buf[0];\n        dsc_out->box_h = __g_font_buf[1];\n        dsc_out->box_w = __g_font_buf[2];\n        dsc_out->ofs_x = __g_font_buf[3];\n        dsc_out->ofs_y = __g_font_buf[4];\n        '
    content = content.replace(bitmap_text, str1)

    content = content + "\nstatic u16 get_unicode(u16 idx){\n    return unicode_list_1[idx];\n}"

    start = content.find('#include')
    end = content.find('.h"', start)
    str_include = content[start:end+3]
    new_str_include = str_include + '\n#include "fs/fs.h"' + ('\n#define MAX_BUF       %s' % max_num) + ('\n#define FILE_SIZE       ')
    content = content.replace(str_include, new_str_include)
    global content_all_text
    content_all_text = content


def read_file():
    with open("font_change_c.c", 'r', encoding='utf-8') as f:
        content = f.read()

    start = content.find('unicode_list_1[]')
    end = content.find('};', start)
    data = content[start:end]
    global data_list_address_f
    data_list_address_f = re.findall(r'0x[0-9a-fA-F]+', data)

    start = content.find('glyph_bitmap[]')
    end = content.find('};', start)
    data = content[start:end]
    global data_word_mod_f
    data_word_mod_f = re.findall(r'0x[\da-fA-F]+', data)

    start = content.find('glyph_dsc[]')
    end = content.find('};', start)
    data = content[start:end]
    data = data.replace("glyph_dsc[] = {", "")

    result = re.findall(r"{[^{}]*}", data)
    output = []
    for item in result:
        numbers = re.findall(r"\d+", item)
        sublist = [int(num) for num in numbers]
        output.append(sublist)

    global font_w_h_s
    font_w_h_s = np.array(output)[:, 1:]

    global bitmap_data_list, bitmap_data_list_cal, zero_num

    bitmap_data_list = np.array(output)[:, 0]
    zero_num = np.count_nonzero(bitmap_data_list == 0) - 1

    bitmap_data_list_cal = np.arange(len(bitmap_data_list[zero_num:])) * 5 + bitmap_data_list[zero_num:]
    bitmap_data_list_cal = [0] * zero_num + bitmap_data_list_cal.tolist()

    for i in range(0, len(output)):
        if output[i] != output[-1]:
            output[i][0] = output[i+1][0] - output[i][0]
        else:
            output[i][0] = int((output[i][2] * output[i][1]) / 2)
    global max_buf
    array = np.array(output)
    max_buf = np.max(array[:, 0])


def write_word_mod(data_font_mod):
    filename = "font.bin"
    if "\ufeff" in data_font_mod[0]:
        data_font_mod[0] = data_font_mod[0].replace("\ufeff", "")
    data_list = np.array([int(x, 16) for x in data_font_mod])

    sublists = np.split(data_list, bitmap_data_list[1:])
    lst = font_w_h_s.tolist()
    result = [lst[i] + sublists[i].tolist() for i in range(len(sublists))][zero_num:]
    with open(filename, 'wb')as f:
        for sublist in result:
            for item in sublist:
                f.write(struct.pack("B", item))


if __name__ == "__main__":

    # read_file()
    #
    # write_word_mod(data_word_mod_f)
    # file_size = os.path.getsize("a.hex")
    # change_file(max_buf, file_size)

    read_file()

    thread1 = threading.Thread(target=write_word_mod, args=(data_word_mod_f,))
    thread2 = threading.Thread(target=change_file, args=(max_buf,))

    # 启动线程
    thread1.start()
    thread2.start()

    # 等待线程结束
    thread1.join()
    thread2.join()

    file_size = os.path.getsize('font.bin')
    with open('font.c', 'w', encoding='utf-8') as file_content:
        start = content_all_text.find("#define FILE_SIZE")
        content_all_text = content_all_text.replace(content_all_text[start:start+17], "#define FILE_SIZE        %s" % file_size)
        if file_size <= 65535:
            start = content_all_text.find("int32_t bitmap_list[]")
            content_all_text = content_all_text.replace(content_all_text[start:start+20], "int16_t bitmap_list[]")
        file_content.write(content_all_text)


