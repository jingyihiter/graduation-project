# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 15:55:09 2017

@author: 马晶义
"""
from wxpy import *
import random
import time
import re
import sqlite3
import jnius_config
jnius_config.add_options('-Xrs', '-Xmx1024m')
jnius_config.set_classpath('.', 'C:\Program Files\java\jdk1.8.0_111\lib\*')
from jnius import autoclass


bot = Bot(cache_path=True)
myself = bot.self
bot.enable_puid(path='wxpy_puid.pkl')  # 设置puid
Max_members = 10  # 设置群成员上限
searchClass = autoclass("jingyi.SearcherMovies")
answerClass = searchClass()  # init

groups_name = ['电影讨论1群', '电影讨论2群', '电影讨论3群']#, '我搞测试请忽略']  # 实验的群名
film_groups = []  # 设置group类
for group_name in groups_name:
    print(group_name)
    group = ensure_one(bot.groups().search(group_name))
    film_groups.append(group)


def can_answer(msg):
    '''
    能回答则返回回答的txt
    否则返回None
    '''
    answer = answerClass.SearchAnswer(msg, 0)
    if answer != "":
        return answer
    else:
        return None


admin_name='律己'

conn = sqlite3.connect('question.db', check_same_thread=False)
cur = conn.cursor()
questionID = 0  # 问题编号

times = 0

while True:

    '''
    初始时在群里邀请好友聊天
    '''
    if times == -1:
        for name in groups_name:
            group = bot.groups().search(name)[0]
            group.send('你好，我是小影!一起聊天吧！')
            group.send('本机器人拒绝调戏！使用说明参照:http://suo.im/2tmD5Q')

    '''
	自动同意加好友请求
	'''
    @bot.register(msg_types=FRIENDS)
    def auto_accept_friends(msg):
        #new_friend = msg.card.accept()
        new_friend = bot.accept_friend(msg.card)
        new_friend.send('我是小影机器人，我们来聊天吧！')
        new_friend.send('欢迎入群讨论热映电影啦！请回复：我要加群')
        bot.friends(update=True)
        print(new_friend.puid)
        global updatefriend
        updatefriend = 1
        return
    '''
	添加用户为好友，用户对象\用户名\用户的微信ID
	'''
    # userlist=['mjy_1995','马仁锋']
    # for user in userlist:
    #	bot.add_friend(user,'你好，我是小影！')

    '''
	自动建群
	'''
    if times == -1:  # 建群触发
        users = []
        lvj = ensure_one(bot.friends().search('律己'))  # 测试样例
        users.append(lvj)
        new_group_name = '建个群试试'
        group_test = bot.create_group(users, topic=new_group_name)
        bot.groups(update=True, contact_only=False)
        group_test.send('大家好，我是小影机器人！')
        print(group_test.nick_name)
        print(len(group_test))
        groups_name.append(group_test.nick_name)

    '''
	自动回复好友消息
	'''
    my_friends = bot.friends(update=True)
    for my_friend in my_friends:
        @bot.register(my_friends)
        def reply_my_friend(msg):
            receive_type = msg.type
            sender = msg.sender
            # 处理加群消息
            if '我要加群' == msg.text:
                for target_group in film_groups:
                    if sender in target_group:
                        sender.send('你已经加过了"{}"的群'.format(
                            target_group.nick_name))
                        break
                    if len(target_group) < Max_members:
                        target_group.add_members(sender)
                        sender.send('你已成功加入“{}”的群，快和大家一起聊天吧！'.format(
                            target_group.nick_name))
                        target_group.send(
                            '欢迎@{}入群交流[调皮],请遵守本群规则:http://suo.im/2tmD5Q'.format(sender.nick_name))
                        break  # 加入一个群就可以了
                return
            # 这里处理其他消息
            # print(msg)

            if receive_type == 'Picture':  # 发表情包
                emj = random.randint(0, 21)
                document = 'emoj/' + str(emj) + '.jpg'
                sender.send_image(document)
                return
            elif receive_type == 'Recording':
                return '我听不见你说的是什么[捂脸]'
            else:
                # 处理用户的文本消息，如回答用户的问题
                if '你已添加了' in msg.text and '现在可以开始聊天了。' in msg.text:
                    return  # 添加好友的系统提示消息
                regix=re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9]')
                useful_text=regix.sub('',msg.text)
                if useful_text=='': #处理只发特殊符号的消息
                    return '这是什么鸟语，请讲人话'
                question_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9,.;!?|`，。、‘’；“”！·~！？]','',msg.text) #去除问题中的特殊符号
                friend_answer = can_answer(question_text)
                if friend_answer is not None:
                    return friend_answer
                else:
                    return '听不懂你在说什么，换个问题吧'  # 暂随机回答

    '''
	群消息处理
	'''
    @bot.register(Group, TEXT)
    def print_group_msg(msg):
        '''
        群内基本消息
        '''
        global questionID
        mygroup = msg.sender.nick_name
        group_meg_sender = msg.member
        msg_content = msg.text
        memname = msg.member.nick_name
        if '回答id:' in msg_content:  # 问题的回答
            get_questionid = re.search(r'(?<=回答id:)\d+', msg_content)
            if get_questionid is None:
                msg.sender.send('回答问题格式有误，请参照：http://suo.im/2tmD5Q')
            else:
                get_questionid = get_questionid.group()
                a_questionid = int(get_questionid)
                answer_content = msg_content.replace(
                    '回答id:' + get_questionid, '')  # 替换掉格式
                cur.execute('insert into answer values(?,?,?)',
                            (get_questionid, answer_content, memname))
                conn.commit()
                askers = cur.execute(
                    'select username,groupname from question where questionID ={}'.format(get_questionid))
                ask_user = askers.fetchall()[0]
                send_answer = ensure_one(bot.groups().search(ask_user[1]))
                send_answer.send(
                    '@' + ask_user[0] + ' ' + answer_content)  # 回答其他群里回答的答案

        if '@小影' in msg.text:  # 回复@小影的消息
            # print(mygroup)
            if mygroup in groups_name:  # 电影群里的用户问题，
                groupsend = msg.sender  # 群对象
                question_content = msg_content.replace('@小影', '').strip()
                regix=re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9]')
                useful_text=regix.sub('',question_content)
                if useful_text=='': #处理只发特殊符号的消息
                    groupsend.send('这是什么鸟语，请讲人话@{}'.format(memname))
                    return
                if question_content is None or len(question_content) <= 0:
                    groupsend.send('不要只找我不说话啊@{}'.format(memname))
                    return
                question_text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9,.;!?|`，。、‘’；“”！·~！？]','',question_content) #去除问题中的特殊符号
                answer = can_answer(question_text)
                if answer != None:
                    send_msg = answer + '@' + memname  # 消息加工
                    groupsend.send(send_msg)  # 发送到群
                else:
                    groupsend.send('请等待片刻，小影正在努力寻求答案@{}'.format(memname))
                    cur.execute('insert into question values(?,?,?,?)',
                                (questionID, question_content, memname, mygroup))  # 存问题到数据库
                    conn.commit()
                    for forward_group in film_groups:
                        if forward_group == groupsend:
                            continue
                        else:  # 转发消息
                            forward_msg = msg.text.replace(
                                '@小影', '问题id:{} '.format(questionID))
                            forward_group.send(forward_msg)
                    questionID = questionID + 1

        '''
		对举报消息进行删除被举报用户
		'''
        if '踢出@' in msg.text:  # 举报消息
            report_user_name = (re.search(r'(?<=踢出@).*', msg.text)).group()
            report_group = msg.sender
            report_user = bot.friends().search(report_user_name)
            if memname==admin_name:
                try:
                    if report_user!=[]:
                        report_user=report_user[0]
                    report_group.remove_members(
                        report_user)  # 移除群聊 群聊人数少时无法移除
                    report_group.send('已成功移除该成员，请大家遵守规则！')
                except Exception as err:
                    print(err)
                    report_group.send('群聊人数太少无法移除或举报用户不在本群中')
                report_num = 0

    # bot.join()
    time.sleep(3)
    times = times + 1
Bot.logout(myself)
