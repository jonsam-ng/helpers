'''
Author: jonsam jonsam.ng@foxmail.com
Date: 2023-04-13 23:14:37
LastEditors: jonsam jonsam.ng@foxmail.com
LastEditTime: 2023-04-14 00:29:14
FilePath: /tools/runba-helper/check-in.py
Description: Auto check in runba.cyou
'''

# Here is an example of how to set up a daily task using cron:
# 1. Open the terminal and type "crontab -e" to edit your user's crontab file.
# 2. Add a new line to the crontab file with the following format:
# 0 8 * * * /usr/bin/python /path/to/your/script.py
# 3. Save and exit the crontab file.

import requests
import time
import json
from os import path

headers = {
    "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    "referer": "https://cdn.runba.cyou/user",
    "origin": "https://cdn.runba.cyou"
}

apis = {
    "checkin": "https://cdn.runba.cyou/user/checkin"
}


with open(path.abspath('conf.json')) as f:
    keys = json.load(f)


def main():
    for i, cookie in enumerate(keys["cookies"]):
        headers['Cookie'] = cookie
        res = requests.post(apis['checkin'], headers=headers).json()
        time.sleep(0.5)
        success = res['ret'] == 1
        print(str(i) + ' - ' + 'Check in ' + "success" if success else 'failed' +
              ", msg: " + res['msg'] + '.')


if __name__ == '__main__':
    main()
