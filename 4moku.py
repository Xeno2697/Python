from array import array
from operator import truediv
from tkinter import END
import numpy as np
import random
from tqdm import tqdm

#自駒は１、敵駒は２

gamma = 0.9#割引率（数手後の報酬の減少係数）
alpha = 0.1#学習率（今回の試行の結果を今までに対してどの程度重視するか）
beta = 0.1#突然変異発生率
map = np.zeros((7, 6))
Q_table = {}

def map_serial(nmap):
    out : int = 0
    for i in range(7):
        for j in range(6):
            out *= 3
            out += nmap[i,j]
    if str(out) in Q_table:
        nmap
    else:
        Q_table[str(out)] = np.array([0,0,0,0,0,0,0])
    return str(out)

def map_GUI(nmap):
    print(' 0123456 ')
    for j in reversed(range(6)):
        print('|',end='')
        for i in range(7):
            if nmap[i,j] == 1:
                print('o',end='')
            elif nmap[i,j] == 2:
                print('x',end='')
            else:
                print(' ',end='')
        print('|')
    print('---------')

def capable_search(nowmap):
    path = []
    for i in range(7):
        if nowmap[i,5] == 0:
            path.append(i)
    return path

def enemy_action(nowmap):
    path = capable_search(nowmap)
    
    for i in path:
        lmap = nowmap.copy()
        lmap = put(lmap,i,1)
        if result_judge(lmap) != 0:
            path = [i]
            break
    for i in path:
        lmap = nowmap.copy()
        lmap = put(lmap,i,2)
        if result_judge(lmap) != 0:
            path = [i]
            break
    return np.random.choice(path)

def put(nowmap,action,player):
    for i in range(6):
        if nowmap[action,i] == 0:
            nowmap[action,i] = player
            break
    return nowmap

def result_judge(nowmap):
    #縦列
    player = 0
    count = 0
    judge = 0
    for i in range(7):
        count = 0
        for j in range(6):
            if nowmap[i,j] == 0:
                count = 0
            elif nowmap[i,j] == player:
                count += 1
            else:
                player = nowmap[i,j]
                count = 1
            if count == 4:
                judge = player
                break
    #横列
    player = 0
    count = 0
    for j in range(6):
        count = 0
        for i in range(7):
            if nowmap[i,j] == 0:
                count = 0
            elif nowmap[i,j] == player:
                count += 1
            else:
                player = nowmap[i,j]
                count = 1
            if count == 4:
                judge = player
                break
            
    return judge

win = 0
for i in tqdm(range(1000)):
    #ゲーム初期化
    judge = 0
    map = np.zeros((7, 6))
    #ゲームは21手で終わる
    for j in range(21):
        origin_map = map_serial(map)
        #打てる手の検索
        hit = -1
        path = capable_search(map)
        #勝ち手、負け手を先に探しておく
        choice = 0
        for k in path:
            lmap = map.copy()
            lmap = put(lmap,k,1)
            if result_judge(lmap) != 0:
                hit = k
                choice = 1
                break
        for k in path:
            lmap = map.copy()
            lmap = put(lmap,k,2)
            if result_judge(lmap) != 0:
                hit = k
                choice = 2
                break
        #低確率で完全ランダム、高確率で現状最大価値手
        if hit == -1 and random.random() <= beta:
            #ランダムに打ち手を決める
            hit = np.random.choice(path)
            choice = 3
        elif hit == -1:
            acs = np.zeros(7)
            for f in path:
                acs[f] = 100000
            hit = np.argmax((Q_table[map_serial(map)]+acs))
            choice = 4
        
        map = put(map,hit,1)
        
        #デバック用表示プログラム
        #map_GUI(map)
        #print('hit = ',end='')
        #print(hit,end='')
        #print(' choice is ',end='')
        #if choice == 1:
        #    print('to win')
        #elif choice == 2:
        #    print('to avoid defeat')
        #elif choice == 3:
        #    print('random')
        #elif choice == 4:
        #    print('Q_learning')


        #勝利確認
        judge = result_judge(map)
        if judge == 0:
            #敵の打ち手を決める
            ene_hit = enemy_action(map)
            map = put(map,ene_hit,2)
            #敗北確認
            judge = result_judge(map)
        #Q値更新
        r = 0
        if judge == 1:
            r = 100
            win += 1
        elif judge == 2:
            r = -100
        next_map : str = map_serial(map)
        max = np.amax(Q_table[next_map])
        Q_table[origin_map][hit] = Q_table[origin_map][hit] + alpha*(gamma * max - Q_table[origin_map][hit] + r)
        #勝負が終わってないならループ、マップ更新
        #map_GUI(map)
        if r != 0:   
            break
    if i%100 == 0:
        print('試行',end='')
        print(i+1,end='')
        print('回目、勝率',end='')
        print((float(win)/float(100)*100),end='')
        print('%')
        win = 0
    if i %1000 == 999:
        map_GUI(map)
#できたQテーブルを出力