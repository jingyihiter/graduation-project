import pylab as plt
plt.figure(figsize=(6,6))

x = [0.01,0.1,0.2,0.3,0.4,0.5,0.6]
BM25_y=[0.655394524959742,0.646302250803858,0.6,0.509090909090909,0.416666666666666,0.275,0]
Bool_y=[0.74074074074074,0.398713826366559,0.335135135135135,0.3,0.222222222222222,0.125,0]
Dirichlet_y=[0.684380032206119,0.495176848874598,0.394594594594594,0.363636363636363,0.25,0.125,0]
JelinekMercer_y=[0.505636070853462,0.466237942122186,0.459459459459459,0.409090909090909,0.347222222222222,0.175,0]
plt.plot(x,BM25_y,label=u"BM25")
plt.plot(x,Bool_y,label=u"Bool")
plt.plot(x,Dirichlet_y,label=u"Dirichlet")
plt.plot(x,JelinekMercer_y,label=u"JelinekMercer")
plt.legend()
plt.xlim(0.0,0.7)
plt.ylim(0.0,1.0)
plt.xlabel("bleu threshold")
plt.ylabel("precesioin rate")
plt.title(u"Retrieval Models comparison in searching comment")
plt.show()