# -*- encoding:utf-8 -*-
import sqlite3
import os
conn = sqlite3.connect('douban.db')
cur = conn.cursor()
main_document = 'train/douban/'

# 好于 better_than
cur.execute("select * from better_than")
movies_better = cur.fetchall()
better_count = 0
for i in range(0, len(movies_better)):
    bettte_file = open(main_document + 'better/' +
                       str(better_count) + '.txt', 'w')
    better_count += 1
    bettte_file.write(movies_better[i][0].encode(
        'utf-8') + "好于" + movies_better[i][1].encode('utf-8') + "\n")
    bettte_file.close()

# 豆瓣评分及评分人数
cur.execute("select movie_name,score,score_num from score_box")
movies_box = cur.fetchall()
score_count = 0
for j in range(0, len(movies_box)):
    scorebox_file = open(main_document + 'score/' + str(score_count)+'.txt', 'w')
    score_count += 1
    scorebox_file.write(movies_box[j][0].encode(
        'utf-8') + "#豆瓣评分" + str(movies_box[j][1]) + "分#" + str(movies_box[j][2]) + "人评" + '\n')
    scorebox_file.close()

# 电影信息
cur.execute("select * from movies")
movies_info = cur.fetchall()
movies_ls = []
movie_count = 0
for k in range(0, len(movies_info)):
    movies_info_file = open(main_document + 'movie/' +
                            str(movie_count) + '.txt', 'w')
    movie_count += 1
    movieinfo = movies_info[k]
    movies_ls.append(movieinfo[0])  # 电影列表
    movies_info_file.write(movieinfo[0].encode('utf-8') + "#别名" + movieinfo[17].encode('utf-8') + "#年份" + movieinfo[1].encode('utf-8') + "#上映日期" + movieinfo[15].encode('utf-8')
                           + "#时长" + movieinfo[16].encode('utf-8') + "#导演" + movieinfo[9].encode('utf-8') + "#编剧" + movieinfo[8].encode('utf-8') + "#演员" + movieinfo[10].encode('utf-8') + "#简介" + movieinfo[-1].strip(' ').strip('\n').encode('utf-8'))
    movies_info_file.write("\n")
    movies_info_file.close()
# 影评信息
commentdir = main_document + 'comment/'
try:
    os.mkdir(commentdir)
except:
    pass

# 长影评的数据需要进一步的处理
file_count = 0
for l in range(0, len(movies_ls)):
    filmname = movies_ls[l]
    print filmname.encode('utf-8')
    # comment_file = open(commentdir+str(filmname.encode('gbk'))+".txt",'w')
    cur.execute(
        "select comment_content from comments where movie_name ='" + filmname + "'")
    comments = cur.fetchall()
    for m in range(0, len(comments)):
        comment_file = open(commentdir + str(file_count) + ".txt", 'w')
        file_count += 1
        comment_file.write(comments[m][0].encode('utf-8') + '\n')
        comment_file.close()

cur.close()
conn.close()
