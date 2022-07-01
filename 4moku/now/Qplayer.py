from cmath import inf
import numpy as np
import random

from tqdm import tqdm
from board import board as bd
import csv

class Qplayer:

    def __init__(self,mp:bd,a=0.35,g=0.95,s=0.1):
        self.X = mp.X
        self.Y = mp.Y
        self.alpha = a
        self.gamma = g
        self.sigma = s
        self.Q = {}
        self.csv_read()
        return

    def choice(self,map:bd,gote):
        self.koma = 1
        if gote:
            self.koma = -1
        path = map.search(self.koma)#勝利確定の手を探す
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
                max = -inf
                f = 0
                for i in range(self.X):
                    if max < qarray[i]:
                        max = qarray[i]
                        f = i
                return f

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
        if map_array[act,self.Y-1] != 0:
            print("Error! learning's act is wrong.",end="")
            print(act) 
        for i in range(self.Y):
            if map_array[act,i] == 0:
                map_array[act,i] = koma
                break
        if gote:
            map_array *= -1
        next_Qarray = self.qget(tuple(map(tuple,map_array)),-1)
        map_array[act,i] = 0

        l = 0
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
    
    def csv_write(self):
        with open('Qlearning.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            p = [[0 for a in range(self.Y)] for b in range(self.X)]
            for i,key in tqdm(enumerate(self.Q)):
                for j in range(self.X):
                    for k in range(self.Y):
                        if key[j][k] == 0:
                            p[j][k] = str(0)
                        elif key[j][k] == 1:
                            p[j][k] = str(1)
                        else:
                            p[j][k] = str(2)
                val = ""
                for j in range(self.X):
                    val += "".join(p[j])
                writer.writerow([val]+[ a for a in self.Q[key]])
    
    def csv_read(self):
        with open('Qlearning.csv', 'r') as f:
            key_list = [[0 for a in range(self.Y)] for b in range(self.X)]
            reader = csv.reader(f)
            for row in tqdm(reader): 
                key_str = row[0]
                for i in range(self.X):
                    for j in range(self.Y):
                        if key_str[self.Y*i+j] == "1":
                            key_list[i][j] = int(1)
                        elif key_str[self.Y*i+j] == "2":
                            key_list[i][j] = int(-1)
                        else:
                            key_list[i][j] = int(0)
                row = [float(a) for a in row[1:]]
                self.Q[tuple(map(tuple, key_list))] = row