#import matplotlib.pyplot as plt 
import pylab as plt
plt.figure(figsize=(6,6))

x = [0.01,0.1,0.2,0.3,0.4,0.5,0.6]
BM25_y=[0.835748792270531,0.77491961414791,0.686486486486486,0.6,0.486111111111111,0.375,0.166666666666666]
Bool_y=[0.867954911433172,0.47588424437299,0.367567567567567,0.309090909090909,0.194444444444444,0.15,0.166666666666666]
Dirichlet_y=[0.835748792270531,0.604501607717041,0.459459459459459,0.345454545454545,0.25,0.15,0.166666666666666]
JelinekMercer_y=[0.632850241545893,0.598070739549839,0.513513513513513,0.445454545454545,0.333333333333333,0.25,0.166666666666666]
plt.plot(x,BM25_y,label=u"BM25")
plt.plot(x,Bool_y,label=u"Bool")
plt.plot(x,Dirichlet_y,label=u"Dirichlet")
plt.plot(x,JelinekMercer_y,label=u"JelinekMercer")
plt.legend()
plt.xlim(0.0,0.7)
plt.ylim(0.0,1.0)
plt.xlabel("bleu threshold")
plt.ylabel("precesioin rate")
plt.title(u"Retrieval Models comparison in searching weibo")
plt.show()
