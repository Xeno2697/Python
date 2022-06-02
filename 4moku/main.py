from cgitb import reset
from ssl import PROTOCOL_TLSv1_1
from unittest import result
import numpy as np
from board import board as bd
from Q_player import QLplayer
#自駒は１、敵駒は２

gamma = 0.9#割引率（数手後の報酬の減少係数）
alpha = 0.2#学習率（今回の試行の結果を今までに対してどの程度重視するか）
beta = 0.1#突然変異発生率
X=7
Y=6

board = bd(7,6,4)
player1 = QLplayer(board,False)
player2 = QLplayer(board,True)

for i in range(10000):
    result = 0
    for j in range(X*Y/2):
        hit = player1.choice(board)
        board.push(hit,1)
        if board.judge() == 1:
            result = 1
            break
        ene_hit = player2.choice(board)
        board.push(hit,2)
        if board.judge() == 2:
            result = 2
            break
    
#やっとわかった・・・つまり先手後手どちらでも動き、かつどちらもネガマックス法で動かさないと、正常にQ評価が出来ないってこと！

