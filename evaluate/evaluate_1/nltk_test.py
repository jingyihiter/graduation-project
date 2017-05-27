import nltk
import sqlite3
import jieba
import re


import jnius_config
jnius_config.add_options('-Xrs', '-Xmx1024m')
jnius_config.set_classpath('.', 'C:\Program Files\java\jdk1.8.0_111\lib\*')
from jnius import autoclass

searchClass = autoclass("jingyi.SearcherMovies")
answerClass = searchClass()  # init

def Calculat_Score(weibo,comment,sim):
	'''
	检索微博，计算答案与微博对应的评论之间的bleu值
	'''
	try:
		answer = answerClass.SearchAnswer(comment,sim)
		bleuscore = GetBleuScore(StringToList(answer),StringToList(weibo))
	except:
		answer=''
		bleuscore=0
	return answer,bleuscore

def StringToList(st):
	'''
	字符串转换成列表
	'''
	n =len(st)
	st_list=[]
	for i in range(0,n):
		st_list.append(st[i])
	'''
	sd = jieba.cut(st)
	st_list = ("/".join(st)).split('/')
	'''
	return st_list

def GetBleuScore(hypo,refer):
	'''
	计算bleu值
	'''
	bleuscore= nltk.translate.bleu_score.sentence_bleu([refer],hypo)
	#print(bleuscore)
	return bleuscore
	#print(BLEUscore)

def commentsOrderByBleuscore(comments,content,filecount,bleu,sim,document):
	'''
	'''
	n =len(comments)
	if(n<1):
		return
	comments_bleu =[]
	for comment in comments: #计算bleu值
		tem=[]
		comment_content = re.sub(r'回复@.*:|@.* ','',comment[0])
		tem.append(comment_content)
		tem.append(GetBleuScore(StringToList(comment_content),StringToList(content)))
		comments_bleu.append(tem)
	for i in range(0,n): #排序
		for j in range(n-1,i,-1):
			if(comments_bleu[j][1] > comments_bleu[j-1][1]):
				tem = comments_bleu[j]
				comments_bleu[j]=comments_bleu[j-1]
				comments_bleu[j-1]=tem
	if(comments_bleu[0][1]<bleu): #如果bleu值最大的比0.01小
		#filecount[2]+=1
		return
	file_=open("bleu/"+document+"2/"+str(filecount[0])+".txt",'w',encoding='utf-8')
	#print(type(content))
	file_.write(content+'\n')
	#for i in range(0,n):
	file_.write(comments_bleu[0][0]+" \t"+str(comments_bleu[0][1])+'\n')
	evalu = Calculat_Score(content.replace('[','').replace(']',''),comments_bleu[0][0],sim)
	file_.write(evalu[0]+'\t'+str(evalu[1])) #评测的结果 bleu值
	file_.close()
	filecount[0]+=1
	if evalu[1]>=bleu:
		filecount[1]+=1

def main1(bleu,sim,document):
	'''
	主函数
	'''
	conn = sqlite3.connect("weibo.db")
	cur= conn.cursor()
	cur.execute("select content,blogid from weiblog where comments_count > 0")
	weiblogs = cur.fetchall()
	filecount=[]
	filecount.append(0) #文件数
	filecount.append(0) #达标数
	filecount.append(0) #阈值上的总数
	for i in range(0,len(weiblogs)): #先取前100
		weibo = weiblogs[i]
		cur.execute("select content from weicomment where blogid='"+weibo[1]+"'")
		comments = cur.fetchall()
		commentsOrderByBleuscore(comments,weibo[0],filecount,bleu,sim,document)
	#print(bleu,str(filecount[0]),str(filecount[1]),str(filecount[2]))
	print(document, "pre "+str(float(filecount[1])/filecount[0]))

def main():
	bleulist=[0.01,0.1,0.2,0.3,0.4,0.5,0.6]
	document=['BM25/','BOOL/','VSM/','Dirichlet/','JelinekMercer/']
	for i in range(0,5):
		main1(0.4,i,document[i])
	#for bl in bleulist:
	#	main1(bl)

if __name__=='__main__':
	main()