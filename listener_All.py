import json
import os
from datetime import datetime

from DrissionPage._pages.chromium_page import ChromiumPage
from loguru import logger

from tiktok_test import get_page

ROOT_PATH = 'listener_data'
formatted_time = datetime.now().strftime("%Y-%m-%d---%H_%M_%S")
logger.add(f'{ROOT_PATH}/logs/{formatted_time}.log', format="{time} {level} {message}", level="INFO")


def save_to_json(origin_json, function_name, user_name):
    # 设置json数据包存储位置，按照采集用户名存储
    save_current_time = datetime.now().strftime("%Y-%m-%d---%H_%M_%S")

    fin_path = f'./{ROOT_PATH}/{function_name}/{user_name}'
    os.makedirs(fin_path, exist_ok=True)
    with open(f'{fin_path}/{function_name}---{save_current_time}.json', 'w', encoding='utf8') as f:
        json.dump(origin_json, f, ensure_ascii=False, indent=4)


def listener_tiktok_fans(tiktok_fans_page: ChromiumPage):
    tiktok_fans_page.listen.start('www.tiktok.com/api/user/list/?WebIdLastTime')  # 开始监听，指定获取包含该文本的数据包

    logger.info('开始监听')
    username = tiktok_fans_page.url.split('@')[-1]
    count = 1
    for packet in tiktok_fans_page.listen.steps():
        temp_json = packet.response.body
        try:
            temp = temp_json['userList'][0]
            save_to_json(temp_json, 'tiktok_fans', username)
            logger.info(f'监听到第{count}个数据包')
            count += 1
        except Exception as e:
            logger.error(f'当前数据包没有用户列表')
            pass


if __name__ == '__main__':
    user_id = 'jf8r69r'
    main_page = get_page(user_id)
    listener_tiktok_fans(main_page)
