# @filename: vcf_card2.py
# -*- coding: utf-8 -*-
# @Author: Li Gang
# @Date:   2019-03-03 10:27:54
# @Last Modified by:   Li Gang
# @Last Modified time: 2019-03-04 11:21:14
# 把手机上导出的vcf电话簿解析出来存放在一个excel文件（phonebook.xls)中
#
import re
import xlwt
import pickle

pre = 'CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:'        # unicode encoded tag
catalog = ['FN', 'N', 'ORG', 'TEL', 'TITLE', 'PHOTO',
           'ADR', 'EMAIL', 'NOTE', 'X-QQ']              # pre-defined item name
catalog_cn =['姓', '名', '工作单位', '电话', '职位', '照片',
           '地址', '电邮', '备注', 'QQ号码']              # 中文对照
# filter for valid begnning of a line within a record
fil_str = '|^'.join(catalog)
filt_str_begin = rf'(^{fil_str})[;:]'
filt_begin_end = rf'^BEGIN|^END|^VERSION'   # section mark;version mark


# a generator to generate a record (a list of lines)
def read_record(fname):  
    record = []
    try:
        with open(fname, 'r') as f:
            while True:
                s = f.readline()
                if not s:
                    break
                if re.findall(filt_begin_end, s.strip()) == []:  # 是实际的信息
                    if re.findall(filt_str_begin, s) == []:      # 上一行未结束时有换行
                        record[-1] = record[-1] + s.strip()      # 加到前一行末尾
                    else:
                        record.append(s.strip())                 # 否则列表中新加一条
                if 'END' in s:
                    yield record
                    record = []
                # print(s.strip())
    except EOFError:
        return


# 解析一条记录的各个域，将结果用字典result_dic返回
def parse_record(rec):
    result_dic = {}
    for s in rec:
        y = re.findall(filt_str_begin, s)
        if y != []:
            head = y[0]
            k = s.find(pre)                                 # 将=XX=XX=XX形式的信息解码
            if k > -1:
                t = s[k + len(pre):]
                val = re.sub(r':|;|=|\s', '', t)
                info = bytes.fromhex(val).decode('utf-8')
            else:
                t = s[len(head):]
                info = re.sub(r':|;|=|\s', '', t)
            if 'HOME' in info or 'CELL' in info or 'WORK' in info or 'PREF' in info:  # 去掉电话前的这几个属性
                info = info[4:]
            # print(f'{head}--{info}')
            if head != 'PHOTO':                             # 不保存照片
                result_dic[head] = info
    return result_dic


# 这个函数干完所有活（总调度），把vcf文件中的记录取出来，放在一个列表中返回。
def get_all_records(fname):
    rec = read_record(fname)
    phonebook = []
    for r in rec:
        p = parse_record(r)
        phonebook.append(p)
    return phonebook


# 把号码簿列表book中的内容存入fwname命名的excel文件中('*.xls')
def save_to_xls(fwname, book):
    wbk = xlwt.Workbook()                           # 定义一个workbook对象
    sheet = wbk.add_sheet("通信录")                 # 新建一个sheet并命名
    # 先写表头
    i = 0
    for j, s in enumerate(catalog_cn):
        sheet.write(i, j, label=s)
    # 再写内容
    i = 1
    for p in book:
        for k, v in p.items():
            for j, s in enumerate(catalog):
                if s == k:
                    sheet.write(i, j, label=v)

        i += 1
    wbk.save(fwname)


# ###############主程序#######################
if __name__ == '__main__':
    fn = '00001.vcf'
    phonebook = get_all_records(fn)
    fwname = r'phonebook.xls'
    save_to_xls(fwname, phonebook)
    # 用 pickle 来实现持久化
    with open('phoneb.pickle', 'wb') as fout:
        pickle.dump(phonebook, fout)
    print('done!')
