import datetime
import json
import os
import time

import pyotp
import requests
from DrissionPage._pages.chromium_page import ChromiumPage
from DrissionPage._units.actions import Actions
from DrissionPage.common import from_selenium
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import facebook_caption

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
        page_start.set.window.max()
        page_start.set.window.mini()
        page_start.set.timeouts(10)
        # 开启平滑滚动，滚动结束后进行下一步操作
        page_start.set.scroll.smooth(on_off=True)
        page_start.set.scroll.wait_complete(on_off=True)

        # 创建文件夹
        os.makedirs(f'./{ROOT_PATH}/{user_id_start}', exist_ok=True)

        return page_start


def get_page(get_user_id):
    r = Run()

    selenium_webdriver, selenium_address, get_user_id = r.start_userID(get_user_id)
    origin_page = r.start_selenium(selenium_webdriver, selenium_address, get_user_id)

    return origin_page


def face_init(page_init: ChromiumPage, email_init, pwd_init, fa_two_init):
    def get_faTwo_code(fa_2):
        # 创建一个TOTP对象
        totp = pyotp.TOTP(fa_2)
        # 生成当前时间的验证码
        return totp.now()

    page_init.get('https://mbasic.facebook.com/login.php')
    # 输入邮箱和密码
    page_init.ele('#m_login_email').input(email_init)
    page_init.ele('tag:input@name=pass').input(pwd_init)
    # 点击登录
    page_init.ele('tag:input@name=login').click()
    fa_2_code = get_faTwo_code(fa_two_init)
    fa2_code_box = page_init.wait.ele_loaded('#approvals_code', timeout=10)
    if fa2_code_box:
        fa2_code_box.input(fa_2_code)
    # 提交验证码
    page_init.ele('#checkpointSubmitButton-actual-button', timeout=5).click()
    # 继续
    page_init.ele('#checkpointSubmitButton-actual-button', timeout=5).click()
    # 前往首页
    while True:
        page_init.wait(3, 5)
        try:
            jinxu = page_init.wait.ele_loaded('tag:a@@text()=继续', timeout=10)
            if jinxu:
                jinxu.click()
            else:
                break
        except:
            continue
    page_init.wait.doc_loaded(timeout=10)
    page_init.wait(5, 7)
    ac_init = Actions(page_init)
    ac_init.move_to((300, 20)).click()

    # 进入新版facebook主页
    page_init.get('https:www.facebook.com')
    page_init.wait(3, 5)
    ac_init = Actions(page_init)

    # 确认记住密码
    confirmSavePassword = page_init.ele('css:[role="button"]>[role="none"]>[role="none"]', index=1, timeout=10)
    ac_init.move_to(confirmSavePassword).click()


def set_image_to_clipboard(image_path):
    import win32clipboard as wc
    import win32con
    from PIL import Image

    image = Image.open(image_path)
    # 将图片转换为位图格式
    image = image.convert('RGB')
    width, height = image.size
    image_data = image.tobytes()

    # 创建位图对象
    bitmap_info = {
        'bmiHeader': {
            'biSize': 40,
            'biWidth': width,
            'biHeight': height,
            'biPlanes': 1,
            'biBitCount': 24,
            'biCompression': 0,
            'biSizeImage': len(image_data),
            'biXPelsPerMeter': 0,
            'biYPelsPerMeter': 0,
            'biClrUsed': 0,
            'biClrImportant': 0
        },
        'bitmapColors': []
    }

    # 将字典转换为字节串
    bitmap_info_bytes = bytes(str(bitmap_info), 'utf-8')

    # 设置剪贴板内容
    wc.OpenClipboard()
    wc.EmptyClipboard()
    wc.SetClipboardData(win32con.CF_DIB, bitmap_info_bytes + bytes(bitmap_info['bitmapColors']) + image_data)
    wc.CloseClipboard()

if __name__ == '__main__':
    # 记录开始时间
    start_time = time.time()

    main_user_id = 'jfdfett'
    # 'jfdfets'
    page_main = get_page('jfdfett')
    page_main.wait(3, 5)

    # 打开图片文件
    # 使用方法：将图片路径替换为你需要复制的图片路径
    # set_image_to_clipboard("./images.jpg")

    facebook_caption.send_message(page_main, main_user_id)

    # 登陆测试1
    # email = 'qllbkegsas@rambler.ru'
    # pwd = 'E75l8#8XaO!U'
    # fa_two = 'GBWID44ZKESXDV7ZNDIRW75RY4YPFCPU'

    # 登陆测试2
    # email = 'zavaydmvdm@rambler.ru'
    # pwd = 'd65t5#7Y9l#F'
    # fa_two = 'UJCXI32UPBGT5TX7KQQS7WTJLIAPVOIH'
    # face_init(page_main, email, pwd, fa_two)
    #
    # x = 1 / 0

    # 刷帖测试 在主页刷帖
    # ac = Actions(page_main)
    #
    # logger.info(f'{main_user_id}进入视频界面')
    # mian_video_lick = page_main.eles('tag:div@aria-label=赞')
    # # temp_index=1
    # for like_box in mian_video_lick:
    #     if like_box.states.has_rect is not False:
    #         like_box.click()
    #         break
    # logger.info('给主视频点赞')
    #
    # main_Feed = page_main.ele('tag:div@data-pagelet=MainFeed', timeout=10)
    # like_box = main_Feed.eles('tag:div@aria-label=赞')
    # page_main.scroll.down(300)
    #
    # like_sure = False
    # for i in range(3, 200):
    #     video_box = page_main.ele('tag:video', index=i)
    #     if video_box is False or video_box.states.has_rect is False:
    #         continue
    #     page_main.scroll.to_see(video_box)
    #     ac.move_to(video_box)
    #     if 0.5 < random.random() < 0.9 or like_sure:
    #         logger.info('正在点赞')
    #         like_box = main_Feed.ele('tag:video', index=i)
    #         if like_box is False or like_box.states.has_rect is False:
    #             like_sure = True
    #             continue
    #         ac.move_to(like_box).click()
    #     page_main.scroll.down(350)
    # ac.scroll(0, 200)
    # return False, all_like_count

    # facebook_caption.brushPost(page_main, main_user_id)

    # 记录结束时间
    end_time = time.time()

    # 计算运行时间
    elapsed_time = end_time - start_time
    logger.info(f"程序运行时间：{elapsed_time}秒")
    # print([1,2,4,5,6][:-1])
