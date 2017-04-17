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


def save_comment(comment):
    '''
    评论与热评的json格式一样
    '''
    approve = comment['approve']
    approved = comment['approved']
    try:
        authInfo = comment['authInfo']
    except:
        pass
    avatarurl = comment['avatarurl']
    try:
        cityName = comment['cityName']
    except:
        pass
    content = comment['content']
    filmView = comment['filmView']
    comment_id = comment['id']
    isMajor = comment['isMajor']
    juryLevel = comment['juryLevel']
    movieId = comment['movieId']
    nick = comment['nick']
    nickName = comment['nickName']
    print nickName
    oppose = comment['oppose']
    pro = comment['pro']
    reply = comment['reply']
    score = comment['score']
    spoiler = comment['spoiler']
    startTime = comment['startTime']
    supportComment = comment['supportComment']
    supportLike = comment['supportLike']
    sureViewed = comment['sureViewed']
    created_time = comment['time']
    userId = comment['userId']
    userLevel = comment['userLevel']
    try:
        vipInfo = comment['vipInfo']
    except:
        pass
    vipType = comment['vipType']
    try:
        tag_list = comment['tagList']
        fixed = tag_list['fixed']
        for i in range(0, len(fixed)):
            fid = fixed[i]['id']
            fname = fixed[i]['name']
    except:
        pass


def Get_movie_comment_content(comment_url, comment_num):
    '''
    获取评论
    '''
    comment_soup = Get_html(comment_url)
    navbar_title = comment_soup.find('div', 'navbar-title').get_text()
    page = comment_num / 15  # offset 页偏移是15
    movie_id = re.search(r'(?<=movie/).*?(?=/comments)', comment_url).group()
    for i in range(0, page):
        req_url = 'http://m.maoyan.com/mmdb/comments/movie/' + \
            movie_id + '.json?_v_=yes&offset=' + str(i * 15)
        comment_content_json = Get_json(req_url)
        comments = comment_content_json['cmts']
        for j in range(0, len(comments)):
            comment = comments[j]  # 一条评论数据
            save_comment(comment)
        hot_comments = comment_content_json['hcmts']
        for k in range(0, len(hot_comments)):
            hot_comment = hot_comments[k]  # 一条热评数据
            save_comment(hot_comment)


def Get_comment(url):
    '''
    获取电影详情及评论url
    '''
    soup = Get_html(url)
    movie_name = soup.find('div', 'navbar-title').get_text()
    print movie_name
    document = '../../data/maoyan_data/' + movie_name + '.txt'
    movie_ename = soup.find('div', 'movie-ename text-ellipsis').get_text()
    movie_score = soup.find('div', 'movie-score')
    # 上映与点映的评分类型不同
    try:
        split_score = movie_score.find('div', 'split-score-content')
        # 用户评分
        left_score = split_score.find('div', 'left-score')
        user_score_name = left_score.find('span', 'score-name').get_text()
        user_score_val = left_score.find('span', 'score-val').get_text()
        user_score_num = (left_score.find('span', 'score-num')
                          ).find_all('span')[1].get_text()

        # 专业评分
        profession_score_url = split_score.find('a', 'link').get('href')
        right_score = split_score.find('div', 'right-score')
        profession_score_name = right_score.find(
            'span', 'score-name').find('span').get_text()
        profession_score_val = right_score.find('span', 'score-val').get_text()
        profession_score_num = (right_score.find(
            'span', 'score-num')).find_all('span')[1].get_text()
    except:
        pass

    try:

        noreleased_score = movie_score.find('div', 'noreleased-score')
        try:  # 点映评分
            noreleased_score_name = noreleased_score.find_all('span')[
                0].get_text()
            noreleased_score_val = noreleased_score.find(
                'span', 'score').get_text()
            noreleased_score_num = noreleased_score.find(
                'div', 'score-num').find_all('span')[1].get_text()
        except:
            pass
        wish_num = noreleased_score.find(
            'div', 'wish-num').find_all('span')[0].get_text()  # 想看人数
    except:
        pass
    movie_category = soup.find(
        'div', 'movie-category').find('span', 'movie-cat').get_text()  # 电影类别
    try:  # 电影标签 IMAX
        moive_tag = movie_category.find('div', 'movie-tag')
        union_tag = movie - tag.find('div', 'union-tag')
        tag_d = union_tag.find('span', 'tag-d').get_text()
        tag_imax = union_tag.find('span', 'tag-imax').get_text()
    except:
        pass
    movie_content_row = soup.find_all('div', 'movie-content-row')
    movie_country = movie_content_row[0].find_all('span')[0].get_text()
    movie_time = movie_content_row[0].find_all(
        'span')[2].find_all('span')[0].get_text()
    movie_release_time = movie_content_row[1].get_text()
    movie_description = soup.find(
        'div', 'text-expander-content').find('p').get_text()
    movie_celebrities = soup.find('ul', 'movie-celebrities').find_all('li')
    for j in range(0, len(movie_celebrities)):  # 演职员表
        movie_celebrities_roles = movie_celebrities[
            j].find('span', 'movie-celebrities-roles').get_text()
        movie_celebrities_name = movie_celebrities[j].find_all('span')[
            0].get_text()
        movie_celebrities_url = movie_celebrities[
            j].find('a', 'link').get('href')
    section_panel = soup.find('section', 'panel ')  # panel后面竟然有个空格
    movie_panel = section_panel.find('div', 'panel-content')  # 票房数据
    movie_box = movie_panel.find('div', 'movie-box hasLink')  # 大陆上映票房
    if movie_box is None:
        movie_box = movie_panel.find('div', 'movie-box')  # 未上映票房
    movie_panel_Cell = movie_box.find_all('div', 'cell')
    for k in range(0, len(movie_panel_Cell)):
        panel_cell_desc = movie_panel_Cell[k].find('p', 'desc').get_text()
        panel_cell_num = movie_panel_Cell[k].find('p', 'num').get_text()
    movie_comment_url = soup.find(
        'a', 'link link-more comments-link').get('href')
    movie_comment_url = 'http://m.maoyan.com' + movie_comment_url
    movie_comment_num = soup.find(
        'a', 'link link-more comments-link').find_all('span')[1].get_text()
    movie_comment_num = int(movie_comment_num)
    # print movie_comment_url, movie_comment_num
    Get_movie_comment_content(movie_comment_url, movie_comment_num)


def GetMoive():
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
            Get_comment(moive_url)


def main():
    '''
    主函数
    '''
    GetMoive()


if __name__ == '__main__':
    main()
