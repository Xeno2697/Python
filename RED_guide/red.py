import numpy as np
import math
from field import Field
from path import Path
import random

RED_MOVE_Alpha = 1.0

class Red: 
    def __init__(self,x,y):
        self.position = np.array((x,y),dtype=float)
        self.anker = False
        
        #収束用パラメータ
        self.number_to_goal = 0
        self.number_to_road = 0
        self.number_to_container = 0
        self.time = 0
        
        #拡散用パラメータ
        self.anker_inblood = 0.0 #負にするとREDが寄ってくる、正にすると離れる
        self.anker_vectol = np.array([1,0])
        self.anker_number = 0
        
        #協調用パラメータ
        self.number_of_supporters = 0 #自身の意見に同調するREDの数、大きいほど優先率が高い
        
        #動作パラメータ
        self.back = False
        self.num = 0
        self.move_vectol = np.array([1,0])
        
    def change_to_mover(self):
        self.anker = False
        self.anker_inblood = 0.0
        self.anker_vectol = np.array([0,0])
        self.back = False
        self.num = 0
        self.number_to_goal = 0
        self.number_to_road = 0
        self.number_to_container = 0
        self.direction_reversal()
        self.forward()
    def forward(self,power = 1.0):
        if(not np.isnan(self.move_vectol[0])):
            self.position += self.move_vectol * power
        else:
            self.move_vectol = np.array([1,0])
    def rotate(self, rad_abs = 0):
        if(rad_abs > math.pi):
            rad_abs -= math.pi*2
        elif(rad_abs < math.pi):
            rad_abs += math.pi*2
        self.move_vectol = np.array([math.cos(rad_abs), math.sin(rad_abs)])
    def direction_reversal(self):
        self.back = True
        self.move_vectol *= -1
    def move_random(self,logimap:Field, vectol = np.zeros(2), alpha = RED_MOVE_Alpha):
            if(vectol is False):
                self.direction_reversal()
            if(random.random() < 0.4 and not self.back):
                dis = np.linalg.norm(vectol,ord=2)
                angle = 0.0
                if(dis == 0):
                    angle = (random.random()-0.5)*2.0*math.pi
                else:
                    rad = math.atan2(vectol[1], vectol[0])
                    angle = random.gauss(rad, math.pi/2*alpha)
                self.rotate(angle)
            next_pos = self.position + self.move_vectol
            if(not logimap.collision_judge(next_pos[0],next_pos[1])):
                self.forward()
            else:
                self.direction_reversal()
                self.forward()
    def action_mover(self, field:Field, search_data, alpha = RED_MOVE_Alpha):
        n = 0
        vec_sum = np.zeros(2)
        for i in range(len(search_data)):
            if(search_data[i]['anker_vectol'][0] is not None):
                distance = search_data[i]['distance']
                anker_vectol = search_data[i]['anker_vectol']
                position_vectol = search_data[i]['position_vectol']
                #naiseki = np.dot(anker_vectol,position_vectol)
                vec_sum += (anker_vectol+(position_vectol/distance*0.2))*0.1
                n += 1
        if(n == 0):
            #アンカーが一つもない
            return False
        if(n < 3):
            #アンカーが十分数存在しないので、とりあえずバック。
            n = 0
            for i in range(len(search_data)):
                if(search_data[i]['anker_vectol'][0] is not None):
                    distance = search_data[i]['distance']
                    anker_vectol = search_data[i]['anker_vectol']
                    position_vectol = search_data[i]['position_vectol']
                    #naiseki = np.dot(anker_vectol,position_vectol)
                    vec_sum += -position_vectol/distance*0.2
                    n += 1
            #標準偏差を利用したランダム方向移動
        vectol = vec_sum/n
        if(random.random() < 0.4 and not self.back):
                dis = np.linalg.norm(vectol,ord=2)
                angle = 0.0
                if(dis == 0):
                    angle = (random.random()-0.5)*2.0*math.pi
                else:
                    rad = math.atan2(vectol[1], vectol[0])
                    angle = random.gauss(rad, math.pi/2*alpha)
                self.rotate(angle)
            
        next_pos = self.position + self.move_vectol
        if(next_pos[0] == np.nan):
            print("Error: position is NaN.")
        if(not field.collision_judge(next_pos[0],next_pos[1])):
                self.forward()
        else:
                self.direction_reversal()
                self.forward()
    def action_anker(self, path:Path, data):
        #自身のサポーターの数
        #自身の意見の信用度
        #自身を必要とする存在の有無
        #意見を変化させるか否か
        #自身をムーバーにするか否か
        a = 1
    def move_to_xy(self,x,y):
        vec = np.array([x,y]) - self.position
        dis = np.linalg.norm(vec,ord=2)
        angle = 0.0
        if(dis != 0):
            rad = math.atan2(vec[1], vec[0])
            self.rotate(rad)
        self.forward() 