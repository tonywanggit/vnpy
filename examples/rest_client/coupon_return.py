# -*- coding: utf-8 -*-
# @Time    : 2019/11/25 10:33
# @Author  : Tony
"""批量返券"""
import json

from typing import Optional

from vnpy.api.rest import RestClient, Request

COUPON_API_URL = "http://coupon.iapi.ymatou.com"


class CouponClient(RestClient):

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

    def return_coupon(self, user_id, main_order_id, coupon_code):
        self.add_request(
            method="POST",
            path="/api/callback/returnCoupon",
            callback=self.on_callback,
            on_error=self.on_error,
            data={
                "appId": "stg.iapi.ymatou.com",
                "couponCodes": [coupon_code],
                "mainOrderId": main_order_id,
                "requestId": main_order_id,
                "userId": user_id
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
    fo = open("d:/usr/temp/coupon_return_userid_2.csv", "r")
    lines = [x.replace('\n', '').split(',') for x in fo.readlines()]
    fo.close()

    cnt = 0

    # client = CouponClient()
    # for line in lines:
    #     if line[2]:
    #         client.return_coupon(int(line[0]), line[1], line[2])
    #     # if line[3]:
    #     #     client.return_coupon(int(line[0]), line[1], line[3])
    #     break
    #
    # client.join()

    print("return_coupon")
