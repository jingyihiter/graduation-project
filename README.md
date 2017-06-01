# graduation-project
my undergraduation project-weichat-robot in movies
------------------------------------------------

第一部分：[数据获取](https://github.com/jingyihiter/graduation-project/tree/master/GetData)
========

一、[豆瓣影评数据爬取](https://github.com/jingyihiter/graduation-project/blob/master/GetData/douban.py)
>1、模拟登录<br>
>2、影评信息爬取<br>
>3、存数到sqlite3数据库中


二、[微博电影影评数据爬取](https://github.com/jingyihiter/graduation-project/blob/master/GetData/weibo.py)
>1、模拟登录手机端m.weibo.cn<br>
>2、获取影评信息<br>
>3、钓鱼功能<br>
>4、存储到sqlite3数据库中


三、[猫眼电影影评数据抓取](https://github.com/jingyihiter/graduation-project/blob/master/GetData/maoyan.py)
>1、获取手机端m.maoyan.com的影评数据<br>
>2、存储到mysql数据库中，并备份成sql文件<br>
>3、存储到sqlite3数据库中


四、[现有数据](https://github.com/jingyihiter/graduation-project/tree/master/GetData/sqlite3_data)
>1、时间 2017.4.30 <br>
>2、数目 微博24058条 豆瓣21012条 猫眼11854条<br>
>3、时间 2017.5.8  微博评论8万条,作为检索数据源<br>
>4、评价数据源 2017.5.24 新爬取的微博数据2700条微博<br>


第二部分：[检索系统构建](https://github.com/jingyihiter/graduation-project/tree/master/SearchModel/movieRobot)
===============
Lucene 检索工具
>1、构建索引<br>
>2、检索结果<br>



第三部分：[微信机器人设计](https://github.com/jingyihiter/graduation-project/tree/master/wxpy)
====================
>wxpy应用


第四部分：[检索模型的评价](https://github.com/jingyihiter/graduation-project/tree/master/evaluate)
========================
检索模型<br>
>1、BM25算法<br>
>2、布尔模型<br>
>3、Dirichlet语言模型<br>
>4、JelinekMercer语言模型<br>

评价数据源<br>
>1、采用新爬取的数据源作为评价数据<br>
>2、将原始数据去重后分为5类，取其中一类作为评价数据<br>

评价方法<br>
>1、bleu值 <br>
>2、检索微博计算评论相关的bleu值
>3、检索评论计算微博相关的bleu值



[文档部分](https://github.com/jingyihiter/graduation-project/tree/master/document)
=======
>1、开题报告<br>
>2、开题答辩ppt<br>
>3、论文大纲<br>
>4、中期报告<br>
>5、中期答辩ppt<br>
>6、过程管理<br>
>7、周报内容<br>