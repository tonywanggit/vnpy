# -*- coding: utf-8 -*-
# @Time    : 2019/9/20 9:15
# @Author  : Tony
"""行情数据接口"""
from vnpy.trader.mddata.dataapi import MdDataApi
from vnpy.trader.mddata.jqdata import jqdata_client
from vnpy.trader.mddata.rqdata import rqdata_client
from vnpy.trader.setting import SETTINGS

if SETTINGS["mddata.api"] == "jqdata":
    mddata_client: MdDataApi = jqdata_client
else:
    mddata_client: MdDataApi = rqdata_client
