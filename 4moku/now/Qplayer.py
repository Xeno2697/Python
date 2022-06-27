from cmath import inf
import numpy as np
import random
from board import board as bd

class Qplayer:

    def __init__(self,map:bd,a=0.35,g=0.95,s=0.1):
        self.X = map.X
        self.Y = map.Y
        self.alpha = a
        self.gamma = g
        self.sigma = s
        self.Q = {tuple((map.X,map.Y)):list([0,0,0,0,0,0,0])}

    def choice(self,map:bd,gote):
        self.koma = 1
        if gote:
            self.koma = -1
        path = map.search(self.koma,map.map)#勝利確定の手を探す
        if path != -1:
            return path+10000
        else:
            if random.random() < self.sigma:
                #一定確率でランダムな可能な手を打つ
                path = np.array(map.capable_path())
                return np.random.choice(path)
            else:
                #見つからないなら、Q学習データから最善手を求める
                qarray = self.qget(map.tupleout(gote),-1)
                return np.argmax(qarray)

    def qget(self, key:tuple, act =-1):
        if key in self.Q:
            a = self.Q[key]
            if act == -1:
                return a
            else:
                return a[act]
        else:
            a = np.zeros(self.X)
            for i in range(self.X):
                if key[i][self.Y-1] != 0:
                    a[i] = -float('inf')
            self.Q[key] = a
            if act == -1:
                return a
            else:
                return a[act]
            
    def learn(self,mp:bd,act,gote:bool,reward= 0):
        map_array = mp.arrayout(gote)
        t = mp.tupleout(gote)
        yet_Q = self.qget(t,act) 
        koma = 0
        if gote:
            koma = -1
        else:
            koma = 1
        for i in range(self.Y):
            if map_array[act,i] == 0:
                map_array[act,i] = koma
                break
        if not gote:
            map_array *= -1
            next_Qarray = self.qget(tuple(map(tuple,map_array)),-1)
            map_array[act,i] = 0
        else:
            next_Qarray = self.qget(tuple(map(tuple,map_array)),-1)
            map_array[act,i] = 0

        l = -inf
        for i in range(self.X):
            if map_array[i,self.Y-1] == 0:
                q = next_Qarray[i]
                if l<q:
                    l=q
        if l == -inf:
            l = 0
        if reward > 0:
            self.Q[t][act] = ((1.0 - self.alpha)*yet_Q)  + (reward)
        else:
            self.Q[t][act] = ((1.0 - self.alpha)*yet_Q)  + ( -l * self.gamma)
        return