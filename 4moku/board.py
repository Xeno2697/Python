from http.client import ImproperConnectionState
from unittest import result
from xml.sax import make_parser
import numpy as np

X:int = 7
Y:int = 6
WIN_CONDITION = 4
mp = np.zeros((X,Y))

last_put_x = 3 #勝敗判定に利用
last_put_y = 4 #勝敗判定に利用
class board:

    def __init__(self):
        mp = np.zeros((X,Y))    

    def capable_path(self):
        path = []
        for i in range(X):
            if mp[i,Y-1] == 0:
                path.append(i)
        return path
    
    def push(x,player):
        for i in range(Y):
            if mp[x,i] == 0:
                mp[x,i] = player
                last_put_x = X
                last_put_y = i
                break
        return mp

    def pop(x):
        a = 0
        for i in reversed(range(Y)):
            if mp[x,i] != 0:
                a = mp[x,i]
                mp[x,i] = 0
                break
        return a

    def show():
        print('--',end='')
        for i in range(X):
            print('-',end='')
        print('')
        for i in reversed(range(Y)):
            print('|',end='')
            for j in range(X):
                if mp[j,i] == 0:
                    print(' ',end='')
                elif mp[j,i] == 1:
                    print('o',end='')
                elif mp[j,i] == 2:
                    print('x',end='')
            print('|')
        print('--',end='')
        for i in range(X):
            print('-',end='')
        print('')

    def reset():
        mp = np.zeros(X,Y)

    def tupleout():
        return tuple(map(tuple, mp))
    
    def judge(x=-1,play = 1):#引数がない場合はそのまま、ある場合、配置後の仮想マップを判定
        #最後に駒配置された縦列を勝敗確認
        if x != -1:
            board.push(x,play)
        player = 0
        count = 0
        result = 0
        for i in range(Y):
            if mp[last_put_x,i] == 0:
                count = 0
                player = 0
            elif mp[last_put_x,i] == player:
                count += 1
                if count == 4:
                    result = player
                    break
            else:
                count = 1
                player = mp[last_put_x,i]

        if result == 0:
            #最後に駒配置された横列を勝敗確認
            player = 0
            count = 0
            result = 0
            for i in range(X):
                if mp[i,last_put_y] == 0:
                    count = 0
                    player = 0
                elif mp[i,last_put_y] == player:
                    count += 1
                    if count == 4:
                        result = player
                        break
                else:
                    count = 1
                    player = mp[i,last_put_y]

            if result == 0:
                #\斜め確認
                a = min(last_put_x,last_put_y)
                b = min(X-last_put_x+a-1,Y-last_put_y+a-1)
                for i in range(b):
                    if mp[last_put_x-a+i,last_put_y-a+i] == 0:
                        count = 0
                        player = 0
                    elif mp[last_put_x-a+i,last_put_y-a+i] == player:
                        count += 1
                        if count == 4:
                            result = player
                            break
                    else:
                        count = 1
                        player = mp[last_put_x-a+i,last_put_y-a+i]

                if result == 0:
                    #/斜め確認
                    a = min(X-1-last_put_x,last_put_y)
                    b = min(last_put_x+a+1,Y-(last_put_y-a))
                    for i in range(b):
                        if mp[last_put_x+a-i,last_put_y-a+i] == 0:
                            count = 0
                            player = 0
                        elif mp[last_put_x+a-i,last_put_y-a+i] == player:
                            count += 1
                            if count == 4:
                                result = player
                                break
                        else:
                            count = 1
                            player = mp[last_put_x+a-i,last_put_y-a+i]
                        #print(last_put_x+a-i,last_put_y-a+i)
        if x != -1:
            board.pop(x)
        return result

board.show()