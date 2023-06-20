import numpy as np
import math
from field import logicalmap
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
        self.anker_vectol = np.array([0,0])
        self.move_vectol = np.array([1,0])
        
        self.back = False
        self.num = 0
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
        self.position += self.move_vectol * power
    def rotate(self, rad_abs):
        self.move_vectol = np.array([math.cos(rad_abs), math.sin(rad_abs)])
    def direction_reversal(self):
        self.back = True
        self.move_vectol *= -1
    def move_random(self,logimap:logicalmap, vectol = np.zeros(2), alpha = RED_MOVE_Alpha):
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
    def move_to_xy(self,x,y):
        vec = np.array([x,y]) - self.position
        dis = np.linalg.norm(vec,ord=2)
        angle = 0.0
        if(dis != 0):
            rad = math.atan2(vec[1], vec[0])
            self.rotate(rad)
        self.forward() 