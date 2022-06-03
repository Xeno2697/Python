from http.client import ImproperConnectionState
from unittest import result
from xml.sax import make_parser
import numpy as np
class board:

    def __init__(self,x=7,y=6,win=4):
        self.X=x
        self.Y=y
        self.WIN_CONDITION =win
        self.mpp = np.zeros((self.X,self.Y))
        self.last_put_x = 3
        self.last_put_y = 4

    def capable_path(self):
        path = []
        for i in range(self.X):
            if self.mpp[i,self.Y-1] == 0:
                path.append(i)
        return path
    
    def push(self,x : int,koma :int):
        for i in range(self.Y):
            if self.mpp[x,i] == 0:
                self.mpp[x,i] = koma
                self.last_put_x = x
                self.last_put_y = i
                return True
        print('Error cannot push')
        return False

    def pop(self,x):
        a = 0
        for i in reversed(range(self.Y)):
            if self.mpp[x,i] != 0:
                a = self.mpp[x,i]
                self.mpp[x,i] = 0
                break
        return a

    def show(self):
        print('--',end='')
        for i in range(self.X):
            print('-',end='')
        print('')
        for i in reversed(range(self.Y)):
            print('|',end='')
            for j in range(self.X):
                if self.mpp[j,i] == 0:
                    print(' ',end='')
                elif self.mpp[j,i] == 1:
                    print('o',end='')
                elif self.mpp[j,i] == -1:
                    print('x',end='')
            print('|')
        print('--',end='')
        for i in range(self.X):
            print('-',end='')
        print('')

    def reset(self):
        self.mpp = np.zeros((self.X,self.Y))

    def tupleout(self,reverse : bool = False):
        out = np.zeros((self.X,self.Y))
        if reverse:
            out *= -1
            return tuple(map(tuple, out))
        else:
            return tuple(map(tuple, self.mpp))
    
    def judge(self,x=-1,play = 1):#引数がない場合はそのまま、ある場合、配置後の仮想マップを判定
        #最後に駒配置された縦列を勝敗確認
        play = np.array(play)
        if x != -1:
            self.push(x,play)
        player = 0
        count = 0
        result = 0
        for i in range(self.Y):
            if self.mpp[self.last_put_x,i] == 0:
                count = 0
                player = 0
            elif self.mpp[self.last_put_x,i] == player:
                count += 1
                if count == self.WIN_CONDITION:
                    if x != -1:
                        self.pop(x)
                    return player
            else:
                count = 1
                player = self.mpp[self.last_put_x,i]

        if result == 0:
            #最後に駒配置された横列を勝敗確認
            player = 0
            count = 0
            for i in range(self.X):
                if self.mpp[i,self.last_put_y] == 0:
                    count = 0
                    player = 0
                elif self.mpp[i,self.last_put_y] == player:
                    count += 1
                    if count == self.WIN_CONDITION:
                        if x != -1:
                            self.pop(x)
                        return player
                else:
                    count = 1
                    player = self.mpp[i,self.last_put_y]

            if result == 0:
                #\斜め確認
                #print('|')
                count = 0
                player = 0
                a = min(self.last_put_x,self.last_put_y)
                b = min(self.X-self.last_put_x+a,self.Y-self.last_put_y+a)
                for i in range(b):
                    if self.mpp[self.last_put_x-a+i,self.last_put_y-a+i] == 0:
                        count = 0
                        player = 0
                    elif self.mpp[self.last_put_x-a+i,self.last_put_y-a+i] == player:
                        count += 1
                        if count == self.WIN_CONDITION:
                            if x != -1:
                                self.pop(x)
                            return player
                    else:
                        count = 1
                        player = self.mpp[self.last_put_x-a+i,self.last_put_y-a+i]
                    #print(self.last_put_x-a+i,self.last_put_y-a+i)

                if result == 0:
                    #/斜め確認
                    #print('/')
                    count = 0
                    player = 0
                    a = min(self.X-1-self.last_put_x,self.last_put_y)
                    b = min(self.last_put_x+a+1,self.Y-(self.last_put_y-a))
                    for i in range(b):
                        if self.mpp[self.last_put_x+a-i,self.last_put_y-a+i] == 0:
                            count = 0
                            player = 0
                        elif self.mpp[self.last_put_x+a-i,self.last_put_y-a+i] == player:
                            count += 1
                            if count == self.WIN_CONDITION:
                                if x != -1:
                                    self.pop(x)
                                return player
                        else:
                            count = 1
                            player = self.mpp[self.last_put_x+a-i,self.last_put_y-a+i]
                        #print(self.last_put_x+a-i,self.last_put_y-a+i)
        if x != -1:
            self.pop(x)
        return 0