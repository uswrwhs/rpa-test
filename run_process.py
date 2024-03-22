import datetime
import json
import math
import msvcrt
import multiprocessing
import os
import random
import time

import requests
from DrissionPage.common import from_selenium
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import my_utils
import tiktok_caption

ROOT_PATH = 'browserDownload'
LOG_PATH = f'./logs/more_process'

# 设置日志文件名和格式 日志文件按不同日期分别存放
formatted_time = datetime.datetime.now().strftime("%Y-%m-%d---%H_%M_%S")
current_data = datetime.datetime.now().strftime("%Y-%m-%d")
os.makedirs(f'{LOG_PATH}/{current_data}', exist_ok=True)
logger.add(f'{LOG_PATH}/{current_data}/{formatted_time}.log', format="{time} {level} {message}", level="INFO")


class Run:
    def __init__(self):
        self.finger_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.finger_url = 'http://local.adspower.com:50325'

    # 根据对应user_id打开对应窗口
    def start_userID(self, user_id):
        url = f'{self.finger_url}/api/v1/browser/start'
        data = {'user_id': user_id}
        res = requests.get(url, headers=self.finger_headers, params=data)
        if res.status_code == 200:
            res_result = json.loads(res.text)
            if res_result["msg"] == "Success" or res_result["msg"] == "success":
                # 注意：下面两个参数必须传给selenium才能 启动指纹浏览器
                selenium_webdriver = res_result["data"]["webdriver"]
                selenium_address = res_result["data"]["ws"]["selenium"]
                logger.info(res_result)
                return selenium_webdriver, selenium_address, user_id
        else:
            logger.info(f'启动对应user_id指纹浏览器失败, 状态码:{res.status_code}')

    def start_selenium(self, selenium_webdriver, selenium_address, user_id):
        logger.info(f'当前执行窗口--{user_id}')
        chrome_option = Options()
        service = Service(selenium_webdriver)
        chrome_option.add_experimental_option("debuggerAddress", selenium_address)  # 这行命令必须加上，才能启动指纹浏览器

        driver = webdriver.Chrome(service=service, options=chrome_option)
        # driver.maximize_window()
        driver.close()
        page = from_selenium(driver)
        page.set.window.normal()

        return page


r = Run()


def saveCompleteId(user_id_save):
    # 打开文件并获取锁
    with open('complete_id.txt', 'a') as file:
        msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, 1)  # 获取锁
        file.write(f"{user_id_save}\n")
        msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)  # 释放锁


# 将user_id存入任务队列中
def operate_browser(browser_id_op, model, temp_index):
    selenium_webdriver, selenium_address, user_id = r.start_userID(user_id=browser_id_op)
    page = r.start_selenium(selenium_webdriver, selenium_address, user_id)
    logger.info(f'{browser_id_op}   {model}')

    #
    logger.info(f'当前是第{temp_index}台浏览器')

    # logger.info(page.url)
    flag = False
    if page.url.find('https://www.tiktok.com/') != -1 or len(page.url) > len('https://www.tiktok.com/foryou'):
        page.get('https://www.tiktok.com/')
    val_flag = my_utils.validation(page, browser_id_op)
    if val_flag:
        if model == 'modify_personal_data':
            flag = tiktok_caption.modify_personal_data(page, browser_id_op)
        elif model == 'upload_video':
            flag = tiktok_caption.upload_video(page, browser_id_op)
        elif model == 'resetTabBar':
            flag = tiktok_caption.resetTabBar(page)
        elif model == 'brushVideo':
            flag = tiktok_caption.brushVideo(page, browser_id_op)
        elif model == 'commentAreaAt':
            if temp_index > 21:
                page.quit()
                return 0
            page.wait(1, 5)
            logger.info(f'当前是第{temp_index}台浏览器')
            flag, next_flag = tiktok_caption.commentAreaAt(page, browser_id_op, temp_index)
            if next_flag == '123':
                logger.info(f'用户id文件消耗完毕')
                flag = True
    else:
        flag = False
    # page.wait(15, 20)

    if flag:
        saveCompleteId(browser_id_op)
        logger.info(f'{browser_id_op}已完成操作')
    else:
        logger.info(f'{browser_id_op}有异常情况，发生中断')
    page.quit()


def start_many_process(browsers, model, cycle_index):
    # 启动多个进程来操作多个浏览器

    processes = []
    count = 1
    for browsers_id in browsers:
        temp = (cycle_index - 1) * len(browsers) + count
        process = multiprocessing.Process(target=operate_browser, args=(browsers_id, model, temp))
        processes.append(process)
        process.start()
        count += 1
        time.sleep(5)

    # 等待所有进程完成
    for process in processes:
        process.join()


def reset_complete_txt():
    with open('browser_id.txt', 'r', encoding='utf8') as f:
        origin_browser_id_set = set(line.strip() for line in f.readlines())
    with open('complete_id.txt', 'r', encoding='utf8') as f:
        complete_browser_id_set = set(line.strip() for line in f.readlines())
    if origin_browser_id_set == complete_browser_id_set:
        with open('complete_id.txt', 'w', encoding='utf8') as f:
            f.write('')
        logger.info('complete文件已重置，可以进行新的操作')


# 导出未完成的浏览器序号
def exportIncompleteBrowserNumber():
    with open('browser_id.txt', 'r', encoding='utf8') as f:
        origin_browser_id_set = set(line.strip() for line in f.readlines())
    with open('complete_id.txt', 'r', encoding='utf8') as f:
        complete_browser_id_set = set(line.strip() for line in f.readlines())
    # 去除已完成操作的浏览器
    browser_id_set = origin_browser_id_set - complete_browser_id_set

    # 读取编号转id的json文件
    with open('temp/video/browser_id.json', 'r', encoding='utf8') as f:
        tran_json = json.load(f)
    # print(tran_json)
    no_complete_browser_list = [tran_json[b_id] for b_id in browser_id_set]
    print(no_complete_browser_list)


def run(op_i):
    model_list = ['modify_personal_data', 'upload_video', 'brushVideo', 'commentAreaAt']
    operate_index = op_i

    # 最大进程数
    maxProcesses = 3
    with open('browser_id.txt', 'r', encoding='utf8') as f:
        origin_browser_id_set = set(line.strip() for line in f.readlines())
    with open('complete_id.txt', 'r', encoding='utf8') as f:
        complete_browser_id_set = set(line.strip() for line in f.readlines())
    # 去除已完成操作的浏览器
    browser_id_set = origin_browser_id_set - complete_browser_id_set

    numberCycles = math.ceil(len(browser_id_set) / maxProcesses)

    cycle_count = 1
    for count_i in range(numberCycles):
        # 随机选取N个浏览器 N = numberOfProcesses
        try:
            current_browser_id_list = random.sample(browser_id_set, maxProcesses)
        except ValueError:
            current_browser_id_list = list(browser_id_set)
        start_many_process(current_browser_id_list, model_list[operate_index], cycle_count)
        cycle_count += 1
        for repeat_i in current_browser_id_list:
            browser_id_set.remove(repeat_i)
    # 线程池
    # with multiprocessing.Pool(processes=maxProcesses) as pool:  # 创建一个包含maxProcesses个进程的进程池
    #     for browser in browser_id_set:
    #         time.sleep(random.uniform(2, 5))  # 暂停2秒
    #         pool.apply_async(operate_browser, args=(browser, model_list[operate_index],))  # 使用进程池处理浏览器自动化操作
    #     pool.close()
    #     pool.join()

    logger.info('操作已全部完成')
    # reset_complete_txt()


if __name__ == "__main__":
    # 232 212
    op_index_list = [3, 2]
    op_index = 0
    run(2)
    # while True:
    #     run(op_index_list[op_index])
    #     time.sleep(random.uniform(2, 5))
    #
    #     with open('browser_id.txt', 'r', encoding='utf8') as f:
    #         origin_browser_id_set = set(line.strip() for line in f.readlines())
    #     with open('complete_id.txt', 'r', encoding='utf8') as f:
    #         complete_browser_id_set = set(line.strip() for line in f.readlines())
    #     if len(origin_browser_id_set) != len(complete_browser_id_set):
    #         continue
    #     else:
    #         index = 0
    #         op_index += 1
    #         if op_index > 1:
    #             break
    #         reset_complete_txt()
