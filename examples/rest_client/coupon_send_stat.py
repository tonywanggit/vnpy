# -*- coding: utf-8 -*-
# @Time    : 2019/11/25 10:33
# @Author  : Tony
"""批量发券统计"""
import json
import time

from itertools import groupby
from typing import Optional

from vnpy.api.rest import RestClient, Request

COUPON_API_URL = "http://coupon.iapi.ymatou.com"

COUPON_STAT = []

class CouponInfoClient(RestClient):

    def __init__(self):
        super().__init__()
        self.init(COUPON_API_URL)
        self.start()

    def sign(self, request: Request):
        request.headers = {"Content-Type": "application/json"}
        if request.method == "POST":
            if request.data:
                request.json_data = request.data
                request.data = json.dumps(request.data)
        return request

    def get_coupon(self, user_id, batch_code, cnt):
        self.add_request(
            method="POST",
            path="/api/Promotion/getUserCouponInfosByBatch",
            callback=self.on_callback,
            on_error=self.on_error,
            data={
                "appId": "stg.iapi.ymatou.com",
                "batchCode": batch_code,
                "userId": user_id,
                "cnt": cnt
            }
        )

    @staticmethod
    def on_callback(response, request: Request):
        if response and response["data"] and response["data"]["couponInfos"]:
            coupon_list = response["data"]["couponInfos"]
            send_cnt = int(request.json_data["cnt"])
            recv_cnt = len(coupon_list)

            if recv_cnt < send_cnt:
                COUPON_STAT.append((request.json_data["userId"], request.json_data["batchCode"], send_cnt, recv_cnt))

    @staticmethod
    def on_error(
            exception_type: type,
            exception_value: Exception,
            tb,
            request: Optional[Request],
    ):
        print(exception_type, exception_value, request)


if __name__ == '__main__':
    fo = open("d:/usr/temp/coupon_20200205_all.csv", "r")
    lines = [x.replace('\n', '').split(',') for x in fo.readlines()]
    fo.close()

    client = CouponInfoClient()
    for line in lines:
        user_id = int(line[0])
        batch_codes = [x for x in line[1:] if x]
        batch_codes_group = [(k, len(list(g))) for k, g in groupby(sorted(batch_codes), key=lambda x: x)]

        for batch_code, cnt in batch_codes_group:
            # client.get_coupon(user_id, batch_code, cnt)
            time.sleep(0.1)
    client.join()

    print(COUPON_STAT)
    print("send_coupon_stat finish")
