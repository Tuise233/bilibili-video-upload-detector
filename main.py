# By 马马马马马马酱

import requests
import json
import time
from BrowserReader import GoogleBrowerCookie

video_bvid = None
video_amount = 0
now_follower = 0
last_follower = 0
check_count = 0
last_time = 0


def get_cookies(b_type):
    '''
    读取浏览器记录，支持google浏览器和新版edge浏览器
    :param b_type: 浏览器名称
    :return: 格式化后的cookies
    '''
    cookies1 = GoogleBrowerCookie("api.bilibili.com", b_type).get_cookie_str()
    cookies2 = GoogleBrowerCookie(".bilibili.com", b_type).get_cookie_str()
    return (cookies1 + cookies2)[:-1]


def get_csrf(b_type):
    """
    读取csrf值
    :param b_type: 浏览器名称
    :return: csrf值
    """
    cookie = GoogleBrowerCookie(".bilibili.com", b_type)
    cookie.get_cookie_from_chrome()
    return cookie.cookies.get("bili_jct")


def get_new_video(uid, b_type):
    global video_bvid
    global video_amount
    global now_follower
    global last_follower
    global check_count
    global last_time
    check_count += 1
    print('检查视频推送... 当前检查次数{}次'.format(check_count))
    url = 'https://api.bilibili.com/x/space/arc/search?mid=9978781&pn=1&ps=25&index=1&jsonp=jsonp'  # mid为UP主的UID
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75'
    }
    html = requests.get(url, headers=header)
    data = json.loads(html.text)
    video = data['data']['list']['vlist'][0]
    if video['bvid'] != video_bvid:
        if video_bvid is None:
            last_follower = get_follower(uid, b_type)
            video_bvid = video['bvid']
            print('脚本初始化运行')
        else:
            now_follower = get_follower(uid, b_type)
            video_bvid = video['bvid']
            video_amount += 1

            time_cc = video['created'] - last_time  # 与上次发视频的时间差
            video_day, video_hour = divmod(time_cc, 3600 * 24)  # 计算天数
            video_hour, video_minute = divmod(video_hour, 3600)  # 计算小时
            video_minute, video_second = divmod(video_minute, 60)  # 计算分钟和秒

            print('新视频更新 - 视频标题{} 视频时长{} BV号{}\n更新间隔时间{}天{}时{}分{}秒\n'
                  '今日推送视频数量{}个\n当前粉丝数{}个 新增粉丝{}个'.format(video['title'],
                                                         video['length'],
                                                         video['bvid'],
                                                         video_day,
                                                         video_hour,
                                                         video_minute,
                                                         video_second,
                                                         video_amount,
                                                         now_follower,
                                                         now_follower - last_follower))
            # 评论
            comment = '[脚本由Python编写]\n陈师姬成长日记\n已推送新视频!\n' \
                      '视频标题:{}\n视频时长:{}\n更新间隔时间:{}天{}时{}分{}秒\n' \
                      '今日推送视频数量:{}个\n当前粉丝数:{}个\n距上个视频新增粉丝数:{}'.format(
                video['bvid'], video['length'], video_day, video_hour, video_minute, video_second, video_amount,
                now_follower,
                now_follower - last_follower)

            last_follower = now_follower
            check_count = 0
            reply_video(video['aid'], comment, b_type)


def reply_video(aid, msg, b_type):
    url = 'https://api.bilibili.com/x/v2/reply/add'
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
        'cookie': get_cookies(b_type)
    }
    data = {
        'oid': aid,
        'type': '1',
        'message': msg,
        'plat': '1',
        'ordering': 'heat',
        'jsonp': 'jsonp',
        'csrf': get_csrf(b_type)
    }
    requests.post(url, headers=header, data=data)


def get_follower(uid, b_type):
    url = 'https://api.bilibili.com/x/relation/stat?vmid={}&jsonp=jsonp'.format(uid)  # vmid为UP主UID
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75',
        'cookie': get_cookies(b_type)
    }
    html = requests.get(url, headers=header)
    data = json.loads(html.text)
    return data['data']['follower']


if __name__ == "__main__":
    check_timer = 0
    video_amount = int(input("请输入当天投稿视频数量:"))  # 输入的值为今天已经投稿的视频数量
    mid = input("请输入UP主的UID:")
    b_type = input("请输入打开b站浏览器的名称（google或edge）:")
    while True:
        get_new_video(mid, b_type)
        time.sleep(60)
