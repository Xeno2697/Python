from math import inf
from re import X
import numpy as np
from board import board as bd
import random
import math

X:int = 7
Y:int = 6
q = {}
QMAX = 10000000 

class QLplayer:

    def __init__(self,board:bd,gote:bool = False,a=0.35,g=0.95,s=0.0):
        self.alpha = a #学習率
        self.gamma = g #割引率
        self.sigma = s #突然変異率
        self.gote = gote 
        if gote:
            self.my = -1
            self.ene = 1
        else:
            self.my :int = 1
            self.ene :int = -1
        self.q = q
    
    def choice(self,map:bd):
        result = -1
        #勝利確定探索
        path = map.capable_path()
        for i in path:
            result = map.judge(i,self.my)
            if result == self.my:
                return i
        #敗北確定探索
        for i in path:
            result = map.judge(i,self.ene)
            if result == self.ene:
                return i          
        #低確率ランダム
        if random.random() < self.sigma:
            return np.random.choice(path)
        #Q値から最大価値手を打つ。
        c = np.full(X,-np.inf)
        key = map.tupleout(self.gote)
        if not key in q:
            q[key] = np.zeros(X)
        for i in path:
            c[i] = q[key][i]
        return np.argmax(c)
    
    def learn(self,state:bd,act :int,reward :float = 0):
        now_state = state.tupleout(self.gote)
        if q.get(now_state) is None:
                q[now_state] = np.zeros(7)  
        p :bool = state.push(act,self.my)
        next_state = state.tupleout(not self.gote)
        path = state.capable_path()

        if p:
            state.pop(act)
        
        m = -np.inf
        if not next_state in q:
            q[next_state] = np.zeros(X)
        for i in path:            
            if q[next_state][i] > m:
                m = q[next_state][i]
        
        d = (( 1.0 - self.alpha )*q[now_state][act])  +( -m * self.gamma +reward)
        q[now_state][act]  = d
        if q[now_state][act] != 0:
            print('',end='')
        return