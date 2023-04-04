# This script is used as a price helper when shopping on uniqlo.com
# see origin website at https://h.uniqlo.cn/home/c_mobile/1292471262

import requests
import json
import prettytable
import time

# boy girl
type = 'boy'

# how many products will probe
maxSize = 200
# sleep some time for per product
sleep_time_per_product = 0.12
# some filters for products
filters = ['isExpress']
# filters = []
# origin price must in this range
origin_price_range = [200, 9999]
# current price must in current range
current_price_range = [0, 120]
# min discount rate we can accept
min_discount_rate = 0.6
# size of product name we want to show
product_name_max_len = 20
# black list for product list
product_name_black_list = ["孕妇", "裤"]


apis = {
    "search":  "https://d.uniqlo.cn/h/hmall-sc-service/search/searchWithCategoryCodeAndConditions/zh_CN",
    "detail": "https://h.uniqlo.cn/product?pid=",
    "express_detail": 'https://d.uniqlo.cn/h/stock/stock/query/zh_CN'
}

search_params_boy = {
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

search_params_girl = {
    "pageInfo": {
        "page": 1,
        "pageSize": 999
    },
    "categoryCode": "1292471261",
    "insiteDescription": "",
    "color": [],
    # 尺码
    "size": [],
    "season": [],
    "material": [],
    # 超值精选
    "identity": [
        "concessional_rate"
    ],
    # 分类
    "sex": [
        "女装"
    ],
    # 销量排序
    "rank": "sales",
    # 价格区间
    "priceRange": {
        "low": 30,
        "high": 300
    }
}

search_params = search_params_boy if type == 'boy' else search_params_girl

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


def printTable(p_list, fields):
    table = prettytable.PrettyTable()
    table.field_names = fields
    for item in p_list:
        table.add_row(list(map(lambda field: item[field], fields)))
    table.set_style(prettytable.MSWORD_FRIENDLY)
    table.align["productName"] = "l"
    print(table)


def filter_process(product):
    next = True
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
    if 'isExpress' in filters and next:
        res = requests.get(
            "https://d.uniqlo.cn/h/product/i/product/spu/h5/query/" + product["productCode"] + "/zh_CN", headers=common_headers).json()
        if not res["success"]:
            next = False
        else:
            summary = res["resp"][0]["summary"]
            if not summary:
                next = False
            else:
                isExpress = summary['isExpress'] == 'Y'
                next = isExpress

    return next


def hit_product_name_black_list(name):
    hit = False
    for word in product_name_black_list:
        if word in name:
            hit = True
            break
    return hit


def main():
    search_res = requests.post(
        apis["search"], data=json.dumps(search_params), headers=common_headers).json()
    if not search_res['success']:
        log("Request search list failed")
        exit(0)
    p_list = search_res["resp"][1]
    log(str(len(p_list)) + ' products found')

    attrs_to_delete = ["categoryCode", "stores"]
    for item in p_list:
        for attr in attrs_to_delete:
            del item[attr]
        item["concessional_rate"] = round(
            (item["originPrice"] - item["minPrice"]) / item["originPrice"], 4)
    p_list = list(filter(lambda item: item["stock"] == "Y", p_list))
    p_list = list(filter(lambda item: item["originPrice"] in range(
        origin_price_range[0], origin_price_range[1]), p_list))
    p_list = list(filter(lambda item: item["minPrice"] in range(
        current_price_range[0], current_price_range[1]), p_list))
    p_list = list(
        filter(lambda item: item["concessional_rate"] >= min_discount_rate, p_list))
    p_list = list(filter(lambda item: (not hit_product_name_black_list(
        item["productName4zhCN"])), p_list))
    p_list.sort(key=lambda item: item["concessional_rate"], reverse=True)
    log(str(len(p_list)) + ' products has stock, origin prices ranges in ' +
        str(origin_price_range[0]) + ' and ' + str(origin_price_range[1]) + ', current prices ranges in ' +
        str(current_price_range[0]) + ' and ' + str(current_price_range[1]) + ', discount rate at lease ' + str(min_discount_rate))

    top_list = []
    # we want more top products for filter
    log('look for front ' + str(maxSize) + ", filters are " + str(filters))
    for item in p_list[0:maxSize]:
        if not filter_process(product=item):
            # log("product " + item["productCode"] + ' has been filtered')
            continue
        url = apis["detail"] + item["productCode"]
        top_list.append(
            {"url": url, "discount_rate": item["concessional_rate"], "price": item["minPrice"], "originPrice": item["originPrice"], "productName": item["productName4zhCN"][:product_name_max_len]})
        # sleep some time not to effect services
        time.sleep(sleep_time_per_product)
    if not len(top_list):
        log('not products found')
    else:
        printTable(p_list=top_list, fields=[
            'productName', 'price', 'originPrice',  'discount_rate', 'url'])


def log(msg):
    print("[uniqlo_helper] " + msg + '.')


if __name__ == '__main__':
    main()
