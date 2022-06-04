import numpy as np
from board import board as bd
class eAI:
    def __init__(self) -> None:
        pass

    def choice(self, mp:bd, gote:bool):
        path = mp.capable_path()
        result :int = -1
        if gote:
            my = -1
            ene = 1
        else:
            my :int = 1
            ene :int = -1
        #勝利確定探索
        for i in path:
            result = mp.judge(i,my)
            if result == my:
                return i
        #敗北確定探索
        for i in path:
            result = mp.judge(i,ene)
            if result == ene:
                return i          
        return np.random.choice(path)
