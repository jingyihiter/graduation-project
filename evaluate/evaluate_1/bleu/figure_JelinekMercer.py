import pylab as plt
plt.figure(figsize=(6,6))

x = [0.01,0.1,0.2,0.3,0.4,0.5,0.6]
JelinekMercer_comment=[0.505636070853462,0.466237942122186,0.459459459459459,0.409090909090909,0.347222222222222,0.175,0]
JelinekMercer_weibo=[0.632850241545893,0.598070739549839,0.513513513513513,0.445454545454545,0.333333333333333,0.25,0.166666666666666]
plt.plot(x,JelinekMercer_weibo,label=u"JelinekMercer_weibo")
plt.plot(x,JelinekMercer_comment,label=u"JelinekMercer_comment")
plt.legend()
plt.xlim(0.0,0.7)
plt.ylim(0.0,1.0)
plt.xlabel("bleu threshold")
plt.ylabel("precesioin rate")
plt.title(u"JelinekMercer Model between weibo and comment")
plt.show()