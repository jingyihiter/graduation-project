import pylab as plt
plt.figure(figsize=(6,6))

x = [0.01,0.1,0.2,0.3,0.4,0.5,0.6]
BM25_comment=[0.655394524959742,0.646302250803858,0.6,0.509090909090909,0.416666666666666,0.275,0]
BM25_weibo=[0.835748792270531,0.77491961414791,0.686486486486486,0.6,0.486111111111111,0.375,0.166666666666666]
plt.plot(x,BM25_weibo,label=u"BM25_weibo")
plt.plot(x,BM25_comment,label=u"BM25_comment")
plt.legend()
plt.xlim(0.0,0.7)
plt.ylim(0.0,1.0)
plt.xlabel("bleu threshold")
plt.ylabel("precesioin rate")
plt.title(u"BM25 between weibo and comment")
plt.show()