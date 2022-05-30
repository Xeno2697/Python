from array import array
from operator import truediv
from tkinter import END
import numpy as np

#自駒は１、敵駒は２

gamma = 0.9#割引率（数手後の報酬の減少係数）
alpha = 0.1#学習率（今回の試行の結果を今までに対してどの程度重視するか）
beta = 0.1#突然変異発生率
map = np.array(np.zeros([7,6]))
Q_table = {"apple":1}

def map_serial(map):
    out : int = 0
    for i in range(7):
        for j in range(6):
            out *= 3
            out += map[i][j]
    if str(out) in Q_table:
        map
    else:
        Q_table[str(out)] = np.array([0,0,0,0,0,0,0])
    return str(out)

def capable_search(nowmap):
    path = []
    for i in range(7):
        if nowmap(i,5) == 0:
            path.append(i)
    return path

def enemy_action(nowmap):
    path = capable_search(nowmap)
    for i in path:
        map = put(nowmap,i,2)
        if result_judge(map) != 0:
            path = [i]
            break
    return np.random.choice(path)

def put(nowmap,action,player):
    for i in range(7):
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
    judge = 0
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
for i in range(100):
    #ゲーム初期化
    judge = 0
    map = np.zeros(7)
    #ゲームは21手で終わる
    for j in range(21):
        origin_map = map_serial(map)
        #打てる手の検索
        path = capable_search(map)
        #低確率で完全ランダム、高確率で現状最大価値手
        if np.random.rand() <= beta:
            #ランダムに打ち手を決める
            hit = np.random.choice(path)
        else:
            hit = np.argmax(Q_table[map])
        map = put(map,hit,1)
        
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
        Q_table[origin_map][hit] = Q_table[origin_map][hit] + alpha*(gamma*np.amax[Q_table[map_serial(map)]] - Q_table[origin_map][hit] + r)
        #勝負が終わってないならループ、マップ更新
        if r != 0:
            
            break
    if i%10 == 0:
        print('試行',end='')
        print(i,end='')
        print('回目、勝率',end='')
        print((win/i),end='')
        print('%')
#できたQテーブルを出力