


create database weibo character set utf8;

use weibo;

create table movies(
	movie_name varchar(100),
	nick_name varchar(100),
	rating varchar(50),
	score float(2,1),
	total_count varchar(10),
	movieUrl text,
	detailUrl text,
	shortcommenturl text,
	huatiUrl text,
	movieID varchar(30)
);


create table movies_detail(
	movie_name varchar(100),
	en_name varchar(100),
	nick_name varchar(100),
	director varchar(40),
	writescreen varchar(40),
	actors text,
	movie_type text,
	country varchar(40),
	release_time text,
	time_long varchar(30),
	description text
	);

create table weiblog(
	movie_name varchar(100),
	blog_type varchar(20),
	blog_url text,
	itemID varchar(50),
	create_time varchar(50),
	content text,
	reposts_count int,
	comments_count int,
	attitudes_count int,
	cradid varchar(30),
	blogid varchar(50),
	source varchar(50),
	favorited varchar(10),
	rating varchar(50),
	textLength varchar(20),
	isLongText varchar(10),
	rid varchar(50),
	attitudes_status int,
	bid varchar(20),

	userid varchar(12),
	username varchar(100),
	userurl text,
	statuse_count int,
	vertified varchar(5),
	vertified_type int,
	userdescription text,
	gender varchar(5),
	mbtype int,
	urank int,
	mbrank int,
	followes_count int,
	follow_count int
	);

create table weicomment(
	blogid varchar(50),
	comment_id varchar(30),
	create_at varchar(50),
	source varchar(30),
	content text,
	like_counts int,
	liked varchar(5),
	userid varchar(12),
	username varchar(100),
	userurl text,
	vertified varchar(5),
	vertified_type int,
	mbtype int
	);