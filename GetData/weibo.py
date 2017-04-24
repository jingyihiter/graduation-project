# -*- coding: utf-8 -*-
# coding:utf-8

"""
Created on Sun Apr 11 11:03:39 2017

@author: 马晶义
"""


import requests
import re
from bs4 import BeautifulSoup as BS
import chardet
import urllib2
import urllib
import chardet
import json
import base64
import time
import math
import random
from urllib import quote_plus
from PIL import Image

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
        Ubuntu Chromium/57.0.2987.98 Chrome/57.0.2987.98 Safari/537.36',
    'Connection': 'keep-alive',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    #'Accept-Encoding': 'gzip, deflate, br',
    #'Accept': '*/*'
}


def login_pre(username, Session):
    '''
    获取验证码
    '''
    su = (base64.b64encode(quote_plus(username).encode('utf-8'))
          ).decode('utf-8')  # 用户名用base64加密
    pre_Data = {
        "checkpin": '1',
        "entry": 'mweibo',
        "su": su,
        "callback": 'jsonpcallback' + str(int(time.time() * 1000) + math.floor(random.random() * 100000))
    }
    pre_headers = headers.copy()
    pre_headers['Host'] = 'login.sina.com.cn'
    pre_headers['Referer'] = 'https://passport.weibo.cn/signin/login'
    pre_url = 'https://login.sina.com.cn/sso/prelogin.php'
    pre_text = Session.get(pre_url, params=pre_Data, headers=pre_headers).text
    try:
        pre_json = json.loads(pre_text[0])
        if pre_json['showpin'] == 1:  # 验证码
            pre_headers['Host'] = 'passport.weibo.cn'
            capt = Session.get(
                'https://passport.weibo.cn/captcha/image', headers=pre_headers)
            capt_json = capt.json()
            capt_base64 = capt_json["data"]["image"].split('base64',)[
                1]  # captcha image
            with open('../../data/weibo_data/captcha.png', 'wb') as f:
                f.write(base64.b64encode(capt_base64))
                f.close()
            img = Image.open('../../data/weibo_data/captcha.png')
            img.show()
            img.close()
            captcha = raw_input('input captcha:\n>')
            return captcha, capt_json["data"]["pcid"]
    except Exception, e:
        # print Exception, ':', e  # no captcha
        return ''


def login(username, password, Session, pincode):
    '''
    模拟登录手机端微博
    '''
    login_url = "https://passport.weibo.cn/signin/login"
    data = {
        'username': username,
        'password': password,
        'savestate': '1',
        'r': 'http://m.weibo.cn/',
        'ec': '0',
        'pagerefer': login_url,
        'entry': 'mweibo',
        'wentry': '',
        'loginfrom': '',
        'client_id': '',
        'code': '',
        'qq': '',
        'mainpageflag': '1',
        'hff': '',
        'hfp': '',
    }
    login_headers = headers.copy()

    login_headers['Host'] = 'passport.weibo.cn'
    login_headers['Accept-Encoding'] = 'gzip, deflate, br'
    login_headers['Accept'] = '*/*'
    login_headers['Origin'] = 'https://passport.weibo.cn'
    login_headers['Referer'] = login_url
    login_headers['Content-Type'] = 'application/x-www-form-urlencoded'
    if pincode == '':
        pass
    else:
        data['pincode'] = pincode[0]
        data['pcid'] = pincode[1]
    post_url = 'https://passport.weibo.cn/sso/login'
    # Session.get(login_url)
    slt = Session.post(post_url, data=data, headers=login_headers)
    # print slt.status_code
    # print slt.text
    login_js = slt.json()
    crossdomain = login_js['data']['crossdomainlist']
    cn = "https:" + crossdomain["sina.com.cn"]
    login_headers["Host"] = "login.sina.com.cn"
    Session.get(cn, headers=login_headers)
    return Session


def login_simulate(username, password):
    '''
    模拟登录手机端微博
    '''
    session = requests.Session()
    s_headers = headers.copy()
    s_headers['Upgrade-Insecure-Requests'] = '1'
    index_url = 'https://passport.weibo.cn/signin/login'
    session.get(index_url, headers=s_headers)
    pincode = login_pre(username, session)
    session = login(username, password, session, pincode)
    print 'login successful!'
    return session


def Get_movies(Session):
    # print 'Get moive'
    moive_headers = headers.copy()
    moive_headers['Host'] = 'm.weibo.cn'
    moive_headers['Accept-Encoding'] = 'gzip, deflate, sdch'
    moive_headers['Accept'] = 'application/json, text/plain, */*'
    moive_headers[
        'Referer'] = 'http://m.weibo.cn/p/index?containerid=10100310001'
    moive_headers['X-Requested-With'] = 'XMLHttpRequest'
    movie_url = 'http://m.weibo.cn/p/index?containerid=10100310001'
    Session.get(movie_url, headers=headers).text
    # html = askUrl(movie_url)
    #soup = BS(html, 'lxml')
    # print html
    listurl = 'http://m.weibo.cn/api/container/getIndex?containerid=10100310001#10100310001'
    # print moive_headers
    html1 = Session.get(listurl, headers=moive_headers)
    cards = html1.json()['cards'][2]
    # print type(cards)
    cards_group = cards['card_group']
    moive_file = open('../../data/weibo_data/moive.txt', 'w')
    moive_dict = {}
    len_cards = len(cards_group)
    # print len_cards
    for i in range(1, len_cards):
        movie_item = cards_group[i]
        moive_title = movie_item['title_sub']
        moive_actor = movie_item['desc1']
        moive_score = movie_item['desc2']
        moive_url = movie_item['scheme']
        moive_id = movie_item['object_id']
        moive_dict[moive_title] = moive_url  # 传递电影参数
        moive_file.write('ID:' + str(moive_id) + '\n')
        moive_file.write("title:" + str(moive_title) + '\n')
        moive_file.write('url:' + str(moive_url) + '\n')
        moive_file.write('actor:' + str(moive_actor) + '\n')
        moive_file.write('score:' + str(moive_score) + '\n')
    moive_file.close()
    return moive_dict


def Get_moive_detail(filename, filmurl, session):
    '''
    获取电影详情页内容
    '''
    baseurl = 'http://m.weibo.cn/api/container/getSecond?' + \
        filmurl.split('?')[1]
    detail_headers = headers.copy()
    detail_headers['Host'] = 'm.weibo.cn'
    detail_headers['X-Requested-With'] = 'XMLHttpRequest'
    detail_headers['Accept-Encoding'] = 'gzip, deflate, sdch'
    detail = session.get(baseurl, headers=detail_headers)
    detail = detail.json()
    detail_file = open('../../data/weibo_data/movie_detail/' +
                       filename + '.txt', 'w')
    detail_file.write('movie_title:' + filename + '\n')
    items = detail['cards'][0]['card_group']
    len_ls = len(items)
    # print len_ls
    for i in range(0, len_ls):
        item = items[i]
        detail_file.write(item['item_name'] + ':' +
                          item['item_content'] + '\n')
    detail_file.close()


def Get_short_comment(filename, url, session):
    '''
    电影短点评   
    '''
    target_url = 'http://m.weibo.cn/api/container/getIndex?' + \
        url.split('?')[1]
    short_headers = headers.copy()
    short_headers['Host'] = 'm.weibo.cn'
    short_json = session.get(target_url, headers=short_headers)
    cards = short_json['cards']
    tuan_comment_score = cards['group'][0]['title_sub']  # 点评团评分
    tuan_comment_url = cards['group'][0]['scheme']
    Get_tuan_comment(filename, tuan_comment_url, session)  # 点评团点评
    Net_friend_score = cards['group'][1]['title_sub']  # 网友评分
    Net_friend_url = cards['group'][1]['scheme']
    Get_Net_friend_comment(filename, Net_friend_url, session)  # 网友点评


def Get_Net_friend_comment(filename, url, session):
    '''
    网友点评
    '''
    friend_url = url.split('?')[1]
    sub_url_pattern = r'\%3A'
    friend_url = re.sub(sub_url_pattern, ':', friend_url)
    sub_url_pattern = r'__group__'
    friend_url = re.sub(sub_url_pattern, '__normal__', friend_url)
    friend_url = 'http://m.weibo.cn/api/container/getIndex?' + friend_url
    friend_headers = headers.copy()
    friend_headers['Host'] = 'm.weibo.cn'
    page = 1
    sinceid = ''
    while True:
        if page == 1:
            sinceid = ''
        else:
            sinceid = '&since_id=' + since_id
        friend_req_url = friend_url + sinceid
        # print '>>>>>>>>>', friend_req_url
        friend_comment_json = session.get(
            friend_req_url, headers=friend_headers)
        friend_comment_json = friend_comment_json.json()
        print friend_comment_json['cardlistInfo']
        since_id = friend_comment_json['cardlistInfo']['since_id']
        json_ok = friend_comment_json['ok']
        if json_ok == 0:
            break
        card_group_ls = friend_comment_json['cards'][0]['card_group']
        cards_len = len(card_group_ls)
        for i in range(0, cards_len):
            item = card_group_ls[i]
            blog_url = item['scheme']
            Get_weibo_and_comment(filename, blog_url, session)
            itemid = item['itemid']
            mblog = item['mblog']
            create_time = mblog['created_at']
            blogid = mblog['id']
            source = mblog['source']
            favorited = mblog['favorited']
            isLongText = mblog['isLongText']
            rid = mblog['rid']
            # 用户信息
            useinfo = mblog['user']
            usrid = useinfo['id']
            username = useinfo['screen_name']
            print username
            userurl = useinfo['profile_url']
            statuses_count = useinfo['statuses_count']
            verified = useinfo['verified']
            verified_type = useinfo['verified_type']
            usedescription = useinfo['description']
            gender = useinfo['gender']
            mbtype = useinfo['mbtype']
            urank = useinfo['urank']
            mbrank = useinfo['mbrank']
            followers_count = useinfo['followers_count']
            follow_count = useinfo['follow_count']
        page = page + 1
        #sinceid = ''


def Get_tuan_comment(filename, url, session):
    '''
    点评团点评
    '''
    tuan_url = url.split('?')[1]
    sub_url_pattern = r'\%3A'
    tuan_url = re.sub(sub_url_pattern, ':', tuan_url)
    tuan_url = 'http://m.weibo.cn/api/container/getIndex?' + tuan_url
    tuan_headers = headers.copy()
    tuan_headers['Host'] = 'm.weibo.cn'
    page = 1
    page_str = ''
    while True:
        if page != 1:
            page_str = '&page=' + str(page)
        tuan_req_url = tuan_url + page_str
        tuan_comment_json = session.get(tuan_req_url, headers=tuan_headers)
        tuan_comment_json = tuan_comment_json.json()
        json_ok = tuan_comment_json['ok']
        if json_ok == 0:
            break
        card_group_ls = tuan_comment_json['cards'][0]['card_group']
        cards_len = len(card_group_ls)
        for i in range(0, cards_len):
            item = card_group_ls[i]
            blog_url = item['scheme']
            Get_weibo_and_comment(filename, blog_url, session)
            itemid = item['itemid']
            mblog = item['mblog']
            create_time = mblog['created_at']
            blogid = mblog['id']
            source = mblog['source']
            favorited = mblog['favorited']
            isLongText = mblog['isLongText']
            rid = mblog['rid']
            # 用户信息
            useinfo = mblog['user']
            usrid = useinfo['id']
            username = useinfo['screen_name']
            print username
            userurl = useinfo['profile_url']
            statuses_count = useinfo['statuses_count']
            verified = useinfo['verified']
            verified_type = useinfo['verified_type']
            usedescription = useinfo['description']
            gender = useinfo['gender']
            mbtype = useinfo['mbtype']
            urank = useinfo['urank']
            mbrank = useinfo['mbrank']
            followers_count = useinfo['followers_count']
            follow_count = useinfo['follow_count']
        page = page + 1


def Get_relation(filename, url, session):
    '''
    相关话题
    '''
    document = '../../data/weibo_data/relation_topic/' + filename + '.txt'
    id_pattern = r'(?<=containerid=).*?(?=_)'
    contain_id = re.search(id_pattern, url).group()
    relation_headers = headers.copy()
    relation_headers['Host'] = 'm.weibo.cn'
    relation_headers['X-Requested-With'] = 'XMLHttpRequest'
    page = 1
    while True:
        if page == 1:
            page_str = ''
        else:
            page_str = '&page=' + str(page)
        topic_url = 'http://m.weibo.cn/api/container/getIndex?containerid=' + \
            contain_id + '_-_cardlist_huati' + page_str + url[-65:]
        relation_topic = session.get(topic_url, headers=relation_headers)
        relation_topic = relation_topic.json()
        relation_ok = relation_topic['ok']
        if relation_ok == 0:
            break

        relation_cards = relation_topic['cards'][0]['card_group']
        cardls_len = len(relation_cards)
        for i in range(0, cardls_len):
            item = relation_cards[i]
            blog_url = item['scheme']
            Get_weibo_and_comment(filename, blog_url, session)
            itemid = item['itemid']
            mblog = item['mblog']
            mnlog_id = mblog['id']
            try:
                textLength = mblog['textLength']  # 有的json没有
            except:
                textLength = 'None'
            source = mblog['source']
            favorited = mblog['favorited']
            isLongText = mblog['isLongText']
            rid = mblog['rid']
            bid = mblog['bid']
            # 用户信息
            useinfo = mblog['user']
            usrid = useinfo['id']
            username = useinfo['screen_name']
            print username
            userurl = useinfo['profile_url']
            statuses_count = useinfo['statuses_count']
            verified = useinfo['verified']
            verified_type = useinfo['verified_type']
            usedescription = useinfo['description']
            gender = useinfo['gender']
            mbtype = useinfo['mbtype']
            urank = useinfo['urank']
            mbrank = useinfo['mbrank']
            followers_count = useinfo['followers_count']
            follow_count = useinfo['follow_count']
        page = page + 1


def Get_weibo_and_comment(filename, url, session):
    '''
    微博内容及对应的评论
    '''
    blog_headers = headers.copy()
    blog_headers['Host'] = 'm.weibo.cn'
    mblogid_pattern = r'(?<=mblogid=).*?(?=&)'
    mblogid = re.search(mblogid_pattern, url).group()  # mblogid
    blog_content_url = 'http://m.weibo.cn/statuses/extend?id=' + mblogid
    blog_content = session.get(blog_content_url, headers=blog_headers)
    blog_content_json = blog_content.json()
    if blog_content_json['ok'] == '0':
        pass
    else:
        longTextContent = blog_content_json['longTextContent']  # 微博内容
        reposts_count = blog_content_json['reposts_count']  # 转发
        comments_count = blog_content_json['comments_count']  # 评论
        attitudes_count = blog_content_json['attitudes_count']  # 点赞

    page = 1
    while True:  # 评论很多页
        blog_comment_url = 'http://m.weibo.cn/api/comments/show?id=4094973479614586&page=' + \
            str(page)
        blog_comment = session.get(blog_comment_url, headers=blog_headers)
        blog_comment = blog_comment.json()
        blog_ok = blog_comment['ok']
        if blog_ok != 0:
            data = blog_comment['data']
            data_len = len(data)
            for i in range(0, data_len):
                item = data[i]
                comment_id = item['id']
                create_time = item['created_at']
                sourece = item['source']
                comment_text = item['text']
                like_counts = item['like_counts']
                liked = item['liked']
                user = item['user']
                user_id = user['id']
                username = user['screen_name']
                # print username
                user_verified_type = user['verified_type']
                user_mbtype = user['mbtype']
                user_url = user['profile_url']
            page = page + 1
        else:
            break  # 页面加载完


def Get_hot_comment(flag, url, filename, session):
    '''
    好评和差评的格式一样，整合为一个函数
    '''
    if flag == 1:
        document = '../../data/weibo_data/good_comment/' + filename + '.txt'
        cardlist_str = '_-_cardlist_goodweibo&'
        title = '好评微博'

    else:
        document = '../../data/weibo_data/bad_comment/' + filename + '.txt'
        cardlist_str = '_-_cardlist_badweibo&'
        title = '差评微博'

    id_pattern = r'(?<=containerid=).*?(?=&)'
    contain_id = re.search(id_pattern, url).group()
    hot_headers = headers.copy()
    hot_headers['Host'] = 'm.weibo.cn'
    hot_headers['X-Requested-With'] = 'XMLHttpRequest'
    page = 1
    while True:
        if page == 1:
            page_str = ''
        else:
            page_str = 'page=' + str(page) + '&'
        hot_url = 'http://m.weibo.cn/api/container/getIndex?containerid=' + contain_id +\
            cardlist_str + page_str + 'count=20&title=' + urllib.quote(title)
        hot_content_json = session.get(hot_url, headers=hot_headers)
        hot_content = hot_content_json.json()
        hot_ok = hot_content['ok']
        if hot_ok == 0:  # 页面加载完
            break

        cards_group = hot_content['cards'][0]['card_group']
        cards_len = len(cards_group)
        for i in range(0, cards_len):
            item = cards_group[i]
            blog_url = item['scheme']
            Get_weibo_and_comment(filename, blog_url, session)  # 微博内容及评论信息
            # 微博信息
            rating = item['rating']
            mblog = item['mblog']
            mnlog_id = mblog['id']
            try:
                textLength = mblog['textLength']  # 有的json没有
            except:
                textLength = 'None'
            source = mblog['source']
            favorited = mblog['favorited']
            isLongText = mblog['isLongText']
            rid = mblog['rid']
            attitudes_status = mblog['attitudes_status']
            bid = mblog['bid']
            # 用户信息
            useinfo = mblog['user']
            usrid = useinfo['id']
            username = useinfo['screen_name']
            print username
            userurl = useinfo['profile_url']
            statuses_count = useinfo['statuses_count']
            verified = useinfo['verified']
            verified_type = useinfo['verified_type']
            usedescription = useinfo['description']
            gender = useinfo['gender']
            mbtype = useinfo['mbtype']
            urank = useinfo['urank']
            mbrank = useinfo['mbrank']
            followers_count = useinfo['followers_count']
            follow_count = useinfo['follow_count']
        page = page + 1  # 下一页


def Get_movie_comment(filmname, filmurl, session):
    '''
    获取电影内容
    '''
    baseurl = 'http://m.weibo.cn/api/container/getIndex?'
    req_url = baseurl + str(filmurl.split('?')[1])
    req_headers = headers.copy()
    req_headers['Host'] = 'm.weibo.cn'
    req_headers['X-Requested-With'] = 'XMLHttpRequest'
    req_headers['Referer'] = filmurl
    req_headers['Accept'] = 'application/json, text/plain, */*'
    req_headers['Accept-Encoding'] = 'gzip, deflate, sdch'
    req_json = session.get(req_url, headers=req_headers)
    req_json = req_json.json()
    movie_info = req_json['pageInfo']
    moive_cards = req_json['cards']
    print movie_info['page_title']

    detail_url = movie_info['desc_scheme']  # 电影详情页
    Get_moive_detail(filmname, detail_url, session)
    try:  # 有短点评（对应页面的影评button）
        short_comment_url = moive_cards[4][
            'card_group'][0]['group'][2]['scheme']
        Get_short_comment(filmname, short_comment_url, session)  # 短点评
        print short_comment_url

    except:  # 无
        pass
    relation_url = moive_cards[4]['card_group'][4]['scheme']  # 相关
    Get_relation(filmname, relation_url, session)
    Get_hot_comment(1, filmurl, filmname, session)  # 好评微博
    Get_hot_comment(0, filmurl, filmname, session)  # 差评微博


def fish_data(session):
    '''
    钓鱼
    '''
    fish_headers = headers.copy()
    fish_headers['Host'] = 'm.weibo.cn'
    fish_headers['X-Requested-With'] = 'XMLHttpRequest'
    fish_headers['Referer'] = 'http://m.weibo.cn/mblog'
    fish_headers['Origin'] = 'http://m.weibo.cn'
    blogcontent = '速度与激情8 你给几分？@爱上电影-'
    formdata = {
        'content': blogcontent,
        'annotations': '',
        'st': 'aefc55',
    }
    fish_url = 'http://m.weibo.cn/mblogDeal/addAMblog'
    resp = session.post(fish_url, data=formdata, headers=fish_headers)
    response_json = resp.json()
    if response_json['ok'] == 1:
        print 'send successful'
    else:
        print 'send failure'


def main():
    username = '18045177508'
    password = 'MJY123456'
    session = login_simulate(username, password)
    fish_data(session)
    #moive_dict = Get_movies(session)
    # for item in moive_dict:
    #    Get_movie_comment(item, moive_dict[item], session)

    #Get_relation('file', 'http://m.weibo.cn/p/index?containerid=100120177778_-_cardlist_huati&page=1&count=20&luicode=10000011&lfid=100120177778&featurecode=20000180', session)
    #Get_tuan_comment('file', 'http://m.weibo.cn/p/index?containerid=230530100120107740__group__mobile_info_-_pageapp%253A230564a2607872b4b3f8d684a4b8acbc65b4d7&luicode=10000011&lfid=230530100120107740__all__mobile_info_-_pageapp%3A230564a2607872b4b3f8d684a4b8acbc65b4d7&featurecode=20000180', session)
    #Get_Net_friend_comment('file', 'http://m.weibo.cn/p/index?containerid=230530100120107740__group__mobile_info_-_pageapp%253A230564a2607872b4b3f8d684a4b8acbc65b4d7&luicode=10000011&lfid=230530100120107740__all__mobile_info_-_pageapp%3A230564a2607872b4b3f8d684a4b8acbc65b4d7&featurecode=20000180', session)
if __name__ == '__main__':
    main()
