# By 马马马马马马酱

import requests
import json
import time

video_bvid = 'null'
video_amount = 0
video_hour = 0
video_minute = 0
video_second = 0
now_follower = 0
last_follower = 0
check_count = 0

def get_new_video():
    global video_bvid
    global video_amount
    global video_second
    global video_minute
    global video_hour
    global now_follower
    global last_follower
    global check_count
    check_count += 1
    print('检查视频推送... 当前检查次数{}次'.format(check_count))
    url = 'https://api.bilibili.com/x/space/arc/search?mid=9978781&pn=1&ps=25&index=1&jsonp=jsonp' #mid为UP主的UID
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75' 
    }
    html = requests.get(url, headers=header)
    data = json.loads(html.text)   
    video = data['data']['list']['vlist'][0]
    if video['bvid'] != video_bvid:
        if video_bvid == 'null':
            last_follower = get_follower()
            video_bvid = video['bvid']
            print('脚本初始化运行')
        else:
            now_follower = get_follower()
            video_bvid = video['bvid']
            video_amount += 1
            print('新视频更新 - 视频标题{} 视频时长{} BV号{}\n更新间隔时间{}时{}分{}秒\n今日推送视频数量{}个\n当前粉丝数{}个 新增粉丝{}个'.format(video['title'], video['length'], video['bvid'], video_hour, video_minute, video_second, video_amount, now_follower, now_follower-last_follower))
            #评论
            comment = '[脚本由Python编写]\n陈师姬成长日记\n已推送新视频!\n视频标题:{}\n视频时长:{}\n更新间隔时间:{}时{}分{}秒\n今日推送视频数量:{}个\n当前粉丝数:{}个\n距上个视频新增粉丝数:{}'.format(video['bvid'], video['length'], video_hour, video_minute, video_second, video_amount, now_follower, now_follower-last_follower)
            last_follower = now_follower
            video_hour = 0
            video_minute = 0
            video_second = 0
            check_count = 0
            reply_video(video['aid'], comment)


def reply_video(aid, msg):
    url = 'https://api.bilibili.com/x/v2/reply/add'
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75', # User Agent
        'cookie': '请填写cookie' #cookie请自己准备帐号登录 F12获取
    }
    data = {
        'oid': aid,
        'type': '1',
        'message': msg,
        'plat': '1',
        'ordering': 'heat',
        'jsonp': 'jsonp',
        'csrf': '请填写csrf' #没有过多研究，个人理解为每个用户拥有的验证特征码  需要自行去手动评论F12抓包获取
    }
    html = requests.post(url, headers=header, data=data)
    data = json.loads(html.text)

def get_follower():
    url = 'https://api.bilibili.com/x/relation/stat?vmid=9978781&jsonp=jsonp' # mid为UP主UID
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75' # User Agent
    }
    html = requests.get(url ,headers=header)
    data = json.loads(html.text)
    return data['data']['follower']

if __name__ == "__main__":
    check_timer = 0
    video_amount = int(input("请输入当天投稿视频数量:")) #输入的值为今天已经投稿的视频数量
    while True:
        video_second += 1
        check_timer += 1

        if check_timer == 10:
            check_timer = 0
            get_new_video()

        if video_second >= 60:
            video_minute += 1
            video_second = 0

        if video_minute >= 60:
            video_hour += 1
            video_minute = 0

        if video_second == 59 and video_minute == 59 and video_second == 59:
            video_amount = 0
            
        time.sleep(1)
        
