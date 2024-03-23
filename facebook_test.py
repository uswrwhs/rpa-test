import datetime
import json
import os
import time

import pyotp
import requests
from DrissionPage._pages.chromium_page import ChromiumPage
from DrissionPage.common import from_selenium
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

ROOT_PATH = 'other/test'
LOG_PATH = f'./{ROOT_PATH}/logs'

# 设置日志文件名和格式 日志文件按不同日期分别存放
formatted_time = datetime.datetime.now().strftime("%Y-%m-%d---%H_%M_%S")
current_data = datetime.datetime.now().strftime("%Y-%m-%d")
os.makedirs(f'{LOG_PATH}/{current_data}', exist_ok=True)
logger.add(f'{LOG_PATH}/{current_data}/{formatted_time}.log', format="{time} {level} {message}", level="INFO")


class Run():
    def __init__(self):
        self.finger_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.finger_url = 'http://local.adspower.com:50325'

    # 根据对应user_id打开对应窗口
    def start_userID(self, start_user_id):
        url = f'{self.finger_url}/api/v1/browser/start'
        data = {'user_id': start_user_id}
        res = requests.get(url, headers=self.finger_headers, params=data)
        if res.status_code == 200:
            res_result = json.loads(res.text)
            if res_result["msg"] == "Success" or res_result["msg"] == "success":
                # 注意：下面两个参数必须传给selenium才能 启动指纹浏览器
                selenium_webdriver_su = res_result["data"]["webdriver"]
                selenium_address_su = res_result["data"]["ws"]["selenium"]
                logger.info(res_result)
                return selenium_webdriver_su, selenium_address_su, start_user_id
        else:
            logger.info(f'启动对应user_id指纹浏览器失败, 状态码:{res.status_code}')

    def start_selenium(self, selenium_webdriver_start, selenium_address_start, user_id_start):
        logger.info(f'当前执行窗口--{user_id_start}')
        chrome_option = Options()
        service = Service(selenium_webdriver_start)
        chrome_option.add_experimental_option("debuggerAddress", selenium_address_start)  # 这行命令必须加上，才能启动指纹浏览器

        driver = webdriver.Chrome(service=service, options=chrome_option)

        # driver.close()

        # driver.maximize_window()
        page_start = from_selenium(driver)
        page_start.set.window.normal()

        # 创建文件夹
        os.makedirs(f'./{ROOT_PATH}/{user_id_start}', exist_ok=True)

        return page_start


def get_page(get_user_id):
    r = Run()

    selenium_webdriver, selenium_address, get_user_id = r.start_userID(get_user_id)
    origin_page = r.start_selenium(selenium_webdriver, selenium_address, get_user_id)

    return origin_page


def face_init(init_page: ChromiumPage, email_init, pwd_init,fa_two_init):
    def get_faTwo_code(fa_2):
        # 创建一个TOTP对象
        totp = pyotp.TOTP(fa_2)
        # 生成当前时间的验证码
        return totp.now()

    init_page.get('https://mbasic.facebook.com/login.php')

    init_page.ele('#m_login_email').input(email_init)
    init_page.ele('tag:input@name=pass').input(pwd_init)

    # 登陆账号
    init_page.ele('tag:input@name=login').click()
    fa_2_code=get_faTwo_code(fa_two_init)


if __name__ == '__main__':
    # 记录开始时间
    start_time = time.time()

    main_user_id = 'jfdfetk'
    page_main = get_page(main_user_id)

    email = 'qllbkegsas@rambler.ru'
    pwd = 'E75l8#8XaO!U'
    fa_two = 'GBWID44ZKESXDV7ZNDIRW75RY4YPFCPU'
    face_init(page_main, email, pwd, fa_two)

    # 记录结束时间
    end_time = time.time()

    # 计算运行时间
    elapsed_time = end_time - start_time
    logger.info(f"程序运行时间：{elapsed_time}秒")
    # print([1,2,4,5,6][:-1])
