# -*- coding: utf-8 -*-
# @Time    : 2019/11/25 10:33
# @Author  : Tony
"""批量发券"""
import json

from itertools import groupby
from typing import Optional

from vnpy.api.rest import RestClient, Request

COUPON_API_URL = "http://coupon.iapi.ymatou.com"


class CouponSendClient(RestClient):

    def __init__(self):
        super().__init__()
        self.init(COUPON_API_URL)
        self.start()

    def sign(self, request: Request):
        request.headers = {"Content-Type": "application/json"}
        if request.method == "POST":
            if request.data:
                request.data = json.dumps(request.data)
        return request

    def send_coupon(self, user_id, batch_code):
        self.add_request(
            method="POST",
            path="/api/Promotion/UserReceiveCoupon",
            callback=self.on_callback,
            on_error=self.on_error,
            data={
                "appId": "stg.iapi.ymatou.com",
                "batchCode": batch_code,
                "userId": user_id,
                "businessType": 1,
                "requestId": "REST-2020-0205-PYTHON"
            }
        )

    @staticmethod
    def on_callback(_, request):
        print(request)

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

    client = CouponSendClient()
    for line in lines:
        user_id = int(line[0])
        batch_codes = [x for x in line[1:] if x]
        batch_codes_group = [(k, len(list(g))) for k, g in groupby(sorted(batch_codes), key=lambda x: x)]

        print(user_id, batch_codes_group)

        # print(user_id, batch_codes)

    #     for batch_code in batch_codes:
    #         client.send_coupon(user_id, batch_code)
    #         print(user_id, batch_code)
    # client.join()
    #
    # print("send_coupon finish")
