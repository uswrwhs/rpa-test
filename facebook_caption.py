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

    join_box = page_joinAGroup.ele('tag:div@aria-label=加入小组', timeout=10).ele('tag:span@dir=auto')
    ac.move_to(join_box).click()
    logger.info(f'{video_user_id}正在加入指定小组')
    page_joinAGroup.wait(3, 5)

    # 返回主页
    back_box = page_joinAGroup.ele('tag:a@aria-label=Facebook', timeout=5)
    ac.move_to(back_box).click()
    page_joinAGroup.wait(3, 5)
    logger.info(f'{video_user_id}正在返回主页')
    return True


def brushVideo(page_brushVideo: ChromiumPage, video_user_id):
    page_brushVideo.set.scroll.smooth()
    page_brushVideo.wait(10, 15)
    ac = Actions(page_brushVideo)
    all_like_count = 0

    # 当前视频页面类型
    if page_brushVideo.url.find('watch?v=') != -1:
        # 长视频页主页面 此页面有多个视频，类似主页，下滑刷新
        start_time_video = time.time()
        cycle_time = random.uniform(4, 7) * 60
        video_count = 0

        mian_video_lick = page_brushVideo.eles('tag:div@aria-label=赞')
        for like_box in mian_video_lick:
            if like_box.states.has_rect is not False:
                like_box.click()
                break
        logger.info(f'{video_user_id}正在给主视频点赞')
        while True:
            video_count += 1
            page_brushVideo.wait(8, 13)
            main_Feed = page_brushVideo.ele('tag:div@data-pagelet=MainFeed', timeout=10)
            logger.info(f'{video_user_id}正在刷视频，当前是第{video_count}个视频')

            video_box = main_Feed.ele('tag:div@aria-label=赞', index=video_count)
            if not video_box:
                video_box = main_Feed.ele('tag:div@aria-label=赞', index=math.floor(video_count / 2))
                if not video_box:
                    running_time = time.time() - start_time_video
                    logger.info(f'{video_user_id}获取下一个视频元素失败，准备返回首页')
                    logger.info(f'{video_user_id}观看视频时间结束,正在结束流程，开始统计数据')
                    logger.info(f'{video_user_id}一共观看了{video_count}个视频，完成{all_like_count}次点赞,'
                                f'耗时{math.floor(running_time / 60)}分{math.ceil(running_time / 60)}秒')
                    return False, all_like_count
            # page_brushVideo.scroll.to_see(video_box)
            ac.move_to(video_box, duration=5)
            if 0.5 < random.random() < 0.8:
                page_brushVideo.wait(2, 4)
                # like_box = main_Feed.ele('tag:div@aria-label=赞', index=video_count).ele('tag:i')
                ac.click()
                all_like_count += 1
                ac.move(120, -100, duration=2)
                logger.info(f'{video_user_id}正在点赞,已经完成{all_like_count}次点赞')
                page_brushVideo.wait(2, 4)

            running_time = time.time() - start_time_video
            if running_time - cycle_time > 0:
                logger.info(f'{video_user_id}观看视频时间结束,正在结束流程，开始统计数据')
                logger.info(f'{video_user_id}一共观看了{video_count}个视频，完成{all_like_count}次点赞,'
                            f'耗时{math.floor(running_time / 60)}分{math.ceil(running_time / 60)}秒')
                return True, all_like_count

    elif page_brushVideo.url.find('www.facebook.com/reel/') != -1:
        # 短视频页面 类似tiktok的短视频页面，可以前往上一个或者下一个视频
        # 不刷短视频，直接返回上一页
        page_brushVideo.wait(3, 5)
        logger.info(f'{video_user_id}当前视频为短视频，直接返回主页')
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
    page_brushPost.set.scroll.smooth()
    ac = Actions(page_brushPost)
    # 定位到第一个帖子
    current_index = 1

    # 定义刷帖时间
    port_start_time = time.time()
    cycle_time = random.uniform(60, 75) * 60
    while True:
        # 滚动到帖子可见
        current_post = page_brushPost.ele(f'tag:div@role=article', index=current_index)
        logger.info(f'{post_user_id}正在主页观看文章，当前观看了{current_index}篇文章')
        ac.move_to(current_post, duration=3.5)
        page_brushPost.scroll.to_see(current_post, center=True)
        # 获取当前元素的静态版本，提升效率
        s_current_ele = current_post.s_ele()
        page_brushPost.wait(3, 5)

        like_box = s_current_ele.ele('tag:div@aria-label=赞')

        # states.is_alive
        # 判断元素是否可用 True为可用

        # 点赞时间触发概率
        if 0.2 < random.random() < 0.3:
            if like_box:
                current_post.ele('tag:div@aria-label=赞').click()
                page_brushPost.wait(2, 4)
                logger.info('')
        # 确认当前帖子类型
        if s_current_ele.ele('tag:div@data-pagelet=Reels'):
            # 短视频
            pass
        elif s_current_ele.ele('tag:a@aria-label=Reels'):
            # 短视频或Reels
            pass
        elif s_current_ele.ele('tag:video'):
            # 视频
            if 0.1 < random.random() < 0.3:
                ac.move_to(current_post, duration=3.5).click()
                try:
                    brushVideo(page_brushPost, post_user_id)
                except:
                    logger.info(f'{post_user_id}视频页发生错误，正在回到上一页')
                    ac.key_down(Keys.ESCAPE)
                    page_brushPost.wait(3, 5)
                    return False
                logger.info(f'{post_user_id}视频观看完成，正在返回主页')
                ac.key_down(Keys.ESCAPE)
                page_brushPost.wait(3, 5)
                return True
        elif s_current_ele.ele('tag:div@aria-label=为你推荐'):
            # 推荐小组
            if 0.1 < random.random() < 0.3:
                group_length = len(current_post.eles('tag:li'))
                for _temp in range(1, group_length - 1):
                    page_brushPost.wait(2, 3)
                    if 0.2 < random.random() < 0.5:
                        if _temp == 1:
                            next_box = current_post.ele('tag:div@aria-label=向右箭头').ele('tag:i')
                            ac.move_to(next_box).click()
                        else:
                            ac.click()
                        logger.info(f'{post_user_id}正在进行小组翻页')
                        page_brushPost.wait(2, 3)
                    elif 0.2 < random.random() < 0.4:
                        logger.info(f'{post_user_id}准备加入小组')
                        public_flag = current_post.ele('tag:li', index=_temp).ele('公开小组')
                        if not public_flag:
                            logger.info(f'{post_user_id}该小组不是公开小组，进入下一次循环')
                            continue
                        add_group_box = current_post.ele('tag:div@aria-label=加入小组', index=_temp)
                        if add_group_box:
                            ac.move_to(add_group_box).click()
                            logger.info(f'{post_user_id}正在点击加入小组按钮')
                            page_brushPost.wait(5, 8)
                        else:
                            logger.error(f'{post_user_id}已经加入该小组，无法重复加入')
                        break
                    # 概率不加小组直接退出
                    elif 0.3 < random.random() < 0.4:
                        logger.info(f'{post_user_id}选择不加入小组，继续下一步操作')
                        break

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


def send_message(page_send: ChromiumPage, user_id_send):
    logger.info(f'{user_id_send}进入私信页面')
    send_test = '61556571823159'
    ac = Actions(page_send)
    send_txt = 1
    send_url = f'https://www.facebook.com/messages/t/{send_test}'

    page_send.get(send_url)

    send_box = page_send.ele('tag:div@aria-label=发消息')
    ac.move_to(send_box).click().type(Keys.CTRL_V)

    send_box.input('这是一条测试消息')
    logger.info(f'{user_id_send}正在发送消息')


# 随机加推荐好友
def Random_add_friends(page_addFri: ChromiumPage, user_id_addFri):
    logger.info(f'{user_id_addFri}准备开始添加好友')
    ac = Actions(page_addFri)

    suggest_fri_url = 'https://www.facebook.com/friends/suggestions'
    page_addFri.get(suggest_fri_url)

    fri_list = page_addFri.eles('tag:div@aria-label=加为好友')
    rand_fri_id = random.sample(range(1, len(fri_list) + 1), 3)

    for fri_box_id in rand_fri_id:
        ac.move_to(fri_list[fri_box_id]).click()
        page_addFri.wait(3, 5)


# 随机添加推荐小组
def addGroupsRandomly(page_addGroup: ChromiumPage, user_id_addGroup):
    sug_group_url = ''
    page_addGroup.get(sug_group_url)
    pass


# 添加指定好友
def addSpecifieFri(page_addGroup: ChromiumPage, user_id_addGroup):
    origin_url = 'https://www.facebook.com/profile.php?id='
    fri_id = '61556571823159'
    ac = Actions(page_addGroup)

    fri_url = origin_url + fri_id
    page_addGroup.get(fri_url)
    page_addGroup.wait(3, 5)

    fri_box = page_addGroup.ele('tag:div@aria-label=添加好友')
    if not fri_box:
        logger.error(f'{user_id_addGroup}获取添加好友按钮失败，准备返回主页')
        return False
    ac.move_to(fri_box).click()
    logger.info(f'{user_id_addGroup}正在添加好友，id:{fri_id}')

    bace_box = page_addGroup.ele('tag:a@aria-label=Facebook')
    if not bace_box:
        logger.error(f'{user_id_addGroup}获取返回主页按钮失败，即将跳转主页链接')
        return False
    ac.move_to(bace_box).click()
    logger.info(f'{user_id_addGroup}添加好友成功，正在回到主页')
    return True


def addFriendsInAGroup(page_add_FriInGp: ChromiumPage, user_id_add_FriInGp):
    ac = Actions(page_add_FriInGp)
    main_box = page_add_FriInGp.ele('tag:div@role=feed')
    current_child = main_box.child('tag:div').next('tag:div')

    add_upperLimit = random.randint(2, 3)
    add_count = 0
    while True:
        page_add_FriInGp.scroll.to_see(current_child, center=True)
        if 0.2 < random.random() < 0.4:
            name_box = current_child.ele('tag:h3').ele('tag:a')
            ac.move_to(name_box)

            page_add_FriInGp.wait.ele_loaded('tag:div@aria-label=链接预览', timeout=10)
            add_user = page_add_FriInGp.ele('tag:div@aria-label=添加好友')
            ac.move_to(add_user).click()
            add_count += 1
            logger.info(f'{user_id_add_FriInGp}正在小组内添加好友，目前添加个数为{add_count}')
            page_add_FriInGp.wait(2, 3)
        if add_count == add_upperLimit:
            logger.info(f'{user_id_add_FriInGp}好友添加达到本次上限，小组内加好友执行结束')
            break
            pass
    return True


if __name__ == '__main__':
    pass
