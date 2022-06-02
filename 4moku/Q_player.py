from math import inf
import numpy as np
from board import board as bd
import random

class QLplayer:

    def __init__(self,board:bd,a=0.1,g=0.9,s=0.1):
        self.q = {}#Q評価
        self.alpha = a #学習率
        self.gamma = g #割引率
        self.sigma = s #突然変異率
        self.x = board.X
        self.y = board.Y
    
    def choice(self,map:bd):
        result = -1
        #勝利確定探索
        path = map.capable_path()
        for i in path:
            result = map.judge(i,1)
            if result == 1:
                return i
        #敗北確定探索
        for i in path:
            result = map.judge(i,2)
            if result == 2:
                return i          
        #低確率ランダム
        if random.random() < self.sigma:
            return random.choice(path)
        #Q値から最大価値手を打つ。
        else:
            q = np.full(7,-inf)
            for i in range(path):
                q[i] = self.getQ(map,i)
        return np.argmax(q)

    def getQ(self,state:bd,act):
        key = state.tupleout()
        if self.q.get(key) is None:
            self.q[key] = np.zeros(self.x)
        return self.q[key][act]
    
    def learn(self,state:bd,act,reward):
        now_state = state.tupleout()
        p :bool = state.push(act)
        next_state = state.tupleout()
        if not p:
            state.pop(act)
        self.q[now_state][act] = (1-self.alpha)(self.q[now_state][act])+(reward+np.amax(self.q[next_state])) * self.gamma
        return

        