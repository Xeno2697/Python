from math import inf
from re import X
import numpy as np
from board import board as bd
import random
import math

X:int
Y:int
Q = {}
QMAX = 10000000 

class QLplayer:

    def __init__(self,board:bd,gote:bool = False,a=0.1,g=0.9,s=0.1):
        self.alpha = a #学習率
        self.gamma = g #割引率
        self.sigma = s
        self.gote = gote #突然変異率
        if gote:
            self.my = -1
            self.ene = 1
        else:
            self.my :int = 1
            self.ene :int = -1
        X = board.X
        Y = board.Y
    
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
        else:
            q = np.full(X,-inf)
            for i in path:
                q[i] = self.getQ(map,i)
        return np.argmax(q)

    def getQ(self,state:bd,act):
        key = state.tupleout(self.gote)
        if Q.get(key) is None:
            Q[key] = np.zeros(X)
        return Q[key][act]
    
    def learn(self,state:bd,act :int,reward :float):
        now_state = state.tupleout(self.gote)
        if Q.get(now_state) is None:
                Q[now_state] = np.zeros(7)  
        p :bool = state.push(act,self.my)
        next_state = state.tupleout(not self.gote)
        path = state.capable_path()
        if p:
            state.pop(act)
        m = -inf
        if Q.get(next_state) is None:
                Q[next_state] = np.zeros(7)  
        for i in path:            
            if Q[next_state][i] >= m:
                m = Q[next_state][i]
        if reward != 0:
            Q[now_state][act] = reward
        else:
            d :float = (( 1.0 - self.alpha )*Q[now_state][act])  +( m * self.gamma )
            if d > QMAX:
                d = QMAX
            elif d < -QMAX:
                d = -QMAX
            Q[now_state][act] = d
        return

        