from cgitb import reset
from ssl import PROTOCOL_TLSv1_1
from unittest import result
import numpy as np
from tqdm import tqdm
from board import board as bd
from Q_player import QLplayer
#自駒は1、敵駒は-1

gamma = 0.9#割引率（数手後の報酬の減少係数）
alpha = 0.2#学習率（今回の試行の結果を今までに対してどの程度重視するか）
beta = 0.1#突然変異発生率
X=7
Y=6

sum_1win = 0
sum_2win = 0

board = bd(7,6,4)
player1 = QLplayer(board,False)
player2 = QLplayer(board,True)


for i in tqdm(range(1000)):
    result = 0
    board.reset()
    for j in range((int)(X*Y/2)):
        r = 0
        hit = player1.choice(board)
        if board.judge(hit,1) == 1:
            r = 1
            player1.learn(board,hit,r)
            board.push(hit,1)
            sum_1win += 1
            break
        else:
            player1.learn(board,hit,r)
            board.push(hit,1)

        

        r = 0
        ene_hit = player2.choice(board)
        if board.judge(ene_hit,-1) == -1:
            r = 1
            player2.learn(board,ene_hit,r)
            board.push(ene_hit,-1)
            sum_2win += 2
            break
        else:
            player2.learn(board,ene_hit,r)
            board.push(ene_hit,-1)

        


for i in range(1):
    result = 0
    board.reset()
    for j in range((int)(X*Y/2)):
        r = 0
        hit = player1.choice(board)
        if board.judge(hit,1) == 1:
            r = 1
            player1.learn(board,hit,r)
            board.push(hit,1)
            print('player1 win')
            break
        else:
            player1.learn(board,hit,r)
            board.push(hit,1)

        board.show()

        r = 0
        ene_hit = player2.choice(board)
        if board.judge(ene_hit,-1) == -1:
            r = 1
            player2.learn(board,ene_hit,r)
            board.push(ene_hit,-1)
            print('player2 win')
            break
        else:
            player2.learn(board,ene_hit,r)
            board.push(ene_hit,-1)

        board.show()
    board.show()
    print('先手',end = '')
    print(sum_1win,end = '')
    print('回勝利')
    print('後手',end = '')
    print(sum_2win,end = '')
    print('回勝利') 
#やっとわかった・・・つまり先手後手どちらでも動き、かつどちらもネガマックス法で動かさないと、正常にQ評価が出来ないってこと！

