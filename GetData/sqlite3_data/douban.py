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
import sqlite3
import random
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

myagent = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729)',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/57.0.2987.98 Chrome/57.0.2987.98 Safari/537.36']

ipaddress=[
    '110.243.243.82:11355','61.186.164.98:8080','27.227.252.32:32212','14.204.22.180:40938','61.186.164.98:8080']

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
    headers = {
        "Host": "www.douban.com",
        "User-Agent":random.choice(myagent),
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.6",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Connection": "keep-alive"
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
        document = 'login_captcha_douban.jpg'
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
    headers = {
    'User-Agent':random.choice(myagent),
    }
    try:
        html = session.get(url, allow_redirects=False,headers=headers).text
    except:
        proxy={'https':'https://'+random.choice(ipaddress)}
        html = session.get(url, allow_redirects=False,headers=headers,proxies=proxy).text
    return html

def Get_movie_from_database(conn):
    '''
    从数据库中拿电影的信息
    '''
    cur = conn.cursor()
    cur.execute('select name,url from movies')
    movies = cur.fetchall()
    cur.close()
    return movies

def Get_file_critic_(baseurl,filmname,conn):
    '''
    影评的url可以通过电影的url截取获得
    '''
    #cur = conn.cursor()
    ls = []
    short_comment_url = str(baseurl)[:42] + 'comments?status=P'
    ls.append(short_comment_url)
    ask_url = str(baseurl)[:42] + 'questions/?from=subject'
    ls.append(ask_url)
    long_comment_url = str(baseurl)[:42] + 'reviews'
    ls.append(long_comment_url)
    return ls #截断
    '''
    movie_html = askUrl(baseurl)
    soup = BeautifulSoup(movie_html,'lxml')
    content = soup.find('div',id='content')
    short_comment_num = content.find('div',id="comments-section").find('h2').find('a').get_text()
    questions_num = content.find('div',id='askmatrix').find('h2').find('a').get_text().strip(' ')
    long_comment_num = content.find('section','reviews mod movie-content').find('h2').find('a').get_text()

    if content is not None:
        movie_h1 = content.find('h1')
        movie_h1 = movie_h1.find_all('span')
        movie_title =movie_h1[0].get_text()
        movie_year = movie_h1[1].get_text()
        article = content.find('div','article')
        movie_info_ls = article.find('div',id='info').find_all('span','attrs')

        info  = content.find('div',id='info')
        info_ls = str(info).split('br/')
        info_len = len(info_ls) #8 9 10 11 12  总长度12 11是缺少官方网站 10 缺少官方网站和IMDB链接 9缺少编剧 8缺少时长
        index = 0
        director = movie_info_ls[index].find('a').get_text() #导演
        index = index + 1
        if info_len > 9:
            screenwriter = movie_info_ls[1].find('a').get_text()#编剧
            index = index + 1
        else:
            screenwriter='None'
        actors_ls = movie_info_ls[index].find_all('a')
        actors = ''
        for i in range(0,len(actors_ls)):#演员
            actors = actors + actors_ls[i].get_text() +'/'
        index = index + 1

        movietype_pattern = r'(?<=<span property="v:genre">).*?(?=</span>)'
        typelist = re.findall(movietype_pattern, str(info))
        movie_type='' #电影类别
        for i in range(0, len(typelist)):
            movie_type = movie_type+typelist[i]+'/'
        index = index +1

        if info_len==12: #官方网站 
            movie_offical_url =re.search(r'<a href=\"(.*?)\" rel="nofollow"',info_ls[index])
            index=index+1
        else:
            movie_offical_url = 'None'

        movie_country = re.search(r'(?<=</span>).*?(?=<)',info_ls[index]).group()#制片国家
        index = index +1
        movie_language = re.search(r'(?<=</span>).*?(?=<)',info_ls[index]).group()#语言
        index = index +1
        movie_release = re.findall(r'(?<=content=\").*?(?=\">)',info_ls[index])#上映日期
        movie_release_time=''
        for i in range(0,len(movie_release)):
            movie_release_time = movie_release_time + movie_release[i]+'/'

        index = index + 1
        if info_len > 8 :
            print filmname
            movie_time = re.search(r'(?<=content=\").*?(?=\")',info_ls[index]).group() #片长
            index = index + 1
        else:
            movie_time='None'

        nick_name = re.search(r'(?<=</span>).*?(?=<)',info_ls[index])
        if nick_name is None:
            nick_name='None'
        else:
            nick_name=nick_name.group().encode('utf-8') #又名
        index = index + 1
        if info_len == 10:
            IMDB = 'None'
        else:
            if index >=info_len:
                IMDB='None'
            else:
                IMDB = re.search(r'(?<=<a href=\").*?(?=\" target="_blank")',info_ls[index])
                if IMDB is None:
                    IMDB='None'
                else:
                 IMDB = IMDB.group().encode('utf-8') #IMDB链接
        description = content.find('div','indent',id='link-report').find('span').get_text().strip(' ').encode('utf-8')

        insert_movies = "insert into movies values('"+filmname+"','"+movie_year+"','"+baseurl+\
            "','"+long_comment_url+"','"+long_comment_num+"','"+short_comment_url+"','"+short_comment_num \
            +"','"+ask_url+"','"+questions_num+"','"+director+"','"+screenwriter+"','"+actors+"','"+\
            movie_type+"','"+movie_country+"','"+movie_language+"','"+movie_release_time+"','"+\
            movie_time+"','"+nick_name+"','"+IMDB+"','"+description+"')"
        cur.execute(insert_movies)

        score_content =content.find('div',id='interest_sectl')
        rating_box = score_content.find('div','rating_wrap clearbox')
        if rating_box is not None:
            movie_score = rating_box.find('strong','ll rating_num').get_text()
            if movie_score != '':
                comment_num = rating_box.find('div','rating_sum').find('span').get_text()
                ratings_weight = rating_box.find('div','ratings-on-weight')
                if ratings_weight is not None:
                    items = ratings_weight.find_all('div','item')
                    star5_percentge = items[0].find('span','rating_per').get_text()
                    star4_percentge = items[1].find('span','rating_per').get_text()
                    star3_percentge = items[2].find('span','rating_per').get_text()
                    star2_percentge = items[3].find('span','rating_per').get_text()
                    star1_percentge = items[4].find('span','rating_per').get_text()

                insert_score_box = "insert into score_box values('"+filmname+"',"+movie_score+","+\
                    comment_num+",'"+star5_percentge+"','"+star4_percentge+"','"+star3_percentge +\
                    "','"+star2_percentge+"','"+star1_percentge+"')"
                cur.execute(insert_score_box)
                conn.commit()

        rating_betterthan = score_content.find('div','rating_betterthan')
        if rating_betterthan is not None:
            better_ls = rating_betterthan.find_all('a')
            for k in range(0,len(better_ls)):
                better_item = better_ls[k].get_text()
                insert_better_than = "insert into better_than values('"+filmname+"','"+better_item+"')"
                cur.execute(insert_better_than)
                conn.commit()

    cur.close()
    return ls
    '''


def save_shortcritic(filename, baseurl, session,conn):
    '''
    短影评下载
    '''
    print filename
    page = 0
    next_page_url = ''
    while next_page_url is not None:
        if page == 0:
            url = baseurl
        else:
            url = baseurl[:50] + next_page_url
            #print url
        headers = {
            'User-Agent':random.choice(myagent),
            }
        html = session.get(url, allow_redirects=False,headers=headers).text
        soup = BeautifulSoup(html, 'lxml')
        for comment_item in soup.find_all('div', 'comment-item'):
            username = comment_item.find('div',"comment")
            if username is None:
                break  # 最后一页没数据的情况
            else:
                username = username.find('span','comment-info').find('a').get_text().replace('"','').replace("'","")
            userurl = comment_item.find('span', 'comment-info').find('a').get('href')
            useful = comment_item.find('span','votes')
            if useful is None:
                useful = 'None'
            else:
                useful = useful.get_text()
            comment_time = comment_item.find('span', 'comment-time').get('title')
            comment_content = comment_item.find('p', "").get_text()
            comment_content = comment_content.replace('"','""').strip('\n')
            comment_content = comment_content.replace("'","''").strip(' ')
            # comment_info = comment_item.find('span', "comment-info")
            # givescore = comment_info.find('span').get('class')
            givescore = re.search(
                r'(?<=<span class=\"allstar).*?(?= rating")', str(comment_item), re.S | re.M | re.I)
            if givescore is not None:
                givescore = givescore.group()
            else:
                givescore = 'None'
            #----
            useless = 'None'
            comment_title = "None"
            cur =conn.cursor()
            #print comment_title,comment_content,url

            #print insert_comments_str
            try:
                cur.execute("insert into comments values(?,?,?,?,?,?,?,?,?,?,?)",(filename,'short',username \
                    ,userurl,useful,useless,str(givescore),comment_time,comment_title,comment_content,url))
            except Exception,e:
                #print insert_comments_str
                print Exception,'-->>>',e
            cur.close()
            conn.commit()
        next_page = soup.find('div', 'center', id='paginator')
        if next_page is not None:
            if page == 0:
                next_page_url = next_page.find('a').get('href')
            else:
                try:
                    next_page_url = next_page.find_all('a')[2].get('href')
                except:
                    break
            page = page + 1
        else:
            break
        #print next_page_url
        #time.sleep(1)
        if page%50==0:
            print 'page->', page
    print 'page:', page


def long_filmcomment(url, filmname, session,conn):
    '''
    根据链接存长影评
    '''
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
    data_content = data_content.replace('"','""') #特殊字符需要转义字符
    data_content = data_content.replace("'","''")
    comment_num = url[-8:]
    comment_num = str(comment_num)[:7]
    useful = soup.find('button', 'btn useful_count ' +
                       comment_num + ' ').get_text().strip(' ')
    useless = soup.find('button', 'btn useless_count ' +
                        comment_num + ' ').get_text().strip(' ')

    #print "-------------------------"
    cur = conn.cursor()
    insert_comments_str = "insert into comments values('"+filmname+"',"+"'long'"+",'"+username+"','"+userurl+\
        "','"+useful+"','"+useless+"'," +str(givescore)+",'"+comment_time+"','"+comment_title+"','" +\
        data_content+"','"+data_url+"')"
    try:
        cur.execute(insert_comments_str)
    except Exception,e:
        #print insert_comments_str
        print Exception,e
    cur.close()
    conn.commit()
    return 1

def save_longcritic(filmname, baseurl, session,conn):
    '''长影评
    '''
    next_page_url = ''
    page = 0
    while next_page_url is not None:
        url = baseurl + next_page_url
        html = askUrl(url)
        soup = BeautifulSoup(html, 'lxml')
        for item in soup.find_all('h3', 'title'):
            comment_url = item.find('a', 'title-link').get('href')
            try:
                long_filmcomment(comment_url, filmname, session,conn)
            except Exception, e:
                #print Exception, ':', e
                print 'error page:', page
                continue
        next_page = soup.find('span','next')
        if next_page is not None:
            next_page_url = next_page.find('a')
            if next_page_url is not None:
                next_page_url = next_page_url.get('href')
                page = page + 1
            else:
                break
        else:
            break
        time.sleep(30)
        if page%10 ==0:
            print 'page:',page
    print 'page = ', page


def main():
    conn = sqlite3.connect('douban.db')
    conn.text_factory = str
    session = login()
    main_url = 'https://movie.douban.com/cinema/nowplaying/haerbin/'
    main_html = askUrl(main_url)
    movies = Get_movie_from_database(conn)
    #film_dict = GetTitleUrl(main_html)
    for i in range(11,len(movies)):
        item = movies[i]
        ls = Get_file_critic_(item[1],item[0],conn)
        #print film.decode('utf-8'), ls[0]
        save_shortcritic(item[0],ls[0], session,conn)
        #save_longcritic(item[0], ls[2], session, conn)
        #time.sleep(60)
    conn.close()

if __name__ == '__main__':
    main()
