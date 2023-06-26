import numpy as np
import math 

BLOOD_SKINNY = 0.1

class Field:
    def __init__(self,mapsize = 80):
        self.obstacles = np.array([[0,0,0]])
        self.walls = np.array([[0,0,0,0]])
        self.mapsize = mapsize
        self.x = np.linspace(0, mapsize, 200) #等間隔でデータを０から２０まで20個作成
        self.y = np.linspace(0, mapsize, 200) #等間隔でデータを０から２０まで20個作成
        self.x, self.y = np.meshgrid(self.x, self.y)
        self.z = np.clip(a = np.cos((self.x-40)*1.5/30)-self.y/90,a_min=0,a_max=100)    
    def obstacle_set(self,x,y,r):
        self.obstacles = np.append(self.obstacles, np.array([[x,y,r]]), axis=0)
        
    def set_wall(self,x1,y1,x2,y2):
        self.walls = np.append(self.walls, np.array([[x1,y1,x2,y2]]), axis=0)
    def judge_walls(self, x1, y1, x2, y2):
        tc1 = (x1 - x2) * (self.walls[:,1] - y1) + (y1 - y2) * (x1 - self.walls[:,0])
        tc2 = (x1 - x2) * (self.walls[:,3] - y1) + (y1 - y2) * (x1 - self.walls[:,2])
        td1 = (self.walls[:,0] - self.walls[:,2]) * (y1 - self.walls[:,1]) + (self.walls[:,1] - self.walls[:,3]) * (self.walls[:,0] - x1)
        td2 = (self.walls[:,0] - self.walls[:,2]) * (y2 - self.walls[:,1]) + (self.walls[:,1] - self.walls[:,3]) * (self.walls[:,0] - x2)
        return np.max((tc1*tc2)<0) and np.max((td1*td2)<0)
    
    def collision_judge(self,x,y):
        for i in self.obstacles:
            vec = np.array([x-i[0],y-i[1]])
            nor = np.linalg.norm(vec,ord=2)
            if(nor < i[2]):
                return True
        if(x < 0 or x > self.mapsize or y < 0 or y > self.mapsize):
            return True
        return False
    def value(x,y):
        z = 0#(math.cos((x-40)*1.5/30)-(y/90))
        if(z < 0):
            z = 0
        z /= 1
        if(z > 1-BLOOD_SKINNY):
            z = 1-BLOOD_SKINNY
        return z  