import numpy as np
from board import board as bd
class eAI:
    def __init__(self) -> None:
        pass

    def choice(self, mp:bd, gote:bool):
        koma = 0
        if gote:
            koma = -1
        else:
            koma = 1
        i = mp.search(koma , mp.map.copy())
        if i != -1:
            return i+10000
        else:
            return np.random.choice(mp.capable_path())
