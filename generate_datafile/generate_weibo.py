# -*- encoding:utf-8 -*-

import sqlite3
import re
import os
conn = sqlite3.connect("weibo.db")
cur = conn.cursor()
main_document = 'train/weibo/'

# 电影信息
cur.execute("select movie_name,nick_name,score from movies")
movies = cur.fetchall()
moviesls = []
score_count = 0
for i in range(0, len(movies)):
    moive = movies[i]
    moviesls.append(moive[0])
    score_file = open(main_document + 'score/' +
                      str(score_count) + '.txt', 'w')
    score_count += 1
    score_file.write(moive[0].encode('utf-8') + "#别名" +
                     moive[1].encode('utf-8') + "#微博评分" + str(moive[2]) + "\n")
    score_file.close()


# 详细信息
cur.execute("select * from movies_detail")
moviedetail = cur.fetchall()
movie_count = 0
for j in range(0, len(moviedetail)):
    detail_file = open(main_document + 'movie/' +
                       str(movie_count) + '.txt', 'w')
    movie_count += 1
    detail = moviedetail[j]
    detail_file.write(detail[0].encode('utf-8') + "#英文名" + detail[1].encode('utf-8') + "#别名" + detail[2].encode('utf-8') + "#导演" + detail[3].encode('utf-8')
                      + "#编剧" + detail[4].encode('utf-8') + "#演员" + detail[5].encode('utf-8') + "#类型" + detail[
        6].encode('utf-8') + "#国家" + detail[7].encode('utf-8') + "#上映日期"
        + detail[8].encode('utf-8') + "#时长" + detail[9].encode('utf-8') + "#简介" + detail[10].encode('utf-8'))
    detail_file.close()

# 微博内容
weiblogdir = main_document + 'weiblog/'
try:
    os.mkdir(weiblogdir)
except:
    pass
file_count = 0
for w in range(0, len(moviesls)):
    filmname = moviesls[w]
    print filmname.encode("utf-8")
    cur.execute(
        "select content,blogid from weiblog where movie_name='" + filmname + "'")
    weiblogs = cur.fetchall()
    # blog_file = open(weiblogdir+str(filmname.encode('gbk'))+'.txt','w')
    for k in range(0, len(weiblogs)):
        blog_file = open(weiblogdir + str(file_count) + ".txt", 'w')
        file_count += 1
        blog_file.write(weiblogs[k][0].encode('utf-8') + '\n')
        blog_file.close()
        cur.execute(
            "select content from weicomment where blogid='" + weiblogs[k][1] + "'")
        blog_comments = cur.fetchall()
        for a in range(0, len(blog_comments)):
            pattern = r'回复@.*?:'  # 去除评论之间的互相@
            blog_comment = re.sub(pattern, '', blog_comments[a][0])
            if len(blog_comment) <= 0:
                continue
            else:
                pass
            comment_file = open(weiblogdir + str(file_count) + ".txt", 'w')
            file_count += 1
            comment_file.write(blog_comment.encode('utf-8') + '\n')
            comment_file.close()
cur.close()
conn.close()
