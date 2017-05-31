import pylab as plt
plt.figure(figsize=(6,6))

x = [0.01,0.1,0.2,0.3,0.4,0.5,0.6]
Dirichlet_comment=[0.684380032206119,0.495176848874598,0.394594594594594,0.363636363636363,0.25,0.125,0]
Dirichlet_weibo=[0.835748792270531,0.604501607717041,0.459459459459459,0.345454545454545,0.25,0.15,0.166666666666666]
plt.plot(x,Dirichlet_weibo,label=u"Dirichlet_weibo")
plt.plot(x,Dirichlet_comment,label=u"Dirichlet_comment")
plt.legend()
plt.xlim(0.0,0.7)
plt.ylim(0.0,1.0)
plt.xlabel("bleu threshold")
plt.ylabel("precesioin rate")
plt.title(u"Dirichlet Model between weibo and comment")
plt.show()