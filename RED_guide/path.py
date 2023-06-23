import numpy as np
BLOOD_BLEEDING = 50 #新規領域開拓時の引き寄せ力
BLOOD_CURE = 0.2
BLOOD_SKINNY = 0.1
BLOOD_FAT = 0.3
class Path:
    def __init__(self,n = 30):
        self.n = n
        self.connect = np.array([[False for i in range(n)] for j in range(n)])
        self.blood = np.zeros((n,n))
        self.size = np.zeros((n,n))
        self.reducation = np.array([[0 for i in range(n)] for j in range(n)])
        self.toconnect(0,[1],[1])
        self.toconnect(1,[2],[0.4])
        self.toconnect(0,[2],[1])    
    def toconnect(self, a, b, l = [1.0],s = [0.0]):
        if(type(b) is int):
            b = np.array([b])
        n = 3
        if(len(b) < n):
            n = len(b)
        for i in range(n):
            self.connect[a,b[i]] = True
            self.connect[b[i],a] = True
            self.size[a,b[i]] = 1.0/l[i]
            self.size[b[i],a] = 1.0/l[i] 
            self.reducation[a,b[i]] = s[i]
            self.reducation[b[i],a] = s[i]
    def disconnect(self,a):
        self.connect[a,:] = np.zeros(self.n)
        self.connect[:,a] = np.zeros(self.n)
        self.blood[a,:] = np.zeros(self.n)
        self.blood[:,a] = np.zeros(self.n)
        self.size[a,:] = np.zeros(self.n)
        self.size[:,a] = np.zeros(self.n)
    #血流調整、および血流ベクトル計算  
    def reset(self):
        self.connect = np.array([[False for i in range(self.n)] for j in range(self.n)])
        self.blood = np.zeros((self.n,self.n))
        self.size = np.zeros((self.n,self.n))
        #self.toconnect(0,[1],[1])
        #self.toconnect(1,[2],[1])
        #self.toconnect(0,[2],[1])
    def blood_regulation(self,i,inblood = 0.0):
        #流入量計算
        q = self.blood[:,i].sum()
        #流入量/パス数　＝パス流出量
        n = self.size[i,:].sum()
        #血液輸出
        self.blood[i,:] = ( q + inblood - 0.1) * self.size[i,:] / n
        #血管幅増減
        self.size[i,:] = np.abs(self.blood[i,:] - self.blood[:,i]) * BLOOD_FAT + ((1-(BLOOD_SKINNY+self.reducation[i,:])) * self.size[i,:])
        self.size[:,i] = np.abs(self.blood[i,:] - self.blood[:,i]) * BLOOD_FAT + ((1-(BLOOD_SKINNY+self.reducation[i,:])) * self.size[:,i])           
