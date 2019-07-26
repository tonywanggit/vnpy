# -*- coding: utf-8 -*-
# @Time    : 2019/7/9 19:07
# @Author  : Tony
"""Description"""
import json

from api.rest import Request
from vnpy.api.rest import RestClient

TOKEN_CLEAN_URL = "http://auth.iapi.ymatou.com"


class TokenClient(RestClient):

    def __init__(self):
        super().__init__()
        self.init(TOKEN_CLEAN_URL)
        self.start()

    def sign(self, request: Request):
        request.headers = {"Content-Type": "application/json"}
        if request.method == "POST":
            if request.data:
                request.data = json.dumps(request.data)
        return request

    def clean_token(self, user_id):
        self.add_request(
            method="POST",
            path="/api/token/delete",
            callback=self.on_clean_token,
            data={"UserId": user_id}
        )

    @staticmethod
    def on_clean_token(_, request):
        print(request)


if __name__ == '__main__':
    fo = open("d:/usr/temp/clean_token_user_id.txt", "r")
    lines = [int(x.replace('\n', '')) for x in fo.readlines()]
    fo.close()
    print(lines)

    # token_client = TokenClient()
    # for user_id in lines:
    #     token_client.clean_token(user_id)
    # token_client.join()




