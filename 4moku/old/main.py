from cgitb import reset
from ssl import PROTOCOL_TLSv1_1
from unittest import result
import numpy as np
from tqdm import tqdm
from board import board as bd
from Q_player import QLplayer
from easyAI import eAI as ai
#自駒は1、敵駒は-1

gamma = 0.9#割引率（数手後の報酬の減少係数）
alpha = 0.2#学習率（今回の試行の結果を今までに対してどの程度重視するか）
beta = 0.1#突然変異発生率
X=7
Y=6

sum_ewin = 0
sum_qwin = 0

board = bd(7,6,4)
board1 = bd(7,6,4)
player1 = QLplayer(board,False)
player2 = QLplayer(board,True)
easyai = ai()

w:int = 0
l:int = 0

for i in tqdm(range(1000)):
    #if i %500 == 0:
    #    player1.learn(board1,0,0)
    #    board1.push(0,1)
    #    player2.learn(board1,0,0)
    #    board1.show()

    #先手Q-learning 後手Q-learning
    result = 0
    board.reset()
    for j in range((int)(X*Y/2)):
        r = 0
        hit = player1.choice(board)
        if board.judge(hit,1) == 1:
            r = 1
            player1.learn(board,hit,r)
            board.push(hit,1)
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
            break
        else:
            player2.learn(board,ene_hit,r)
            board.push(ene_hit,-1)

    if (i+1) %200 == 0:
        board.show()
        print('win',end='')
        print(w,end='')
        print('_lose',end='')
        print(l,end='_')
        print((float)(w / (w+l)) * 100,end = '')
        print('%')
        w = 0
        l = 0

    #先手Q-learning 後手AI
    result = 0
    board.reset()
    for j in range((int)(X*Y/2)):
        r = 0
        hit = player1.choice(board)
        if board.judge(hit,1) == 1:
            r = 1
            player1.learn(board,hit,r)
            board.push(hit,1)
            sum_qwin += 1
            w += 1
            break
        else:
            player1.learn(board,hit,r)
            board.push(hit,1)
        r = 0
        ene_hit = easyai.choice(board,False)
        if board.judge(ene_hit,-1) == -1:
            r = 1
            board.push(ene_hit,-1)
            sum_ewin += 1
            l += 1
            break
        else:
            board.push(ene_hit,-1)

    #先手AI 後手Q-learning
    result = 0
    board.reset()
    for j in range((int)(X*Y/2)):
        r = 0
        b = True
        hit = easyai.choice(board,b)
        if board.judge(hit,1) == 1:
            r = 1
            board.push(hit,1)
            sum_ewin += 1
            l += 1
            break
        else:
            board.push(hit,1)
        r = 0
        ene_hit = player2.choice(board)
        if board.judge(ene_hit,-1) == -1:
            r = 1
            player2.learn(board,ene_hit,r)
            board.push(ene_hit,-1)
            sum_qwin += 1
            w += 1
            break
        else:
            player2.learn(board,ene_hit,r)
            board.push(ene_hit,-1)

board.show()       
print('easyAI',end = '')
print(sum_ewin,end = '')
print('回勝利')
print('Q-leaning',end = '')
print(sum_qwin,end = '')
print('回勝利')      
#やっとわかった・・・つまり先手後手どちらでも動き、かつどちらもネガマックス法で動かさないと、正常にQ評価が出来ないってこと！

