import numpy as np
import random
from board import board as bd

class Qplayer:

    def __init__(self,map:bd,a=0.35,g=0.95,s=0.0):
        self.X = map.X
        self.Y = map.Y
        self.alpha = a
        self.gamma = g
        self.sigma = s
        self.Q = {(0):0}

    def choice(self,map:bd,gote):
        self.koma = 1
        if gote:
            self.koma = -1
        path = map.search(self.koma,map.map)
        if path != -1:
            return path+10000
        else:
            #勝利確定の手を探す
            if random.random() < self.sigma:
                #一定確率でランダムな可能な手を打つ
                path = np.array(map.capable_path())
                return np.random.choice(path)
            else:
                #見つからないなら、Q学習データから最善手を求める
                qarray = self.qget(map,-1,gote)
                return np.argmax(qarray)

    def qget(self, key, act =-1, got = False):
        if key in self.Q:
            a = self.Q[key]
            if act == -1:
                return a
            else:
                return a[act]
        else:
            self.Q[key] = np.zeros(self.X)
            return 0
            
    def learn(self,mp:bd,act,gote,reward= 0):
        map_array = mp.arrayout(gote)
        for i in range(self.Y):
            if map_array[act,i] == 0:
                mp.map[act,i] = 1
                break
            elif i == self.Y-1:
                print("Error!this action is inpossible!")
        map_array *= -1
        l = 0
        for i in range(self.X):           
            if map_array[i,self.Y-1] == 0:
                q = self.qget(tuple(map(tuple, map_array)),i,gote)
                if l < q:
                    l = q
        self.Q[mp.tupleout(gote)][act] = ((1.0 - self.alpha)*self.Q[mp.tupleout(gote)][act])  +( -l * self.gamma +reward)
        return

