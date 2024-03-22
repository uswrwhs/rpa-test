import math
import time

from DownloadKit import DownloadKit
from DrissionPage import ChromiumPage
from loguru import logger

global_set = set()


def download_start(image_url_list):
    for i in range(math.ceil(len(image_url_list) / 5)):
        temp = i * 5
        d = DownloadKit()
        try:
            d.add(image_url_list[temp], goal_path='image_downloader')
            d.add(image_url_list[temp + 1], goal_path='image_downloader')
            d.add(image_url_list[temp + 2], goal_path='image_downloader')
            d.add(image_url_list[temp + 3], goal_path='image_downloader')
            d.add(image_url_list[temp + 4], goal_path='image_downloader')
        except IndexError as e:
            break
        time.sleep(2)


def image_downloader():
    url = 'https://mbasic.facebook.com/'
    page = ChromiumPage(9222)
    page.set.download_path('./image_downloader_facebook')
    # page.get(url)
    # # 读取编号转id的json文件
    # with open('pinterest_cookies.json', 'r', encoding='utf8') as f:
    #     tran_json = json.load(f)
    # page.set.cookies(tran_json)
    # page.refresh()
    # global global_set
    # while True:
    #     main_box = page.wait.ele_loaded('tag:div@role=list', timeout=120)
    #     temp_box = main_box.eles('tag:div@role=listitem')
    #     download_urls = []
    #     for element in temp_box:
    #         temp_url = element.ele('tag:img').attr('src')
    #         if temp_url not in global_set:
    #             download_urls.append(temp_url)
    #             global_set.add(temp_url)
    #
    #     download_start(download_urls)
    #
    #     page.scroll.to_bottom()
    #     page.wait(5, 10)

    page.listen.start('https://scontent-yyz1-1.xx.fbcdn.net/v/t39.30808-6/433')  # 开始监听，指定获取包含该文本的数据包
    # page.get('https://gitee.com/explore/all')  # 访问网址

    d = DownloadKit()
    count = 1
    from datetime import datetime as dt
    for packet in page.listen.steps():
        # print(packet.url)  # 打印数据包url
        logger.info(f'正在下载第{count}张图片')
        d.add(packet.url, goal_path='image_downloader', rename=dt.now().strftime("%Y-%m-%d-%H-%M-%S-%f") + '.jpg',
              suffix='')
        count += 1
        page.scroll.down(40)


def test1():
    url = 'https://www.baidu.com'
    page = ChromiumPage(9222)
    # page.set.download_path('./image_downloader_facebook')
    # page.get(url)
    input_box = page.ele('#kw')
    # input_box.input(Keys.BACKSPACE, clear=False)
    page.run_js("arguments[0].value = arguments[0].value.slice(0, -1);", input_box)


if __name__ == '__main__':
    # image_downloader()

    test1()
    # x=[1,2,5,4,7,8,9,6,4,77]
    # print(x[-1])
