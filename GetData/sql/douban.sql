

#sqlite3 创建
#create database douban character set utf8;
#use douban;

create table movies(
	name varchar(100),
	year varchar(20),
	url text,
	long_com_url text,
	long_com_num int,
	short_com_url text,
	short_com_num int,
	question_url text,
	question_num int,
	director varchar(40),
	screenwrite varchar(40),
	actors text,
	movie_type text,
	country varchar(100),
	language varchar(30),
	release_time text,
	time_long varchar(30),
	nickname text,
	IMDBurl text,
	description text
	);

create table score_box(
	movie_name varchar(100),
	score float(2,1),
	score_num int,
	star5_percentge varchar(10),
	star4_percentge varchar(10),
	star3_percentge varchar(10),
	star2_percentge varchar(10),
	star1_percentge varchar(10)
	);

create table better_than(
	movie_name varchar(100),
	movie_better_than varchar(100)
	);

create table comments(
	movie_name varchar(100),
	comments_type varchar(10),
	username varchar(50),
	userurl text,
	useful varchar(100),
	useless varchar(100),
	givescore int,
	comment_time varchar(40),
	comment_title text,
	comment_content text,
	comment_url text
	);

#create table quesion(

#	)