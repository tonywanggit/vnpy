# -*- coding: utf-8 -*-
# @Time    : 2019/11/13 8:58
# @Author  : Tony
"""Description"""
import re

if __name__ == '__main__':
    fo = open("d:/usr/temp/product_manager.log", "r")
    lines = [x.replace('\n', '') for x in fo.readlines()]
    fo.close()

    fo = open("d:/usr/temp/product_manager_stock.txt", "w")
    for line in lines:
        match_result = re.match(r'.*sellerId":(\d+),.*catalogId":"(.*?)".*num":(\d+).*', line, re.M | re.I)
        fo.write(f"{match_result.group(1)},{match_result.group(2)},{match_result.group(3)}\n")
    fo.close()
