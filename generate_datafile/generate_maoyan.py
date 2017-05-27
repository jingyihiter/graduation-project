# -*- encoding:utf-8 -*
import sqlite3

conn = sqlite3.connect('maoyan.db')
cur = conn.cursor()
main_document = 'train/maoyan/'

# 电影信息
cur.execute("select * from movies")
movies = cur.fetchall()
moviesls = []
movie_count = 0
for i in range(0, len(movies)):
    movie = movies[i]
    moviesls.append(movie[0])
    movie_file = open(main_document + 'movie/' +
                      str(movie_count) + '.txt', 'w')
    movie_count += 1
    movie_file.write(movie[0].encode('utf-8') + '#' + movie[1].encode('utf-8') + "#用户评分" + movie[6].encode('utf-8') + "#专业评分" + movie[8].encode('utf-8') +
                     "#国家" + movie[-4].encode('utf-8') + "#时长" + movie[-3].encode('utf-8') + "#上映日期" + movie[-2].encode('utf-8') + "#简介" + movie[-1].encode('utf-8') + '\n')
    movie_file.close()

# 票房信息
cur.execute("select * from box")
moviebox = cur.fetchall()
box_count = 0
for j in range(0, len(moviebox)):
    box_file = open(main_document + 'box/' + str(box_count) + '.txt', 'w')
    box_count += 1
    item = moviebox[j]
    box_file.write(item[0].encode('utf-8') +
                   item[1].encode('utf-8') + item[2].encode('utf-8') + '\n')
    box_file.close()

# 演员信息
cur.execute("select * from celebrities")
actors = cur.fetchall()
actor_count = 0
for k in range(0, len(actors)):
    actor = actors[k]
    actors_file = open(main_document + 'actor/' +
                       str(actor_count) + '.txt', 'w')
    actor_count += 1
    actors_file.write(actor[0].encode(
        'utf-8') + '中' + actor[2].encode('utf-8') + "演" + actor[1].encode('utf-8') + '\n')
    actors_file.close()

# 影评信息
commentdir = main_document + 'comment/'
file_count = 0
for l in range(0, len(moviesls)):
    filmname = moviesls[l]
    print filmname.encode('utf-8')
    cur.execute(
        "select content from comments where moviename='" + filmname + "'")
    comments = cur.fetchall()
    # comments_file = open(commentdir+str(filmname.encode('gbk'))+'.txt','w')
    for m in range(0, len(comments)):
        comments_file = open(commentdir + str(file_count) + ".txt", 'w')
        file_count += 1
        comments_file.write(comments[m][0].encode('utf-8') + '\n')
        comments_file.close()

cur.close()
conn.close()
