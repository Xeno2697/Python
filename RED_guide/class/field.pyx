import numpy as np
import cython 

BLOOD_SKINNY = 0.1

class Field:
    def __init__(self,mapsize:cython.int = 80):
        self.obstacles = np.array([[0,0,0]])
        self.walls = np.array([[0,0,0,0]])
        self.set_wall(0,0,mapsize,0)
        self.set_wall(0,0,0,mapsize)
        self.set_wall(0,mapsize,mapsize,mapsize)
        self.set_wall(mapsize,0,mapsize,mapsize)
        self.mapsize = mapsize
    def obstacle_set(self,x:cython.float,y:cython.float,r:cython.float):
        self.obstacles = np.append(self.obstacles, np.array([[x,y,r]]), axis=0)
        
    def set_wall(self,x1:cython.float,y1:cython.float,x2:cython.float,y2:cython.float):
        self.walls = np.append(self.walls, np.array([[x1,y1,x2,y2]]), axis=0)
    cdef bool judge_walls(self, x1:cython.float, y1:cython.float, x2:cython.float, y2:cython.float):
        """壁に抵触する場合True"""
        cdef float tc1 = (x1 - x2) * (self.walls[:,1] - y1) + (y1 - y2) * (x1 - self.walls[:,0])
        cdef float tc2 = (x1 - x2) * (self.walls[:,3] - y1) + (y1 - y2) * (x1 - self.walls[:,2])
        cdef float td1 = (self.walls[:,0] - self.walls[:,2]) * (y1 - self.walls[:,1]) + (self.walls[:,1] - self.walls[:,3]) * (self.walls[:,0] - x1)
        cdef float td2 = (self.walls[:,0] - self.walls[:,2]) * (y2 - self.walls[:,1]) + (self.walls[:,1] - self.walls[:,3]) * (self.walls[:,0] - x2)
        return np.max(((tc1*tc2)<0)*((td1*td2)<0))
    
    cdef bool def collision_judge(self, cdef int x, cdef int y):
        cdef int i
        for i in self.obstacles:
            vec = np.array([x-i[0],y-i[1]])
            cdef float nor = np.linalg.norm(vec,ord=2)
            if(nor < i[2]):
                return True
        if(x < 0 or x > self.mapsize or y < 0 or y > self.mapsize):
            return True
        return False 