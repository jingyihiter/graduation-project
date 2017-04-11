# -*- coding: utf-8 -*-
"""
Created on Sun Apr 09 11:03:39 2017

@author: 马晶义
"""

import re
import requests
import json
import urllib2
from bs4 import BeautifulSoup
import chardet
import time

headers = {
    "Host": "www.douban.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.6",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Connection": "keep-alive"
}


def login():
    '''
    模拟登陆豆瓣
    '''
    print 'simulate login'
    data = {
        'source': 'None',
        'redir': 'https://movie.douban.com/',
        'form_email': 'mr_lovegreen@163.com',
        'form_password': 'mjy123456',
        #'captcha_solution':captcha_solution,  #需要验证码的时候补充
        #'captcha_id':captcha_id,
        'login': u'登录'
    }
    login_url = 'https://www.douban.com/accounts/login'
    session = requests.Session()
    html = session.get(login_url, headers=headers).text
    captcha_img_pattern = r'(?<=<img id="captcha_image" src=\").*?(?=\")'
    captcha_image_url = re.search(
        captcha_img_pattern, html, re.S | re.M | re.I)
    if captcha_image_url is not None:  # 需要验证码
        captcha_image_url = captcha_image_url.group()
        # print captcha_image_url
        captcha_image = requests.get(
            captcha_image_url, headers=headers).content
        document = '../../data/douban_data/login_captcha_douban.jpg'
        file_ = open(document, 'wb')
        file_.write(captcha_image)
        file_.close()
        captcha_solution = raw_input('captcha_solution:')
        data['captcha-solution'] = captcha_solution
        # 获取captcha_id
        captcha_id_pattern = r'(?<=<input type="hidden" name="captcha-id" value=\").*?(?=\"/>)'
        captcha_id = re.search(captcha_id_pattern, html, re.S | re.M | re.I)
        if captcha_id is None:
            print 'captcha_id error'
        else:
            captcha_id = captcha_id.group()
            data['captcha-id'] = captcha_id
    session.post(login_url, headers=headers, data=data)
    return session


def GetTitleUrl(html):
    '''
    获取首页电影的title url
    '''
    file_dic = {}
    count = 0
    pattern = r'<li class="stitle">.*?</li>'
    # pattern_html = r'<[^>]+>'
    pattern_url = r'(?<=href=\").+?(?=\")'
    pattern_title = r'(?<=title=\").+?(?=\")'
    for item in re.findall(pattern, html, re.S | re.M | re.I):
        # title = re.sub(pattern_html,'',item)   #正文中有省略，因此使用html标签页内标题
        # title = title.strip()
        if len(item) > 0:
            count = count + 1
        intitle = re.search(pattern_title, item, re.S | re.M | re.I)
        url = re.search(pattern_url, item, re.S | re.M | re.I)
        title = intitle.group()
        url = url.group()
        file_dic[title] = url
    return file_dic


def askUrl(url):
    '''
    获取html
    '''
    request = urllib2.Request(url)
    try:
        response = urllib2.urlopen(request)
        ret_html = response.read()
    except urllib2.URLError, e:
        if hasattr(e, "code"):
            print e.code
        if hasattr(e, "reason"):
            print e.reason
    return ret_html


def Ask_session_Url(url, session):
    '''
    根据url,session获取HTML
    '''
    html = session.get(url, allow_redirects=False).text
    return html


def save_file(document, file):
    '''
    存文件
    '''
    file_ = open(document, 'wb')
    file_.write(file)
    file_.close()


def Get_file_critic_(baseurl):
    '''
    影评的url可以通过电影的url截取获得
    '''
    ls = []
    short_comment_url = str(baseurl)[:42] + 'comments?status=P'
    ls.append(short_comment_url)
    ask_url = str(baseurl)[:42] + 'questions/?from=subject'
    ls.append(ask_url)
    long_comment_url = str(baseurl)[:42] + 'reviews'
    ls.append(long_comment_url)
    return ls


def save_filecritic(filename, baseurl, session):
    '''
    短影评下载
    '''
    # writeHtml(baseurl, filename)
    document = '../../data/douban_data/comment/short/' + filename + '.txt'
    file_ = open(document, 'w')
    file_.write('movie_title:' + str(filename.encode('utf-8')) + '\n')
    page = 0
    next_page_url = ''
    while next_page_url is not None:
        if page == 0:
            url = baseurl
        else:
            url = baseurl[:50] + next_page_url
        html = session.get(url, allow_redirects=False).text
        soup = BeautifulSoup(html, 'lxml')
        for comment_item in soup.find_all('div', 'comment-item'):
            username = comment_item.find('a')
            if username is None:
                break  # 最后一页没数据的情况
            else:
                username = username.get('title')
            userurl = comment_item.find('a', '').get('href')
            useful = comment_item.find('span', 'votes').get_text()
            comment_time = comment_item.find(
                'span', 'comment-time').get('title')
            comment_content = comment_item.find('p', "").get_text()
            # comment_info = comment_item.find('span', "comment-info")
            # givescore = comment_info.find('span').get('class')
            givescore = re.search(
                r'(?<=<span class=\"allstar).*?(?= rating")', str(comment_item), re.S | re.M | re.I)
            if givescore is not None:
                givescore = givescore.group()
            else:
                givescore = 'None'
            file_.write('username:' + str(username.encode('utf-8')) + '\n')
            file_.write('userurl:' + str(userurl.encode('utf-8')) + '\n')
            file_.write('useful:' + str(useful.encode('utf-8')) + '\n')
            file_.write('givescore:' + str(givescore.encode('utf-8')) + '\n')
            file_.write('comment_time:' + str(comment_time) + '\n')
            file_.write('comment_content:' +
                        str(comment_content.encode('utf-8')) + '\n')
        next_page = soup.find('div', 'center', id='paginator')
        if next_page is not None:
            next_page_url = next_page.find('a', 'next')
            if next_page_url is not None:
                next_page_url = next_page_url.get('href')
            # print 'next_page_url=', next_page_url
        page = page + 1
    file_.close()
    print 'page:', page


def long_filmcomment(url, file, session):
    '''
    根据链接存长影评
    '''
    # url = 'https://movie.douban.com/review/8445992/'
    # session = login()
    html = session.get(url, allow_redirects=False).text
    soup = BeautifulSoup(html, 'lxml')
    comment_title = re.search(
        r'(?<=<span property="v:summary">).*?(?=</span>)', str(soup), re.S | re.M | re.I)
    if comment_title is not None:
        comment_title = comment_title.group()
    else:
        return
    main_id = soup.find('header', 'main-hd')
    username = re.search(
        r'(?<=<span property="v:reviewer">).*?(?=</span>)', str(main_id), re.S | re.M | re. I)
    if username is not None:
        username = username.group()
    userurl = re.search(r'(?<=<a href=\").*?(?=\">\s)',
                        str(main_id), re.M | re.S | re.I)
    if userurl is not None:
        userurl = userurl.group()
    else:
        userurl = 'None'
    comment_time = main_id.find('span', 'main-meta').get_text()
    givescore = re.search(
        r'(?<=<span class=\"allstar).*?(?= main-title-rating\")', str(main_id), re.S | re.M | re.I)
    if givescore is not None:
        givescore = givescore.group()
    else:
        givescore = 'None'
    content = soup.find('div', id='link-report')
    data_url = content.find('div').get('data-url')
    data_content = content.find('div', 'review-content clearfix').get_text()
    comment_num = url[-8:]
    comment_num = str(comment_num)[:7]
    useful = soup.find('button', 'btn useful_count ' +
                       comment_num + ' ').get_text()
    useless = soup.find('button', 'btn useless_count ' +
                        comment_num + ' ').get_text()

    # print "-------------------------"
    file.write('username:' + str(username) + '\n')
    file.write('userurl:' + str(userurl) + '\n')
    file.write('givescore:' + str(givescore) + '\n')
    file.write('useful:' + str(useful.encode('utf-8')) + '\n')
    file.write('useless:' + str(useless.encode('utf-8')) + '\n')
    file.write('comment_title:' + str(comment_title) + '\n')
    file.write('data_url:' + str(data_url) + '\n')
    file.write('comment_time:' + str(comment_time) + '\n')
    file.write('data_content:' + str(data_content.encode('utf-8')) + '\n')


def save_longcritic(filename, baseurl, session):
    '''长影评
    '''
    document = '../../data/douban_data/comment/long/' + filename + '_long.txt'
    file_ = open(document, 'w')
    file_.write('movie_title:' + str(filename.encode('utf-8')) + '\n')
    next_page_url = ''
    page = 0
    while next_page_url is not None:
        url = baseurl + next_page_url
        html = askUrl(url)
        soup = BeautifulSoup(html, 'lxml')
        for item in soup.find_all('h3', 'title'):
            comment_url = item.find('a', 'title-link').get('href')
            try:
                long_filmcomment(comment_url, file_, session)
            except Exception, e:
                print Exception, ':', e
                print 'error page:', page
                continue
        next_page = soup.find('span', "next")
        next_page_url = next_page.find('a')
        if next_page_url is not None:
            next_page_url = next_page_url.get('href')
        page = page + 1
    file_.close()
    print 'page = ', page


def main():
    session = login()
    main_url = 'https://movie.douban.com/cinema/nowplaying/haerbin/'
    main_html = askUrl(main_url)
    film_dict = GetTitleUrl(main_html)
    for film in film_dict:
        ls = Get_file_critic_(film_dict[film])
        print film.decode('utf-8'), ls
        save_filecritic(unicode(film, 'utf-8'), ls[0], session)
        save_longcritic(unicode(film, 'utf-8'), ls[2], session)
    #save_filecritic('file', 'https://movie.douban.com/subject/26704592/comments?status=P', session)
    #save_longcritic('long_test', 'https://movie.douban.com/subject/26309788/reviews', session)

if __name__ == '__main__':
    main()
