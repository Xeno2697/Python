from http.client import ImproperConnectionState
import re
from unittest import result
from xml.sax import make_parser
import numpy as np

class board:
    def __init__(self,x=7,y=6,winnum=4):
        self.X = x
        self.Y = y
        self.WINIF = winnum
        self.lastputx = 0
        self.lastputy = 0

        self.map = np.zeros((x,y))
     
    def push(self, x:int, koma:int):
        for i in range(self.Y):
            if self.map[x,i] == 0:
                self.map[x,i] = koma
                self.lastputx = x
                self.lastputy = i
                return True
        
        print("Error! I tried put koma, but I could not.")
        return False
    
    def capable_path(self):
        path = []
        for i in range(self.X):
            if self.map[i,self.Y-1] == 0:
                path.append(i)
        return path
     
    def reset(self):
        self.map = np.zeros((self.X,self.Y))
        return
    
    def search(self,koma,mpp = np.zeros(0)):
        if mpp == np.zeros(0):
            mpp = self.map.copy()
        #　mppは必ず複製数列を使用すること
        for i in range(self.X):
            for y in range(self.Y):
                if mpp[i,y] == 0:
                    break
                elif y == self.Y-1:
                    y = -1
            if y != -1:
                mpp[i,y] = koma
                if self.judge(mpp,i,y):
                    return i
                else:
                    mpp[i,y] = 0      
        return -1

    def judge(self,mpp,x = 0,y=-1):
        if y == -1:
            for y in range(self.Y):
                if mpp[x,y] == 0:
                    y = y-1
                    break
        koma = mpp[x,y]

        count = 0
        for i in range(self.Y):
            if mpp[x,i] == koma:
                count += 1
                if count == self.WINIF:
                    return True
            else:
                count = 0

        count = 0
        for i in range(self.X):
            if mpp[i,y] == koma:
                count += 1
                if count == self.WINIF:
                    return True
            else:
                count = 0
        
        count = 0
        a = min(x,y)
        b = min(self.X-x+a,self.Y-y+a)
        for i in range(b):
            if mpp[x-a+i,y-a+i] == koma:
                count += 1
                if count == self.WINIF:
                    return True
            else:
                count = 0
        
        count = 0
        player = 0
        a = min(self.X-1-x,y)
        b = min(x+a+1,self.Y-(y-a))
        for i in range(b):
            if mpp[x+a-i,y-a+i] == koma:
                count += 1
                if count == self.WINIF:
                    return True
            else:
                count = 0

        return False       

    def tupleout(self,gote:bool):
        a = 1
        if gote:
            a = -1
        return tuple(map(tuple, self.map*a))

    def arrayout(self,gote):
        out = self.map
        if gote:
            out *= -1
        return out

    def print(self):
        for i in range(self.X+2):
            print("-",end="")
        print("")
        for i in reversed(range(self.Y)):
            print("|",end="")
            for j in range(self.X):
                a=self.map[j,i]
                if a == 0:
                    print(" ",end="")
                elif a == 1:
                    print("○",end="")
                else :
                    print("x",end="")
            print("|")
        for i in range(self.X+2):
            print("-",end="")
        print("")