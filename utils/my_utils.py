import base64
import datetime
import json
import msvcrt
import os
import random
import shutil
import time
from io import BytesIO

import cv2
import ddddocr
import pandas as pd
import requests
from DownloadKit import DownloadKit
from DrissionPage._elements.chromium_element import ChromiumElement
from DrissionPage._pages.chromium_page import ChromiumPage
from PIL import Image
from loguru import logger

t1 = datetime.datetime.now()
ROOT_PATH = '../browserDownload'


# PIL图片保存为base64编码
def PIL_base64(img, coding='utf-8'):
    img_format = img.format
    if img_format == None:
        img_format = 'JPEG'

    format_str = 'JPEG'
    if 'png' == img_format.lower():
        format_str = 'PNG'
    if 'gif' == img_format.lower():
        format_str = 'gif'

    if img.mode == "P":
        img = img.convert('RGB')
    if img.mode == "RGBA":
        format_str = 'PNG'
        img_format = 'PNG'

    output_buffer = BytesIO()
    # img.save(output_buffer, format=format_str)
    img.save(output_buffer, quality=100, format=format_str)
    byte_data = output_buffer.getvalue()
    base64_str = 'data:image/' + img_format.lower() + ';base64,' + base64.b64encode(byte_data).decode(coding)

    return base64_str


def rotate_image_f(outer: ChromiumElement, rotate_user_id):
    url1 = outer.attr('src')
    # print(url1)
    inner_url = outer.next('tag:img').attr('src')
    # print(inner_url)

    down_err_flag = download_img(url1, inner_url, f'{ROOT_PATH}/{rotate_user_id}', 'outer.jpeg', 'inner.jpeg')
    if not down_err_flag:
        logger.error(f'{rotate_user_id}进行旋转图片验证时出现错误，请及时处理')
        return -100

    # discern('./publicPicture/inner.jpeg','./publicPicture/outer.jpeg',isSingle=True)

    # 加载外圈大图
    img1 = Image.open(f'{ROOT_PATH}/{rotate_user_id}/outer.jpeg')
    # 图片转base64
    img1_base64 = PIL_base64(img1)
    # 加载内圈小图
    img2 = Image.open(f'{ROOT_PATH}/{rotate_user_id}/inner.jpeg')
    # 图片转base64
    img2_base64 = PIL_base64(img2)

    # 验证码识别接口
    url = "http://www.detayun.cn/openapi/verify_code_identify/"
    data = {
        # 用户的key
        "key": "Mke2XwTi0JAdZGygvXPw",
        # 验证码类型
        "verify_idf_id": "37",
        # 外圈大图
        "img1": img1_base64,
        # 内圈小图
        "img2": img2_base64,
    }
    header = {"Content-Type": "application/json"}

    # 发送请求调用接口
    response = requests.post(url=url, json=data, headers=header)

    # 获取响应数据，识别结果
    result = response.json()
    logger.info(f'{rotate_user_id}调用旋转验证码接口，返回结果{result}')

    # length = 270 / 360 * result['data']['angle']
    # print(length)
    # print("耗时：", datetime.datetime.now() - t1)

    return result['data']['px_distance']


def download_img(url1, url2, download_user_id, name1, name2):
    def img_fileExists(imgExists_file_path, img_name1, img_name2):
        img_path1 = f'{imgExists_file_path}/{img_name1}'
        img_path2 = f'{imgExists_file_path}/{img_name2}'
        if os.path.exists(img_path1) and os.path.exists(img_path2):
            return True
        else:
            return False

    file_path = f'./{ROOT_PATH}/{download_user_id}'
    del_last_img(file_path, name1, name2)
    d = DownloadKit()

    m1 = d.add(url1, rename=name1, suffix='', goal_path=file_path, file_exists='o')
    m2 = d.add(url2, rename=name2, suffix='', goal_path=file_path, file_exists='o')
    timeout = 2

    func_start_time = time.time()
    while True:
        time.sleep(random.randint(3, 5))
        flag = img_fileExists(file_path, name1, name2)
        func_current_time = time.time()
        if flag:
            break
        if func_current_time - func_start_time > timeout * 60:
            logger.error(f'{download_user_id}图片验证码下载失败，请检查网络')
            return False

    # 读取图像
    img = cv2.imread(f'{file_path}/{name1}')
    img2 = cv2.imread(f'{file_path}/{name2}')

    # 保存图像为指定格式
    cv2.imwrite(f'{file_path}/{name1}', img)
    # 保存图像为指定格式
    cv2.imwrite(f'{file_path}/{name2}', img2)
    return True


def img_valid(user_id):
    det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)

    with open(f'./{ROOT_PATH}/{user_id}/puzzle.png', 'rb') as f:
        target_bytes = f.read()

    with open(f'./{ROOT_PATH}/{user_id}/origin.jpeg', 'rb') as f:
        background_bytes = f.read()

    logger.info(f'./{ROOT_PATH}/{user_id}/puzzle.png')

    back_img = Image.open(f'./{ROOT_PATH}/{user_id}/origin.jpeg')

    res = det.slide_match(target_bytes, background_bytes)

    logger.info(res)
    return res['target'][0], back_img.width


def saveCompleteId(user_id_save):
    # 打开文件并获取锁
    with open('tiktok_complete_id.txt', 'a') as file:
        msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, 1)  # 获取锁
        file.write(f"{user_id_save}\n")
        msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)  # 释放锁


def del_last_img(del_path, del_name1, del_name2):
    try:
        os.remove(f'{del_path}/{del_name1}')
        os.remove(f'{del_path}/{del_name2}')
        logger.info(f'{del_path.split("/")[-1]}删除成功')
    except FileNotFoundError:
        logger.error(f"{del_path}文件不存在，无法删除")


def slideVerif(page_slide: ChromiumPage, origin_img: ChromiumElement, user_id_temp, model_type):
    logger.info(origin_img.attr('src'))
    puzzle = origin_img.next('tag:img')
    logger.info(puzzle.attr('src'))

    if model_type == 'slide':
        logger.info(f'{user_id_temp}正在进行平移滑块验证')

        flag = download_img(origin_img.attr('src'), puzzle.attr('src'), user_id_temp, 'origin.jpeg', 'puzzle.png')
        if not flag:
            logger.error(f'{user_id_temp}进行图片验证时出现错误，请检查错误原因')
            return False

        # 滑块与空白处的距离
        sliding_length, origin_length = img_valid(user_id_temp)
        # 变换系数
        transformCoefficient = 340 / origin_length
        # pu_transformCoefficient=puzzle_weight/
        fin_drag_length = round(transformCoefficient * sliding_length, 0)
        logger.info(fin_drag_length)
        # return

        # 拖动滑块
        dragBox = page_slide.ele('tag:div@class:secsdk-captcha-drag-icon')
        dragBox.drag(fin_drag_length, 0, 1)
    elif model_type == 'rotate':
        logger.info(f'{user_id_temp}正在进行旋转滑块验证')
        fin_drag_length = rotate_image_f(origin_img, user_id_temp)
        if fin_drag_length < 0:
            logger.error(f'{user_id_temp}进行图片验证时出现错误，请检查错误原因')
            return False

        dragBox = page_slide.ele('tag:div@class:secsdk-captcha-drag-icon')
        dragBox.drag(fin_drag_length, 0, 1.5)
    return True


def validation(page_validation: ChromiumPage, user_id_validation):
    page_validation.set.NoneElement_value(None)
    start_time = time.time()
    while True:
        counter_flag = 0
        err_flag = True
        # 滑块验证码
        origin_img = page_validation.ele('tag:img@id=captcha-verify-image')
        outer_img = page_validation.ele('tag:img@data-testid=whirl-outer-img')
        if origin_img:
            err_flag = slideVerif(page_validation, origin_img, user_id_validation, 'slide')
        else:
            counter_flag += 1
        if outer_img:
            err_flag = slideVerif(page_validation, outer_img, user_id_validation, 'rotate')
        else:
            counter_flag += 1
        if not err_flag:
            return False
        if counter_flag == 2:
            break
        end_time = time.time()
        if end_time - start_time > 3.5 * 60:
            return False
        time.sleep(10)
    return True


# 视频初始化
def reset_video():
    video_list = os.listdir('../videos')
    folder_list = [name for name in os.listdir(ROOT_PATH) if os.path.isdir(os.path.join(ROOT_PATH, name))]

    for folder, video in zip(folder_list, video_list):
        shutil.move(f'videos/{video}', f'{ROOT_PATH}/{folder}/video_1.mp4')


def rename_video():
    folder_list = [name for name in os.listdir(ROOT_PATH) if os.path.isdir(os.path.join(ROOT_PATH, name))]
    for folder in folder_list:
        video_list = os.listdir(f'{ROOT_PATH}/{folder}')
        for video in video_list:
            if video.find('mp4') != -1:
                os.rename(f'{ROOT_PATH}/{folder}/{video}', f'{ROOT_PATH}/{folder}/video_1.mp4')


def folder_reset():
    temp_dataframe = pd.read_excel('user_list2024-03-27.xlsx')
    with open('../txt_path/facebook_browser_id_1.txt', 'w') as f:
        for i in temp_dataframe['id'][:10]:
            f.write(i + '\n')

    id_json = {}
    for bro_id, index in zip(temp_dataframe['id'][::-1], temp_dataframe['acc_id'][::-1]):
        id_json.update({bro_id: index})
    #
    # with open('browser_id.json', 'w') as f:
    #     json.dump(id_json, f, ensure_ascii=False, indent=4)
    for browser_id in temp_dataframe['id']:
        os.makedirs(f'{ROOT_PATH}/{browser_id}', exist_ok=True)


def move_video():
    def is_folder_empty(folder_path):
        return not os.listdir(folder_path)

    video_list = os.listdir('../videos')
    count = 0
    with open('../txt_path/tiktok_browser_id.txt', 'r') as f:
        browser_ids = [line.strip() for line in f.readlines()]
    for browser_id in browser_ids:
        os.makedirs(f'{ROOT_PATH}/{browser_id}', exist_ok=True)
        shutil.move(f'../videos/{video_list[count]}', f'{ROOT_PATH}/{browser_id}/video_1.mp4')
        count += 1


def run():
    print(121)


def extractData_from_userIdJson():
    userID_jsonNamelist = os.listdir('../listener_data/tiktok_fans/irene93871')
    userId_set = set()

    for userID_jsonName in userID_jsonNamelist:
        with open(f'../listener_data/tiktok_fans/irene93871/{userID_jsonName}', 'r', encoding='utf8') as f:
            origin_data = json.load(f)
            userID_list = origin_data['userList']
        for userID in userID_list:
            temp = f"{userID['user']['uniqueId']}\n"
            if temp not in userId_set:
                userId_set.add(temp)
    with open('../name_data_origin/name.txt', 'w', encoding='utf8') as f:
        f.writelines(userId_set)


def extractData_from_face_txt():
    with open('./facebook_10.txt', 'r', encoding='utf8') as f:
        origin_data = f.readlines()
    origin_json = {
        'id': [],
        'password': [],
        '2fa': [],
        'tel': [],
        'email': [],
        'email_pwd': [],
        'ip_address': []
    }
    for origin in origin_data:
        for line, data_once in zip(origin.split('---'), origin_json):
            origin_json[data_once].append(line.split('：')[1])

    csv_temp = pd.DataFrame(origin_json)
    csv_temp.to_csv('facebook_10.csv', index=False, encoding='utf-8')


def generateImportFile():
    print(1)


def retry_click(origin_ele, click_path) -> bool:
    """重试三次点击
    :param origin_ele: 上级元素
    :param click_path: 点击按钮路径
    :return: 点击事件是否完成
    """
    if isinstance(click_path, list):
        for _temp in range(3):

            pass
    elif isinstance(click_path, str):
        pass

    return True


if __name__ == '__main__':
    # rotate_image_f()
    # reset_video()

    # extractData_from_userIdJson()

    # rename_video()
    folder_reset()
    # move_video()
    # extractData_from_userIdJson()
    # logger.info('121')
    # extractData_from_face_txt()
    # run()
