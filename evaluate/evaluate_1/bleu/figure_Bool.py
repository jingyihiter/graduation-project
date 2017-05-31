import pylab as plt
plt.figure(figsize=(6,6))

x = [0.01,0.1,0.2,0.3,0.4,0.5,0.6]
Bool_comment=[0.74074074074074,0.398713826366559,0.335135135135135,0.3,0.222222222222222,0.125,0]
Bool_weibo=[0.867954911433172,0.47588424437299,0.367567567567567,0.309090909090909,0.194444444444444,0.15,0.166666666666666]
plt.plot(x,Bool_weibo,label=u"Bool_weibo")
plt.plot(x,Bool_comment,label=u"Bool_comment")
plt.legend()
plt.xlim(0.0,0.7)
plt.ylim(0.0,1.0)
plt.xlabel("bleu threshold")
plt.ylabel("precesioin rate")
plt.title(u"Bool Model between weibo and comment")
plt.show()