# This script is used as a price helper when shopping on uniqlo.com
# see origin website at https://h.uniqlo.cn/home/c_mobile/1292471262

import requests
import json
import prettytable
import time


apis = {
    "search":  "https://d.uniqlo.cn/h/hmall-sc-service/search/searchWithCategoryCodeAndConditions/zh_CN",
    "detail": "https://h.uniqlo.cn/product?pid=",
    "express_detail": 'https://d.uniqlo.cn/h/stock/stock/query/zh_CN'
}

search_params = {
    "pageInfo": {
        "page": 1,
        "pageSize": 999
    },
    "categoryCode": "1292471262",
    "insiteDescription": "",
    "color": [],
    # 尺码
    "size": [
        "SMA003",
        "SMA004",
        "SMA005"
    ],
    "season": [],
    "material": [],
    # 超值精选
    "identity": [
        "concessional_rate"
    ],
    # 分类
    "sex": [
        "男装"
    ],
    # 销量排序
    "rank": "sales",
    # 价格区间
    "priceRange": {
        "low": 0,
        "high": 300
    }
}

common_headers = {
    "authorization": "bearer",
    "content-type": "application/json",
    "origin": "https://h.uniqlo.cn",
    "referer": "https://h.uniqlo.cn/",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
}

maxSize = 80
sleep_time_per_product = 0.15


def printTable(p_list, fields):
    table = prettytable.PrettyTable()
    table.field_names = fields
    for item in p_list:
        table.add_row(list(map(lambda field: item[field], fields)))
    table.set_style(prettytable.MSWORD_FRIENDLY)
    table.align["productName"] = "l"
    print(table)


def filter_process(product):
    # has stock process
    # res = requests.post(apis["express_detail"], data=json.dumps({
    #     "type": "DETAIL",
    #     "distribution": "EXPRESS",
    #     "productCode": product["productCode"]
    # }), headers=common_headers).json()
    # if not res["success"]:
    #     return False
    # detail = res["resp"][0]
    # if not detail:
    #     return False
    # hasStock = detail["hasStock"] == "Y"
    # if hasStock:
    #     product['totalStock'] = detail['totalStock']
    # return hasStock

    # has express
    res = requests.get(
        "https://d.uniqlo.cn/h/product/i/product/spu/h5/query/" + product["productCode"] + "/zh_CN", headers=common_headers).json()
    if not res["success"]:
        return False
    summary = res["resp"][0]["summary"]
    if not summary:
        return False
    isExpress = summary['isExpress'] == 'Y'
    return isExpress


def main():
    search_res = requests.post(
        apis["search"], data=json.dumps(search_params), headers=common_headers).json()
    if not search_res['success']:
        log("Request search list failed")
        exit(0)
    p_list = search_res["resp"][1]
    attrs_to_delete = ["categoryCode", "stores"]
    for item in p_list:
        for attr in attrs_to_delete:
            del item[attr]
        item["concessional_rate"] = round(
            (item["originPrice"] - item["minPrice"]) / item["originPrice"], 4)
    p_list = list(filter(lambda item: item["stock"] == "Y", p_list))
    p_list.sort(key=lambda item: item["concessional_rate"], reverse=True)
    top_list = []
    # we want more top products for filter
    for item in p_list[0:maxSize]:
        if not filter_process(product=item):
            continue
        url = apis["detail"] + item["productCode"]
        top_list.append(
            {"url": url, "rate": item["concessional_rate"], "price": item["minPrice"], "originPrice": item["originPrice"], "productName": item["productName4zhCN"][:24]})
        # sleep some time not to effect services
        time.sleep(sleep_time_per_product)
    printTable(p_list=top_list, fields=[
               'productName', 'price', 'originPrice',  'rate', 'url'])


def log(msg):
    print("[uniqlo_helper] " + msg)


if __name__ == '__main__':
    main()
