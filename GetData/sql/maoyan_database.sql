
#--猫眼电影数据库构建命令

#--在爬虫中只针对数据库操作，不参与构建，选择使用命令构建数据库及表

create database maoyan character set utf8;
use maoyan;

#电影表
create table movies(
	name varchar(50),
	ename varchar(50),
	url text,
	movieId int,
	comment_num int,
	comments_url text,
	user_score_val varchar(4),
	user_score_num varchar(10),
	profession_score_val varchar(4),
	profession_score_num varchar(10),
	noreleased_score_val varchar(4),
	noreleased_score_num varchar(10),
	wish_num varchar(10),
	tag_d varchar(4),
	tag_imax varchar(10),
	country varchar(50),
	movie_time varchar(40),
	movie_release_time varchar(40),
	movie_desc text
	);

#评论表
create table comments(
	moviename varchar(50),
	comments_type varchar(5),
	approve int,
	approved varchar(5),
	authInfo text,
	avatarurl text,
	cityName varchar(50),
	content text,
	filmView varchar(5),
	comment_id varchar(9),
	isMajor varchar(5),
	juryLevel int,
	movieId int,
	nick varchar(50),
	nickNmae varchar(50),
	oppose int,
	pro varchar(5),
	reply int,
	score FLOAT(2,1),
	spoliler int,
	start_time varchar(40),
	supportComment varchar(5),
	supportLike varchar(5),
	sureViewd int,
	stime varchar(40),
	userId int,
	userLevel int,
	vipInfo text,
	vipType int
	);

#演职员表
create table celebrities(
	moviename varchar(50),
	celebrities_roles text,
	celebrities_name  varchar(50),
	celebrities_url text
	);

#票房表
create table box(
	moviename varchar(50),
	cell_desc varchar(50),
	cell_num varchar(20));