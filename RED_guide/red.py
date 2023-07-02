import numpy as np
import math
from field import Field
from path import Path
import random

RED_MOVE_Alpha = 1.0
BLOOD_BLEEDING = 50
class Red: 
    def __init__(self,x,y):
        self.position = np.array((x,y),dtype=float)
        self.mode = 0 #0:mover,1:anker,2:returnee
        
        #収束用パラメータ
        self.number_to_goal = 0
        self.number_to_road = 0
        self.number_to_container = 99
        self.time = 0 #意見を持ち続けた時間
        
        #拡散用パラメータ
        self.anker_inblood = 0.0 #負にするとREDが寄ってくる、正にすると離れる
        self.anker_vectol = np.array([1,0])
        self.anker_number = 0
        self.credibility = 0.0
        
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
        self.number_to_container = -1
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
        n = len(search_data)
        if(n >= 3):
            self.back = False
            distance = 100000
            number = 1000000
            for j in range(n):
                if(distance > search_data[j]['distance']):
                    distance = search_data[j]['distance']
                if(number > search_data[j]['number_to_container']):
                    number = search_data[j]['number_to_container']
            if( distance > 5.0):
                self.mode = 1
                self.number_to_container = number+1
                self.anker_inblood = -BLOOD_BLEEDING
                return 1
        elif(n <= 2):
            self.direction_reversal()
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
            self.mode = 2
            return 2
        if(n < 3):
            #アンカーが十分数存在しないので、とりあえずバック。
            vec_sum = np.zeros(2)
            for i in range(len(search_data)):
                if(search_data[i]['anker_vectol'][0] is not None):
                    distance = search_data[i]['distance']
                    position_vectol = search_data[i]['position_vectol']
                    vec_sum += -position_vectol/distance*0.2
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
        #if(next_pos[0] == np.nan):
        #    print("Error: position is NaN.")
        if(not field.judge_walls(self.position[0],self.position[1],next_pos[0],next_pos[1])):
                self.forward()
        else:
                self.direction_reversal()
                self.forward()
        return 0
    def action_anker(self, path:Path, search_data):
        #返し値は、モード変更したか否か
        #自身のサポーターの数と、血液ベクトル
        t = np.zeros(2)
        f = np.zeros(2)
        if(self.number_to_container != 0):
            self.number_to_container = 99
            for i in range(len(search_data)):
                if(self.number_to_container > search_data[i]['number_to_container']+1):
                    self.number_to_container = search_data[i]['number_to_container']+1
                if(search_data[i]['anker_vectol'][0] is not None):
                    blood = search_data[i]['blood']
                    if(blood > 0):
                        t += blood * search_data[i]['position_vectol']/search_data[i]['distance']
                    elif(blood < 0):
                        f += blood * search_data[i]['position_vectol']/search_data[i]['distance']
            self.anker_vectol = (t+f)/4
            norm = np.linalg.norm(t)
            if(norm <= 0.0 and self.num == 0):
                self.time+=1
                if(self.time > 20 + self.number_to_container * 30):#撤退条件
                    self.mode = 2
                    self.time = 0
                    return 2
            else:
                self.time = 0
        self.num = 0
        
        #自身の意見の信用度
        #自身を必要とする存在の有無
        #意見を変化させるか否か
        
        #自身をムーバーにするか否か
    def action_returnee(self,field:Field, search_data, alpha = RED_MOVE_Alpha/3):
        n = len(search_data)
        if(n == 0):
            #アンカーが一つもない
            return False
        min_num = 10000
        vectol = np.zeros(2)
        for i in range(n):
            if(min_num > search_data[i]['number_to_container'] ):
                min_num = search_data[i]['number_to_container']
                distance = search_data[i]['distance']
                position_vectol = search_data[i]['position_vectol']
                vectol = position_vectol*distance
        if(min_num == 0):
            if(np.linalg.norm(vectol) < 1.0):
                self.mode = 0
                return 0
        #標準偏差を利用したランダム方向移動
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
        #if(next_pos[0] == np.nan):
        #    print("Error: position is NaN.")
        if(not field.judge_walls(self.position[0],self.position[1],next_pos[0],next_pos[1])):
                self.forward()
        else:
                self.direction_reversal()
                self.forward()
        return 2
        #ジャッジ追加
    def move_to_xy(self,x,y):
        vec = np.array([x,y]) - self.position
        dis = np.linalg.norm(vec,ord=2)
        angle = 0.0
        if(dis != 0):
            rad = math.atan2(vec[1], vec[0])
            self.rotate(rad)
        self.forward()