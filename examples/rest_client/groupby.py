# -*- coding: utf-8 -*-
# @Time    : 2020/2/5 17:12
# @Author  : Tony
"""Description"""

from itertools import groupby


if __name__ == '__main__':
    lst = [2, 2, 11]
    group_list = [(k, len(list(g))) for k, g in groupby(sorted(lst), key=lambda x: x)]

    for key, cnt in group_list:
        print(key, cnt)
