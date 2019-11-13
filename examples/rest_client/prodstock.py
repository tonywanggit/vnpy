# -*- coding: utf-8 -*-
# @Time    : 2019/11/12 16:51
# @Author  : Tony
"""Description"""
import json
import time

from vnpy.api.rest import RestClient, Request

PRODUCT_API = "http://productmanager.iapi.ymatou.com"
PRODUCT_QUERY_API = "http://productquery.iapi.ymatou.com"


class ProductStockClient(RestClient):

    def __init__(self):
        super().__init__()
        self.init(PRODUCT_API)
        self.start()

    def sign(self, request: Request):
        request.headers = {"Content-Type": "application/json"}
        if request.method == "POST":
            if request.data:
                request.data = json.dumps(request.data)
        return request

    def update_stock(self, seller_id, catalog_id, stock):
        self.add_request(
            method="POST",
            path="/api/SellerProduct/UpdateStockBySku",
            callback=self.on_update_stock,
            data={"sellerId": seller_id,
                  "skuStocks": [{
                      "catalogId": catalog_id,
                      "num": stock
                  }]}
        )

    def on_update_stock(self, _, request):
        print(request)


class ProductQueryClient(RestClient):

    def __init__(self, prod_stock_client: ProductStockClient, not_op_products):
        super().__init__()
        self.init(PRODUCT_QUERY_API)
        self.start()
        self.prod_stock_client = prod_stock_client
        self.not_op_products = not_op_products
        self.not_stock_catalogs = []
        self.stock_catalogs = []

    def sign(self, request: Request):
        request.headers = {"Content-Type": "application/json"}
        if request.method == "POST":
            if request.data:
                request.json_data = request.data
                request.data = json.dumps(request.data)
        return request

    def query(self, catalog_id, return_stock):
        self.add_request(
            method="POST",
            path="/api/Product/GetCatalogListByCatalogIdList",
            callback=self.on_query_data,
            data={"CatalogIdList": [catalog_id], "ReturnStock": return_stock}
        )

    def on_query_data(self, data, request: Request):
        if data["Code"] != 200:
            return

        if data["Data"] and data["Data"]["ProductList"] and data["Data"]["ProductList"][0]:
            stock_num = data["Data"]["ProductList"][0]["CatalogStockNum"]
            product_id = data["Data"]["ProductList"][0]["ProductId"]
            catalog_id = data["Data"]["ProductList"][0]["CatalogId"]
            seller_id = data["Data"]["ProductList"][0]["SellerId"]
            return_stock = request.json_data["ReturnStock"]

            print(catalog_id, seller_id, return_stock, stock_num)

            if product_id in self.not_op_products:
                self.not_stock_catalogs.append(f"{product_id},{catalog_id},{stock_num},{return_stock}")
                return

            if stock_num <= return_stock:
                self.not_stock_catalogs.append(f"{product_id},{catalog_id},{stock_num},{return_stock}")
                return

            self.stock_catalogs.append(f"{product_id},{catalog_id},{stock_num},{return_stock}")
            self.prod_stock_client.update_stock(seller_id, catalog_id, stock_num - return_stock)


if __name__ == '__main__':
    print("end")
    # fo = open("d:/usr/temp/return_product_2.txt", "r")
    # lines = [x.replace('\n', '').split(',') for x in fo.readlines()]
    # fo.close()
    #
    # not_op_products = []
    # fo = open("d:/usr/temp/not_op_products.txt", "r")
    # not_op_products = [x.replace('\n', '') for x in fo.readlines()]
    # fo.close()

    # client = ProductStockClient()
    # query_client = ProductQueryClient(client, not_op_products)
    #
    # for line in lines:
    #     seller_id = int(line[0])
    #     product_id = line[2]
    #     catalog_id = line[3]
    #     stock = int(line[5])
    #     stock_muti = int(line[6])
    #     query_client.query(catalog_id, (stock_muti - 1) * stock)
    #     time.sleep(0.1)
    #
    # query_client.join()
    # client.join()
    #
    # fo = open("d:/usr/temp/no_stock_catalogs.txt", "w")
    # for line in query_client.not_stock_catalogs:
    #     fo.write(line + "\n")
    # fo.close()
    #
    # fo = open("d:/usr/temp/stock_catalogs.txt", "w")
    # for line in query_client.stock_catalogs:
    #     fo.write(line + "\n")
    # fo.close()
