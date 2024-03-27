import math
import random
import time

import pyotp
from DrissionPage._functions.keys import Keys
from DrissionPage._pages.chromium_page import ChromiumPage
from DrissionPage._units.actions import Actions
from loguru import logger

ROOT_PATH = 'browserDownload'


def click_button(page_click: ChromiumPage, locator):
    # 触发点击事件 失败后重试三次
    for index in range(3):
        try:
            page_click.ele(locator, timeout=5).ele('tag:i').click()
            break
        except:
            if index == 2:
                return False
            page_click.wait(2, 5)
            continue
    return True


# 刷短视频
def brushReel(page_brushReel: ChromiumPage, brush_user_id):
    page_brushReel.wait(3, 5)
    start_reel_time = time.time()
    cycle_time = random.uniform(3, 5) * 60
    feel_like_count = 0
    feel_count = 0
    while True:
        page_brushReel.wait(3, 6)
        feel_count += 1
        # 点赞
        if 0.3 < random.random() < 0.4:
            like_loc = 'tag:div@aria-label=赞'
            if not click_button(page_brushReel, like_loc):
                logger.info(f'{brush_user_id}点赞失败，请检查错误原因')
            feel_like_count += 1
            logger.info(f'{brush_user_id}正在feel页面点赞，目前已点{feel_like_count}个赞')
        page_brushReel.wait(3, 4)

        running_time = time.time() - start_reel_time
        if running_time - cycle_time > 0:
            logger.info(f'{brush_user_id}短视频观看时间结束,正在结束流程，开始统计数据')
            logger.info(f'{brush_user_id}一共观看了{feel_count}个短视频，完成{feel_like_count}次点赞,'
                        f'耗时{math.floor(running_time / 60)}分{math.ceil(running_time / 60)}秒')
            return True, feel_count

        next_button = 'tag:div@aria-label=下一条快拍'
        if not click_button(page_brushReel, next_button):
            logger.info(f'{brush_user_id}目前一共刷了{feel_count}条短视频,完成{feel_like_count}次点赞')
            logger.info(f'{brush_user_id}进入下一个短视频失败，准备返回')
            return False, feel_count


# 当前小组链接
# https://www.facebook.com/groups/433276105788114/?ref=share_group_link
# 加入指定小组
def joinAGroup(page_joinAGroup: ChromiumPage, video_user_id, group_url):
    ac = Actions(page_joinAGroup)
    page_joinAGroup.get(group_url)
    page_joinAGroup.wait(2, 3)

    join_box = page_joinAGroup.ele('tag:div@aria-label=加入小组').ele('tag:span@dir=auto')
    ac.move_to(join_box).click()
    logger.info(f'{video_user_id}正在加入指定小组')

    # 返回主页
    back_box = page_joinAGroup.ele('tag:a@aria-label=Facebook')
    ac.move_to(back_box).click()
    logger.info(f'{video_user_id}正在返回主页')


def brushVideo(page_brushVideo: ChromiumPage, video_user_id):
    page_brushVideo.wait(5, 15)
    ac = Actions(page_brushVideo)
    all_like_count = 0

    # 当前视频页面类型
    if page_brushVideo.url.find('watch?v=') != -1:
        # 长视频页主页面 此页面有多个视频，类似主页，下滑刷新
        main_Feed = page_brushVideo.ele('tag:div@data-pagelet=MainFeed')
        start_time_video = time.time()
        cycle_time = random.uniform(4, 7) * 60
        video_count = 0

        video_box = main_Feed.eles('tag:video')
        start_index = 0
        while True:
            video_count += 1

            running_time = time.time() - start_time_video
            if running_time - cycle_time > 0:
                logger.info(f'{video_user_id}观看视频时间结束,正在结束流程，开始统计数据')
                logger.info(f'{video_user_id}一共观看了{video_count}个视频，完成{all_like_count}次点赞,'
                            f'耗时{math.floor(running_time / 60)}分{math.ceil(running_time / 60)}秒')
                return True, all_like_count

            break
        # 点赞
        if 0.5 < random.random() < 0.6:
            like_box = page_brushVideo.ele('tag:div@aria-label=赞', index=3).ele('tag:i')
            if like_box:
                like_box.click()

    elif page_brushVideo.url.find('www.facebook.com/reel/') != -1:
        # 短视频页面 类似tiktok的短视频页面，可以前往上一个或者下一个视频
        flag, count = brushReel(page_brushVideo, video_user_id)
        all_like_count += count
        # 返回上一页
        ac.key_down(Keys.ESCAPE)
        page_brushVideo.wait(3, 5)
    else:
        # 视频聚焦页面 此页面只有一个视频，不能前往下一个或者上一个视频
        if 0.1 < random.random() < 0.2:
            like_box = 'tag:div@aria-label=赞'
            if not click_button(page_brushVideo, like_box):
                logger.info(f'{video_user_id}点赞失败，请检查原因')
            all_like_count += 1
        # 退出视频页

    return all_like_count


def brushPost(page_brushPost: ChromiumPage, post_user_id):
    ac = Actions(page_brushPost)
    # 定位到第一个帖子
    current_index = 1

    # 定义刷帖时间
    port_start_time = time.time()
    cycle_time = random.uniform(30, 40) * 60
    with True:
        # 滚动到帖子可见
        current_post = page_brushPost.ele(f'tag:div@role=article', index=current_index)
        page_brushPost.scroll.to_see(current_post)
        # 获取当前元素的静态版本，提升效率
        s_current_ele = current_post.s_ele()
        page_brushPost.wait(3, 5)

        like_box = s_current_ele.ele('tag:div@aria-label=赞')

        # states.is_alive
        # 判断元素是否可用 True可以

        # 点赞时间触发概率
        if 0.2 < random.random() < 0.3 and like_box:
            current_post.ele('tag:div@aria-label=赞').click()
        # 确认当前帖子类型
        if s_current_ele.ele('tag:div@data-pagelet=Reels'):
            pass
            # # 短视频
            # if 0.1 < random.random() < 0.05:
            #     ac.move_to(current_post).click()
            #     flag, count = brushReel(page_brushPost, post_user_id)
            #     ac.key_down(Keys.ESCAPE)
            #     page_brushPost.wait(3, 5)
            #     logger.info(f'{post_user_id}正在返回')
            # pass
        elif s_current_ele.ele('tag:video'):
            # 视频
            if 0.1 < random.random() < 0.3:
                ac.move_to(current_post).click()
                brushVideo(page_brushPost, post_user_id)
                ac.key_down(Keys.ESCAPE)
                page_brushPost.wait(3, 5)
        elif s_current_ele.ele('tag:div@aria-label=为你推荐'):
            # 推荐小组
            group_length = len(current_post.eles('tag:li'))
            for _temp in range(1, group_length - 1):
                if 0.2 < random.random() < 0.8:
                    if _temp == 1:
                        next_box = current_post.ele('tag:div@aria-label=向右箭头').ele('tag:i')
                        ac.move_to(next_box).click()
                        logger.info(f'{post_user_id}正在进行小组翻页')
                    ac.click()
                if 0.2 < random.random() < 0.3:
                    public_flag = current_post.ele('tag:li', index=_temp).ele('公开小组')
                    if not public_flag:
                        continue
                    add_group_box = current_post.ele('tag:div@aria-label=加入小组', index=_temp)
                    if add_group_box:
                        ac.move_to(add_group_box).click()
                        logger.info(f'{post_user_id}正在加入小组')
                    else:
                        logger.error(f'{post_user_id}已经加入该小组，无法重复加入')
                    break
                # 概率不加小组直接退出
                if 0.3 < random.random() < 0.4:
                    break
        elif s_current_ele.ele('tag:a@aria-label=Reels'):
            # 短视频或Reels
            # 是否选择翻页
            # temp_index = 1
            # if 0.2 < random.random() < 0.5:
            #     page_brushPost.ele('tag:a@aria-label=下一行').click()
            #     temp_index += 2
            # # 是否选择
            # if 0.3 < random.random() < 0.5:
            #     click_reel = current_post.ele('tag:a@aria-label=Reels').ele('tag:div@aria-hidden=false',
            #                                                                 index=random.randint(temp_index,
            #                                                                                      temp_index + 1))
            #     ac.move_to(click_reel).click()
            #     brushReel(page_brushPost, post_user_id)
            #     ac.key_down(Keys.ESCAPE)
            #     page_brushPost.wait(3, 5)
            # pass
            pass

        running_time = time.time() - port_start_time
        if running_time > cycle_time:
            return True
        current_index += 1


def face_init(page_init: ChromiumPage, email_init, pwd_init, fa_two_init, user_id_init):
    def get_faTwo_code(fa_2):
        # 创建一个TOTP对象
        totp = pyotp.TOTP(fa_2)
        # 生成当前时间的验证码
        return totp.now()

    page_init.wait(3, 5)
    page_init.scroll.to_bottom()
    flag = page_init.ele('tag:button@@text()=Allow all cookies')
    if flag:
        flag.click()
    if page_init.url.find('https://mbasic.facebook.com/login.php') == -1:
        page_init.get('https://mbasic.facebook.com/login.php')
    # 输入邮箱和密码
    page_init.ele('#m_login_email').input(email_init)
    page_init.ele('tag:input@name=pass').input(pwd_init)
    logger.info(f'{user_id_init}正在输入邮箱和密码')
    # 点击登录
    page_init.ele('tag:input@name=login').click()
    fa_2_code = get_faTwo_code(fa_two_init)
    fa2_code_box = page_init.wait.ele_loaded('#approvals_code', timeout=10)
    if fa2_code_box:
        fa2_code_box.input(fa_2_code)
        logger.info(f'{user_id_init}正在输入2fa验证码')
    else:
        logger.error(f'{user_id_init}2fa验证码获取失败')
        return False
    # 提交验证码
    page_init.ele('#checkpointSubmitButton-actual-button', timeout=5).click()
    # 继续
    page_init.ele('#checkpointSubmitButton-actual-button', timeout=5).click()
    # 前往首页
    while True:
        page_init.wait(5, 10)
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

    return True


if __name__ == '__main__':
    pass
