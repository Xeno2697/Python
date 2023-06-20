import numpy as np
class Container:
    def __init__(self,x,y):
        self.position = np.array([x,y])
        self.move_vectol = np.array((0.0,0.0))
        self.bool = True    
    def move(self,vectol):
        if(vectol is False):
            self.position += 0
        else:
            d = np.linalg.norm(vectol,ord=2)
            if(d > 0.01):
                self.move_vectol = vectol/d
            else:
                self.move_vectol = np.zeros(2)
            self.position += self.move_vectol * 0.2  