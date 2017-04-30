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
import json
import base64
import time
import math
import random
from urllib import quote_plus
from PIL import Image
import sqlite3

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
    #login_js = slt.json()
    #crossdomain = login_js['data']['crossdomainlist']
    #cn = "https:" + crossdomain["sina.com.cn"]
    #login_headers["Host"] = "login.sina.com.cn"
    #Session.get(cn, headers=login_headers)
    return Session


def login_simulate(username, password):
    '''
    模拟登录手机端微博
    '''
    session = requests.Session()
    s_headers = headers.copy()
    s_headers['Upgrade-Insecure-Requests'] = '1'
    s_headers['Host']='passport.weibo.cn'
    index_url = 'https://passport.weibo.cn/signin/login'
    session.get(index_url, headers=s_headers)
    try:
        pincode = login_pre(username, session)
        session = login(username, password, session, pincode)
    except:
        session = login(username, password, session, '')
    print 'login successful!'
    return session


def Get_movies(Session):
    # print 'Get moive'
    moive_headers = headers.copy()
    moive_headers['Host'] = 'm.weibo.cn'
    moive_headers['Accept-Encoding'] = 'gzip, deflate, sdch'
    moive_headers['Accept'] = 'application/json, text/plain, */*'
    moive_headers['Referer'] = 'http://m.weibo.cn/p/index?containerid=10100310001'
    moive_headers['X-Requested-With'] = 'XMLHttpRequest'
    movie_url = 'http://m.weibo.cn/p/index?containerid=10100310001'
    Session.get(movie_url, headers=headers).text
    listurl = 'http://m.weibo.cn/api/container/getIndex?containerid=10100310001#10100310001'
    html1 = Session.get(listurl, headers=moive_headers)
    html = html1.json()
    cards = html['cards'][2]
    cards_group = cards['card_group']
    moive_lists = []
    len_cards = len(cards_group)
    for i in range(1, len_cards):
        movie_item = cards_group[i]
        moive_title = movie_item['title_sub']
        moive_url = movie_item['scheme']
        movie_ls =[]
        movie_ls.append(moive_title)
        movie_ls.append(moive_url)
        moive_lists.append(movie_ls)
    return moive_lists

def Get_movies_from_database(conn):
    '''
    电影会更新，分块爬取数据，
    这里取数据库里已存的电影进行爬取对应的评论
    '''
    cur = conn.cursor()
    cur.execute('select movie_name,movieUrl from movies')
    movies = cur.fetchall()
    cur.close()
    return movies

def Get_moive_detail(filmname, filmurl, session, conn):
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
    item = detail['cards'][0]['card_group']
    len_ls = len(item)
    # print len_ls
    if len_ls == 11:
        movie_name = item[0]['item_content']
        en_nume = item[1]['item_content']
        nick_name = item[2]['item_content']
        director = item[3]['item_content']
        writescreen = item[4]['item_content']
        actors = item[5]['item_content']
        movie_type = item[6]['item_content']
        country = item[7]['item_content']
        releas_time = item[8]['item_content']
        time_long = item[9]['item_content']
        description = item[10]['item_content']
        description = description.replace('"','\\\"').replace("'","\\\'")
        cur = conn.cursor()
        cur.execute("insert into movies_detail values(?,?,?,?,?,?,?,?,?,?,?)",(movie_name,en_nume,nick_name,director\
                ,writescreen,actors,movie_type,country,releas_time,time_long,description))
        conn.commit()
        cur.close()


def Get_short_comment(filmname, url, session, conn):
    '''
    电影短点评   
    '''
    target_url = 'http://m.weibo.cn/api/container/getIndex?' + \
        url.split('?')[1]
    short_headers = headers.copy()
    short_headers['Host'] = 'm.weibo.cn'
    short_json = session.get(target_url, headers=short_headers)
    cards = short_json.json()['cards']
    tuan_comment_score = cards[0]['group'][0]['title_sub']  # 点评团评分
    tuan_comment_url = cards[0]['group'][0]['scheme']
    Get_tuan_comment(filmname, tuan_comment_url, session, conn)  # 点评团点评  已存
    Net_friend_score = cards[0]['group'][1]['title_sub']  # 网友评分
    Net_friend_url = cards[0]['group'][1]['scheme']
    Get_Net_friend_comment(filmname, Net_friend_url, session, conn)  # 网友点评


def Get_Net_friend_comment(filmname, url, session, conn):
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
    presinceid = ''
    sinceid = ''
    since_id=''
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
        json_ok = friend_comment_json['ok']
        if json_ok == 0:
            break
        presinceid = since_id
        try:
            since_id = friend_comment_json['cardlistInfo']['since_id']
        except:
            break
        print 'page= ',page
        page = page + 1
        if since_id is None or presinceid==since_id:#页面结束
            break
        card_group_ls = friend_comment_json['cards'][0]['card_group']
        cards_len = len(card_group_ls)
        for i in range(0, cards_len):
            blog_item = card_group_ls[i]
            blog_type='NetFriend'
            Get_weibo_and_comment(filmname, blog_type, blog_item, session, conn)
        time.sleep(2)
        if page%10==0:
            time.sleep(5)


def Get_tuan_comment(filmname, url, session, conn):
    '''
    点评团点评
    '''
    cur = conn.cursor()
    tuan_url = url.split('?')[1]
    sub_url_pattern = r'\%3A'
    tuan_url = re.sub(sub_url_pattern, ':', tuan_url)
    tuan_url = 'http://m.weibo.cn/api/container/getIndex?' + tuan_url
    tuan_headers = headers.copy()
    tuan_headers['Host'] = 'm.weibo.cn'
    page = 1
    prepage = 1
    page_str = ''
    while True:
        if page != 1:
            page_str = '&page=' + str(page)
        tuan_req_url = tuan_url + page_str
        tuan_comment_json = session.get(tuan_req_url, headers=tuan_headers)
        #print tuan_req_url.encode('utf-8')
        tuan_comment_json = tuan_comment_json.json()
        json_ok = tuan_comment_json['ok']
        if json_ok == 0:
            break
        prepage = page #当两次访问页面一样时代表已经达到访问被限制的页数
        page = tuan_comment_json['cardlistInfo']['page']
        if page is None or prepage==page: #页面结束
            break
        card_group_ls = tuan_comment_json['cards'][0]['card_group']
        cards_len = len(card_group_ls)
        for i in range(0, cards_len):
            item = card_group_ls[i]
            movie_name = filmname
            blog_type = 'dianpingtuan'
            Get_weibo_and_comment(filmname, blog_type, item, session, conn)
        time.sleep(2)


def Get_relation(filmname, url, session, conn):
    '''
    相关话题
    '''
    print url
    id_pattern = r'(?<=containerid=).*?(?=_)'
    contain_id = re.search(id_pattern, url).group()
    relation_headers = headers.copy()
    relation_headers['Host'] = 'm.weibo.cn'
    relation_headers['X-Requested-With'] = 'XMLHttpRequest'
    page = 1
    prepage=1
    while True:
        if page == 1:
            page_str = ''
            topic_url = 'http://m.weibo.cn/api/container/getIndex?containerid=' + \
            contain_id +'_-_cardlist_huati'+ page_str + url[-44:]
        else:
            page_str = '&page=' + str(page)
            topic_url = 'http://m.weibo.cn/api/container/getIndex?containerid=' + \
                contain_id +'_-_cardlist_huati'+ page_str + url[-44:]
        #print topic_url
        relation_topic = session.get(topic_url, headers=relation_headers)
        relation_topic = relation_topic.json()
        relation_ok = relation_topic['ok']
        if relation_ok == 0:
            break
        prepage = page
        #print 'page->',page
        page = relation_topic['cardlistInfo']['page']
        if page is None or prepage==page:
            break
        relation_cards = relation_topic['cards'][0]['card_group']
        cardls_len = len(relation_cards)
        for i in range(0, cardls_len):
            blog_item = relation_cards[i]
            Get_weibo_and_comment(filmname, 'xiangguanhuati', blog_item, session,conn)
            #把json数据传进去，在评论里解析
        time.sleep(2)
        if page%10==0:
            print 'page:',page
            time.sleep(5)


def Get_weibo_and_comment(filmname, blog_type, blog_item, session, conn):
    '''
    微博内容及对应的评论
    '''
    url = blog_item['scheme']
    itemid = blog_item['itemid']
    mblog = blog_item['mblog']
    mblog_id = mblog['id']
    create_time_blog = mblog['created_at']
    try:
        textLength = mblog['textLength']  # 有的json没有
    except:
        textLength = 'None'
    source = mblog['source']
    favorited = mblog['favorited']
    try:
        rating = mblog['rating']
    except:
        rating='None'
    isLongText = mblog['isLongText']
    rid = mblog['rid']
    try:
        cardid = mblog['cardid']
    except:
        cardid = 'None'
    try:
        attitudes_status = mblog['attitudes_status']
    except:
        attitudes_status = 'None'
    bid = mblog['bid']
    # 用户信息
    useinfo = mblog['user']
    usrid = useinfo['id']
    username = useinfo['screen_name']
    userurl = useinfo['profile_url']
    statuses_count = useinfo['statuses_count']
    vertified = useinfo['verified']
    vertified_type = useinfo['verified_type']
    userdescription = useinfo['description']
    gender = useinfo['gender']
    mbtype = useinfo['mbtype']
    urank = useinfo['urank']
    mbrank = useinfo['mbrank']
    followers_count = useinfo['followers_count']
    follow_count = useinfo['follow_count']

    blog_headers = headers.copy()
    blog_headers['Host'] = 'm.weibo.cn'
    mblogid_pattern = r'(?<=mblogid=).*?(?=&)'
    mblogid = re.search(mblogid_pattern, url).group()  # mblogid
    blog_content_url = 'http://m.weibo.cn/statuses/extend?id=' + mblogid
    blog_content = session.get(blog_content_url, headers=blog_headers)
    try:
        blog_content_json = blog_content.json()
    except Exception,e:
        print Exception,e
        return
    if blog_content_json['ok'] == 0:
        return #没有微博数据
    else:
        longTextContent = blog_content_json['longTextContent']  # 微博内容
        pattern_html = r'<[^>]+>'
        longTextContent = (re.sub(pattern_html,'',longTextContent)).strip(' ') #去除html标签
        reposts_count = blog_content_json['reposts_count']  # 转发
        comments_count = blog_content_json['comments_count']  # 评论
        attitudes_count = blog_content_json['attitudes_count']  # 点赞
    cur = conn.cursor()
    cur.execute('insert into weiblog values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,\
            ?,?,?,?,?,?,?,?,?)',(filmname,blog_type,url,itemid,create_time_blog,longTextContent,reposts_count,\
                comments_count,attitudes_count,cardid,mblogid,source,favorited,rating,textLength,\
                isLongText,rid,attitudes_status,bid,usrid,username,userurl,statuses_count,vertified,\
                vertified_type,userdescription,gender,mbtype,urank,mbrank,followers_count,follow_count))
    conn.commit()
    cur.close()
    #存储评论测试成功。但查看评论的数据，对毕设的效用不大，还拖慢了爬取的速度,暂时注释掉
    '''
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
            cuur = conn.cursor()
            for i in range(0, data_len):
                item = data[i]
                comment_id = item['id']
                create_time = item['created_at']
                sourece_com = item['source']
                comment_text = item['text']
                like_counts = item['like_counts']
                liked = item['liked']
                user = item['user']
                user_id = user['id']
                username = user['screen_name']
                user_vertified = user['verified']
                user_vertified_type = user['verified_type']
                user_mbtype = user['mbtype']
                user_url = user['profile_url']
                cuur.execute('insert into weicomment values(?,?,?,?,?,?,?,?,?,?,?,?,?)',(mblogid,comment_id,\
                        create_time,sourece_com,comment_text,like_counts,liked,user_id,username,user_url,\
                        vertified,vertified_type,mbtype))
                conn.commit()
            page = page + 1
        else:
            break  # 页面加载完
        cuur.close()
    '''


def Get_hot_comment(flag, url, filmname, session, conn):
    '''
    好评和差评的格式一样，整合为一个函数
    '''
    if flag == 1:
        cardlist_str = '_-_cardlist_goodweibo&'
        title = '好评微博'
        blog_type='goodweibo'

    else:
        cardlist_str = '_-_cardlist_badweibo&'
        title = '差评微博'
        blog_type='badweibo'

    id_pattern = r'(?<=containerid=).*?(?=&)'
    contain_id = re.search(id_pattern, url).group()
    hot_headers = headers.copy()
    hot_headers['Host'] = 'm.weibo.cn'
    hot_headers['X-Requested-With'] = 'XMLHttpRequest'
    page = 1
    prepage = 1
    print title
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
        prepage = page
        if page%10==0:
            print 'page->',page
        page = hot_content['cardlistInfo']['page']
        if page is None or prepage == page:
            break
        cards_group = hot_content['cards'][0]['card_group']
        cards_len = len(cards_group)
        for i in range(0, cards_len):
            item = cards_group[i]
            blog_url = item['scheme']
            Get_weibo_and_comment(filmname, blog_type, item, session, conn)  # 微博内容及评论信息
        time.sleep(2) #每页延迟2s


def Get_movie_comment(filmname, filmurl, session,conn):
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
    print req_url
    req_json = session.get(req_url, headers=req_headers)
    req_json = req_json.json()
    movie_info = req_json['pageInfo']
    moive_cards = req_json['cards']
    print movie_info['page_title'].encode('utf-8') #电影名称
    #movies表内容
    movie_name = movie_info['page_title']
    nick_name = movie_info['nick']
    evaluation = movie_info['evaluation']
    rating = evaluation['rating']
    score = evaluation['score']
    total_count = evaluation['total_count']
    moveiUrl = filmurl
    movieID = movie_info['oid']

    detail_url = movie_info['desc_scheme']  # 电影详情页
    Get_moive_detail(filmname, detail_url, session, conn) #已存
    short_comment_url='None'
    try:  # 有短点评（对应页面的影评button）
        short_comment_url = moive_cards[4]['card_group'][0]['group'][2]['scheme']
        relation_url = moive_cards[4]['card_group'][0]['group'][3]['scheme']  # 相关
    except Exception,e:  # 无
        try:
            short_comment_url = moive_cards[3]['card_group'][0]['group'][2]['scheme']
            relation_url = moive_cards[3]['card_group'][0]['group'][3]['scheme']  # 相关
        except Exception,e:
            try:
                relation_url = moive_cards[3]['card_group'][4]['scheme']  # 相关
            except:
                try:
                    short_comment_url = moive_cards[6]['card_group'][0]['group'][2]['scheme']
                    relation_url = moive_cards[6]['card_group'][0]['group'][3]['scheme']  # 相关
                except:
                    try:
                        relation_url = moive_cards[4]['card_group'][4]['scheme']  # 相关
                    except:
                        try:
                            relation_url = moive_cards[4]['card_group'][2]['scheme']  # 相关
                        except:
                            relation_url = moive_cards[6]['card_group'][3]['scheme']  # 相关
    
    cur = conn.cursor()
    cur.execute('insert into movies values(?,?,?,?,?,?,?,?,?,?)',(movie_name,nick_name,\
            rating,score,total_count,moveiUrl,detail_url,short_comment_url,relation_url,movieID))
    conn.commit()
    cur.close()

    if short_comment_url !='None':
        Get_short_comment(filmname, short_comment_url, session, conn)
    Get_relation(filmname, relation_url, session, conn)
    Get_hot_comment(1, filmurl, filmname, session, conn)  # 好评微博
    Get_hot_comment(0, filmurl, filmname, session, conn)  # 差评微博

def main():
    conn = sqlite3.connect('weibo.db')
    conn.text_factory = str
    username = '18045177508'
    password = 'MJY123456'
    session = login_simulate(username, password)
    movie_ls = Get_movies_from_database(conn)
    #moive_ls = Get_movies(session)
    for i in range(0,len(movie_ls)):
        item = movie_ls[i]
        print item[0]
        Get_movie_comment(item[0], item[1], session, conn)
        time.sleep(60)#延迟60s
    conn.close()
if __name__ == '__main__':
    main()

