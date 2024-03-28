import datetime
import json
import math
import os
import random
import time

import requests
from DrissionPage._functions.keys import Keys
from DrissionPage._pages.chromium_page import ChromiumPage
from DrissionPage._units.actions import Actions
from DrissionPage.common import from_selenium
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from utils import my_utils
import tiktok_caption

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
        try:
            os.mkdir(f'./{ROOT_PATH}/{user_id_start}')
            logger.info('浏览器{}文件夹创建成功'.format(user_id_start))
        except:
            logger.info('浏览器{}文件夹已被创建'.format(user_id_start))
        # page.set_download_path()
        # page.download_path('./{}'.format(user_id))

        return page_start


def delete_ceshi(delete_test_page: ChromiumPage):
    title = delete_test_page.ele('tag:div@data-contents=true')

    title.input(clear=True, vals='luxury bag ')
    tag_set = {'gucci', 'chanel', 'fyp', 'foryoupage', 'tiktok', 'louis', 'vuitton', 'prada', 'bag', 'shoes'}
    tag_length = len(tag_set)

    temp_click = delete_test_page.ele('tag:span@@text()=Post a video to your account')
    # 创建ActionChains实例
    ac = Actions(delete_test_page)
    for_count = 0

    for _ in range(tag_length):
        tag = random.choice(list(tag_set))
        tag_set.remove(tag)
        title.input('#', clear=False)
        for char_i in tag[:-1]:
            title.input(char_i, clear=False)

        ac.move_to(temp_click).click()
        title.input(tag[-1], clear=False)

        while_count = 1
        replace_tag_flag = 0
        # return
        for next_i in range(3):
            enter_flag = delete_test_page.wait.ele_loaded('tag:div@class=mentionSuggestions', timeout=2)
            if enter_flag:
                enter_box = enter_flag.child('tag:div').child('tag:div')
                try:
                    enter_box.click()
                    for_count += 1
                except:
                    while_count += 1
                    continue
                break
            else:
                ac.type((Keys.CTRL, 'z'))
                if next_i == 2:
                    ac.type((Keys.CTRL, 'z'))
                else:
                    title.input(tag[-1], clear=False)

        if for_count == 5:
            break

    print(title.text)

    # 修改个人资料
    # tiktok_caption.modify_personal_data(page, user_id)
    # 发布视频
    # tiktok_caption.upload_video(page)

    # download_img()

    # img_valid()
    # os.mkdir('user_id')


def get_page(get_user_id):
    r = Run()

    selenium_webdriver, selenium_address, get_user_id = r.start_userID(get_user_id)
    origin_page = r.start_selenium(selenium_webdriver, selenium_address, get_user_id)

    return origin_page


def brushVideo(page_brush: ChromiumPage, brush_user_id):
    def exploreOrRefulsh(page_brush_explore: ChromiumPage, or_user_id):
        # 返回首页
        page_brush_explore.ele('tag:button@aria-label=Close').ele('tag:svg').click()

        if random.random() >= 0.5:
            # 前往explore界面刷视频
            explore_button = page_brush_explore.ele('tag:a@data-e2e=nav-explore', timeout=10).ele('tag:svg')
            explore_button.click()
            type_list = page_brush_explore.ele('tag:div@class:DivCategoryListWrapper', timeout=5).eles('tag:span')
            rand_type = random.randint(0, len(type_list) - 1)

            type_list[rand_type].click()
            # 随机点进一个视频
            video_list = (page_brush_explore.ele('tag:div@data-e2e=explore-item-list', timeout=10)
                          .eles('tag:div@data-e2e=explore-item', timeout=10))

            # 移动到视频并点击进入界面
            ac = Actions(page_brush_explore)
            rand_video = random.randint(0, len(video_list) - 1)
            ac.scroll(on_ele=video_list[rand_video])
            ac.move_to(ele_or_loc=video_list[rand_video])
            page_brush_explore.wait(3, 5)
            ac.click()

        else:
            logger.info(f'{or_user_id}首页刷新，继续从首页刷视频')
            page_brush_explore.ele('tag:a@data-e2e=nav-foryou', timeout=5).ele('tag:svg').click()
            # 刷新首页视频
            page_brush_explore.refresh()
            page_brush.wait.ele_loaded('tag:span@data-e2e=comment-icon', timeout=10).click()
        logger.info(f'{or_user_id}继续开始视频')

    # 进入视频界面
    start_flag = page_brush.wait.ele_loaded('tag:span@data-e2e=comment-icon', timeout=10)
    start_flag.click()

    func_start_time = time.time()
    cycle_time = random.uniform(10, 15) * 60

    like_count = 1
    video_count = 1

    # 刷视频，循环退出条件为达到规定时间
    temp_count = 1
    while True:
        page_brush.wait(5, 8)

        # 随机点赞 概率0.4
        if 0.4 < random.random() < 0.6:
            like_box = page_brush.ele('tag:span@data-e2e=browse-like-icon', timeout=10).ele('tag:svg')
            like_box.click()
            logger.info(f'{brush_user_id}正在点赞,已完成{like_count}个点赞')
            like_count += 1

        # 每个视频看10-15秒
        page_brush.wait(6, 8)
        current_endTime = time.time()

        running_time = current_endTime - func_start_time
        if running_time > cycle_time:
            logger.info(f'{brush_user_id}时间结束,正在结束流程，开始统计数据')
            logger.info(f'{brush_user_id}一共观看了{video_count}个视频，完成{like_count}次点赞,'
                        f'耗时{math.floor(running_time / 60)}分{math.ceil(running_time / 60)}秒')
            break
        # 点击进入下一个视频
        logger.info(f'{brush_user_id}准备进入下一个视频，目前已经观看了{video_count}个视频')
        video_count += 1
        logger.info(f'{brush_user_id}正在测试exploreOrRefulsh函数功能')

        # 测试用，直接进函数
        exploreOrRefulsh(page_brush, brush_user_id)

        try:
            page_brush.ele('tag:button@aria-label=Go to next video', timeout=5).ele('tag:svg').click()
        except:
            # 进入explore界面或者刷新主页视频
            logger.info(f'{brush_user_id}当前页面视频已经全部刷完，刷新主页或者进入explore页观看视频')
            exploreOrRefulsh(page_brush, brush_user_id)
        temp_count += 1
        if temp_count > 3:
            break
    # 回到首页
    page_brush.get('')
    logger.info(f'{brush_user_id}已经回到首页')
    return True


def getLive_user_id(page_brush: ChromiumPage):
    with open('txt_path/tiktok_browser_id.txt', 'r', encoding='utf8') as f:
        origin_browser_id_list = [line.strip() for line in f.readlines()]

    url = input("请输入直播间链接: ")
    port = input("请输入浏览器序号 (1-49): ")
    user_id_get = origin_browser_id_list[int(port)]

    page_brush.get(url)
    time.sleep(10)
    name_set = set()
    file_path = 'other/temp/name_dir'
    # 获取当前时间
    now = datetime.datetime.now()

    # 将时间格式化为指定格式
    formatted_time = now.strftime("%Y-%m-%d=%H_%M_%S")
    file_name = f'{formatted_time}--{user_id_get}.txt'
    with open(f'{file_path}/{file_name}', 'w', encoding='utf8') as f:
        f.write('')
    try:
        while True:
            try:
                # 点击用户卡片
                page_brush.ele('tag:div@class=tiktok-1pwimsz-DivBottomStickyMessageContainer e15mjof0').ele(
                    'tag:span@class:SpanEllipsisName', timeout=10).click()
                name = page_brush.wait.ele_loaded('tag:a@data-testid=user-card-avatar', timeout=3).attr('href')[2:]

                if name not in name_set:
                    name_set.add(name)
                    print(name)
                    if len(name_set) > 10:
                        with open(f'{file_path}/{file_name}', 'a', encoding='utf8') as f:
                            for i in name_set:
                                f.write(i + '\n')
                        name_set.clear()
                page_brush.ele('tag:div@class:DivClose').click()
            except Exception as e:
                print(e)
                continue
    except:
        with open(f'{file_path}/{file_name}', 'a', encoding='utf8') as f:
            temp = list(name_set)
            for i in temp:
                f.write(i + '\n')


def get_fans(get_fans_page: ChromiumPage, getFans_user_id):
    logger.info(f'{getFans_user_id}开始获取粉丝id')
    get_fans_page.ele('tag:strong@title=Followers', timeout=5).click()
    # listener_All.listener_tiktok_fans(tiktok_fans_page=get_fans_page)

    fans_box = get_fans_page.ele('tag:section@role=dialog', timeout=5)
    ac = Actions(get_fans_page)
    fan_box = fans_box.eles('tag:span@class:SpanNickname', timeout=5)[0]
    logger.info(fan_box.text)
    ac.move_to(fan_box)

    logger.info(f'{getFans_user_id}开始滚动用户列表')
    scroll_count = 1
    while True:
        ac.scroll(0, 1000)
        logger.info(f'{getFans_user_id}正在进行第{scroll_count}次滚动')
        scroll_count += 1
        get_fans_page.wait(3, 5)


def commentAreaAt(page_comment: ChromiumPage, comment_user_id, file_index):
    videoUrl_list = ['https://www.tiktok.com/@wtfjus/video/7348597076084673835',
                     'https://www.tiktok.com/@icespicee/video/7335553442817117483',
                     'https://www.tiktok.com/@gs3361/video/7343273741331270955',
                     'https://www.tiktok.com/@sams.oasis/video/7342229427725667617',
                     'https://www.tiktok.com/@noelgoescrazy/video/7329962222573210913',
                     'https://www.tiktok.com/@zoe_movie/video/7344398724849929518']

    page_comment.get(random.choice(videoUrl_list))
    # page_comment.wait(5, 10)
    my_utils.validation(page_comment, comment_user_id)
    title = page_comment.ele('tag:div@class=DraftEditor-root')

    file_path = f'./split/split_{file_index}.txt'
    with open(file_path, 'r', encoding='utf8') as comment_f:
        lines = [line.strip() for line in comment_f.readlines()]

    at_box = page_comment.ele('tag:div@data-e2e=comment-at-icon', timeout=10).ele('tag:svg')
    page_comment.scroll.to_see(at_box)

    comment_count = 1
    for comment in lines:
        title.input('@', clear=False)
        # input_box = page_comment.ele('tag:span@@text()=@')
        for char_i in comment:
            title.input(char_i, clear=False)
        page_comment.wait(0.5, 1.5)
        logger.info(f'{comment_user_id}已完成第{comment_count}次输入，开始发送评论')
        page_comment.ele('tag:div@data-e2e=comment-post').click()


if __name__ == '__main__':
    # 记录开始时间
    start_time = time.time()

    with open('txt_path/tiktok_browser_id.txt', 'r', encoding='utf8') as f:
        origin_browser_id_list = [line.strip() for line in f.readlines()]

    main_user_id = 'jf8r69r'
    # if_temp = 'jfdfett'
    page = get_page(main_user_id)

    # url = 'https://www.tiktok.com/@fizzinsparklythings/live'
    # for _ in range(5):
    #     delete_ceshi(page)

    # with open('test.json', 'r', encoding='utf-8') as f:
    #     page.cookies(json.load(f))
    # page.refresh()
    # brushVideo(page, user_id)
    # getLive_user_id(page)

    # get_fans(page, main_user_id)

    tiktok_caption.commentAreaAt(page, main_user_id, 1)
    # 记录结束时间
    end_time = time.time()

    # 计算运行时间
    elapsed_time = end_time - start_time
    logger.info(f"程序运行时间：{elapsed_time}秒")
    # print([1,2,4,5,6][:-1])
