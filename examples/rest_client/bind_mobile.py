# -*- coding: utf-8 -*-
# @Time    : 2019/7/9 19:07
# @Author  : Tony
"""Description"""
import json

from api.rest import Request
from vnpy.api.rest import RestClient

BASE_URL = "http://userservice.iapi.ymatou.com"


class BindMobileClient(RestClient):

    def __init__(self):
        super().__init__()
        self.init(BASE_URL)
        self.start()

    def sign(self, request: Request):
        request.headers = {"Content-Type": "application/json"}
        if request.method == "POST":
            if request.data:
                request.data = json.dumps(request.data)
        return request

    def bind_mobile(self, user_id, mobile):
        self.add_request(
            method="POST",
            path="/api/user/bindMobile",
            callback=self.on_clean_token,
            data={"UserId": user_id, "Mobile": mobile}
        )

    @staticmethod
    def on_clean_token(_, request):
        print(request)


if __name__ == '__main__':
    fo = open("d:/usr/temp/mobile.txt", "r")
    # lines = [int(x.replace('\n', '')) for x in fo.readlines()]
    lines = [x.replace('\n', '').split('\t') for x in fo.readlines()]
    fo.close()
    print(lines)

    client = BindMobileClient()
    for mobile, userId in lines:
        client.bind_mobile(userId, mobile)
    client.join()

    # token_client = TokenClient()
    # for user_id in lines:
    #     token_client.clean_token(user_id)
    # token_client.join()




