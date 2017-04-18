# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 10:38:39 2017

@author: 马晶义
"""

import urllib2
from bs4 import BeautifulSoup
import re
import requests
import json
import MySQLdb
import chardet
import time

def Get_json(url):
    '''
    请求获取json数据
    '''
    session = requests.session()
    json_content = session.get(url)
    return json_content.json()


def Get_html(url):
    '''
    '''
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html, 'lxml')
    return soup


def save_comment(comments_type,comment,cur,movie_name):
    '''
    评论与热评的json格式一样
    '''
    approve = comment['approve']
    approved = comment['approved']
    try:
        authInfo = comment['authInfo'].encode('utf-8')
    except:
        authInfo='None'
    avatarurl = comment['avatarurl'].encode('utf-8')
    try:
        cityName = comment['cityName'].encode('utf-8')
    except:
        cityName = 'None'
    content = comment['content'].encode('utf-8')
    content =content.replace("'","\\'")
    content = content.replace('"','\\"')
    content = content.replace('\n','')
    #print 'content - ',content
    filmView = comment['filmView']
    comment_id = comment['id']
    isMajor = comment['isMajor']
    juryLevel = comment['juryLevel']
    movieId = comment['movieId']
    nick = comment['nick'].encode('utf-8')
    nickName = comment['nickName'].encode('utf-8')
    #print nickName
    oppose = comment['oppose']
    pro = comment['pro']
    reply = comment['reply']
    score = comment['score']
    spoiler = comment['spoiler']
    startTime = comment['startTime'].encode('utf-8')
    supportComment = comment['supportComment']
    supportLike = comment['supportLike']
    sureViewed = comment['sureViewed']
    created_time = comment['time'].encode('utf-8')
    userId = comment['userId']
    userLevel = comment['userLevel']
    try:
        vipInfo = comment['vipInfo'].encode('utf-8')
    except:
        vipInfo='None'
    vipType = comment['vipType']

    insert_comments_str ="insert into comments values('"+movie_name+"','"+comments_type+"','"+str(approve)+"','"+str(approved)+\
        "','"+authInfo+"','"+avatarurl+"','"+cityName+"','"+content+"','"+str(filmView)+"','"+str(comment_id)+"','"+str(isMajor) +\
        "','"+str(juryLevel)+"','"+str(movieId)+"','"+nick+"','"+nickName+"','"+str(oppose)+"','"+str(pro)+"','"+str(reply)+"','"+str(score)+"','"+\
        str(spoiler)+"','"+startTime+"','"+str(supportComment)+"','"+str(supportLike)+"','"+str(sureViewed)+"','"+created_time+"',"+\
        str(userId)+","+str(userLevel)+",'"+vipInfo+"',"+str(vipType)+")"
    #print insert_comments_str
    cur.execute(insert_comments_str)


def Get_movie_comment_content(comment_url, comment_num,conn,movie_name):
    '''
    获取评论
    '''
    count = 0
    comment_soup = Get_html(comment_url)
    navbar_title = comment_soup.find('div', 'navbar-title').get_text()
    page = comment_num / 15  # offset 页偏移是15
    movie_id = re.search(r'(?<=movie/).*?(?=/comments)', comment_url).group()
    for i in range(0, page): #限制最多查看67页  1675条评论
        req_url = 'http://m.maoyan.com/mmdb/comments/movie/' + \
            movie_id + '.json?_v_=yes&offset=' + str(i * 15)
        cur = conn.cursor()
        comment_content_json = Get_json(req_url)
        if comment_content_json['total'] ==0: #没有权限访问了，即使登录了
            break
        try:
            comments = comment_content_json['cmts']
            for j in range(0, len(comments)):
                comment = comments[j]  # 一条评论数据
                save_comment('cmts',comment,cur,movie_name)
                count = count + 1
        except:
            pass
        try:
            hot_comments = comment_content_json['hcmts']
            for k in range(0, len(hot_comments)):
                hot_comment = hot_comments[k]  # 一条热评数据
                save_comment('hcmts',hot_comment,cur,movie_name)
                count = count + 1
        except:
            pass
        cur.close()
        conn.commit()
    print i,'--',page,'count=',count,'comment_num',comment_num


def Get_comment(url,conn):
    '''
    获取电影详情及评论url
    '''
    cur = conn.cursor()
    soup = Get_html(url)
    movie_name = soup.find('div', 'navbar-title').get_text().encode('utf-8')
    print movie_name
    document = '../../data/maoyan_data/' + movie_name + '.txt'
    movie_ename = soup.find('div', 'movie-ename text-ellipsis').get_text().encode('utf-8')
    movie_score = soup.find('div', 'movie-score')
    # 上映与点映的评分类型不同
    split_score = movie_score.find('div', 'split-score-content')
    if split_score is not None:
        # 用户评分
        left_score = split_score.find('div', 'left-score')
        user_score_name = left_score.find('span', 'score-name').get_text()
        user_score_val = left_score.find('span', 'score-val').get_text().encode('utf-8')
        user_score_num = (left_score.find('span', 'score-num')
                          ).find_all('span')[1].get_text().encode('utf-8')

        # 专业评分
        profession_score_url = split_score.find('a', 'link').get('href')
        right_score = split_score.find('div', 'right-score')
        profession_score_name = right_score.find(
            'span', 'score-name').find('span').get_text()
        profession_score_val = right_score.find('span', 'score-val').get_text().encode('utf-8')
        profession_score_num = (right_score.find(
            'span', 'score-num')).find_all('span')[1].get_text().encode('utf-8')
    else:#None 为空
        user_score_val ='None'
        user_score_num = 'None'
        profession_score_val = 'None'
        profession_score_num = 'None'

    noreleased_score = movie_score.find('div', 'noreleased-score')
    if noreleased_score is not None:
        # 点映评分
        noreleased_score_name = noreleased_score.find_all('span')[0]
        if noreleased_score_name is not None:
            noreleased_score_name = noreleased_score_name.get_text()
            noreleased_score_val = noreleased_score.find(
                'span', 'score').get_text().encode('utf-8')
            noreleased_score_num = noreleased_score.find(
                'div', 'score-num').find_all('span')[1].get_text().encode('utf-8')
        else:
            noreleased_score_val = 'None'
            noreleased_score_num ='None'
        wish_num = noreleased_score.find(
            'div', 'wish-num').find_all('span')[0].get_text().encode('utf-8')  # 想看人数
    else:
        noreleased_score_val = 'None'
        noreleased_score_num = 'None'
        wish_num = 'None'
        pass
    movie_category = soup.find(
        'div', 'movie-category').find('span', 'movie-cat')  # 电影类别
     # 电影标签 IMAX
    moive_tag = movie_category.find('div', 'movie-tag')
    if moive_tag is not None:
        union_tag = movie_tag.find('div', 'union-tag')
        tag_d = union_tag.find('span', 'tag-d').get_text().encode('utf-8')
        tag_imax = union_tag.find('span', 'tag-imax').get_text().encode('utf-8')
    else:
        tag_d = 'None';tag_imax='None'
    movie_content_row = soup.find_all('div', 'movie-content-row')
    movie_country = movie_content_row[0].find_all('span')[0].get_text().encode('utf-8')
    movie_time = movie_content_row[0].find_all(
        'span')[2].find_all('span')[0].get_text().encode('utf-8')
    movie_release_time = movie_content_row[1].get_text().encode('utf-8')
    movie_description = soup.find(
        'div', 'text-expander-content').find('p').get_text().encode('utf-8')
    movie_celebrities = soup.find('ul', 'movie-celebrities').find_all('li')
    for j in range(0, len(movie_celebrities)):  # 演职员表
        movie_celebrities_roles = movie_celebrities[
            j].find('span', 'movie-celebrities-roles').get_text().encode('utf-8')
        movie_celebrities_name = movie_celebrities[j].find_all('span')[
            0].get_text().encode('utf-8')
        movie_celebrities_url = 'http://m.maoyan.com'+movie_celebrities[
            j].find('a', 'link').get('href').encode('utf-8')
        #存入演职员表
        insert_celebrities_str = 'insert into celebrities values("'+movie_name +'","'+\
            movie_celebrities_roles+'","'+movie_celebrities_name+'","'+movie_celebrities_url+'")'
        #print insert_celebrities_str
        cur.execute(insert_celebrities_str)

    section_panel = soup.find('section', 'panel ')  # panel后面竟然有个空格
    if section_panel is not None:
        movie_panel = section_panel.find('div', 'panel-content')  # 票房数据
        movie_box = movie_panel.find('div', 'movie-box hasLink')  # 大陆上映票房
        if movie_box is None:
            movie_box = movie_panel.find('div', 'movie-box')  # 未上映票房
        movie_panel_Cell = movie_box.find_all('div', 'cell')
        for k in range(0, len(movie_panel_Cell)):
            panel_cell_desc = movie_panel_Cell[k].find('p', 'desc').get_text().encode('utf-8')
            panel_cell_num = movie_panel_Cell[k].find('p', 'num').get_text().encode('utf-8')
            #存入票房表
            insert_box_str = "insert into box values('"+movie_name+"','"+panel_cell_desc+\
                "','"+panel_cell_num+"')"
            cur.execute(insert_box_str)

    movie_comment_url = soup.find(
        'a', 'link link-more comments-link').get('href')
    movie_comment_url = 'http://m.maoyan.com' + movie_comment_url
    movie_comment_num = soup.find(
        'a', 'link link-more comments-link').find_all('span')[1].get_text()
    movie_comment_num = int(movie_comment_num)
    movie_id = re.search(r'(?<=movie/).*?(?=/comments)', movie_comment_url).group()
    #存入数据库表movies
    intsert_movies_str="insert into movies values('" +movie_name +"','"+movie_ename +"','"\
        +url+"','"+movie_id+"','"+str(movie_comment_num) +"','"+movie_comment_url+"','"+user_score_val+\
        "','"+user_score_num+"','"+profession_score_val+"','"+profession_score_num+"','"+noreleased_score_val\
        +"','"+noreleased_score_num +"','"+wish_num+"','"+tag_d+"','"+tag_imax+"','"+movie_country+"','"+movie_time+\
        "','" +movie_release_time+"','"+movie_description+"')"
    cur.execute(intsert_movies_str)
    cur.close()
    conn.commit()
    # print movie_comment_url, movie_comment_num
    Get_movie_comment_content(movie_comment_url, movie_comment_num,conn,movie_name)


def GetMoive(conn):
    '''
    获取电影列表
    '''
    moive_url = 'http://m.maoyan.com/'
    request = urllib2.Request(moive_url)
    response = urllib2.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html, 'lxml')
    movie_item = soup.find_all('li', 'item')
    for i in range(0, len(movie_item)):
        get_url = movie_item[i].find_all('a')[0].get('href')
        moive_url = 'http://m.maoyan.com' + get_url
        movie_title = movie_item[i].find('span', 'movie-name').get_text()
        # print movie_title, '-->', moive_url
        Get_comment(moive_url,conn)


def main():
    '''
    主函数
    '''
    conn = MySQLdb.connect(
        host='localhost',
        port = 3306,
        user='root',
        passwd='mjy123456',
        db='maoyan',
        )
    GetMoive(conn)
    conn.close()


if __name__ == '__main__':
    main()
