from operator import truediv
from tkinter import END
import numpy as np
gamma = 0.9#割引率（数手後の報酬の減少係数）
alpha = 0.1#学習率（今回の試行の結果を今までに対してどの程度重視するか）
map = np.array(np.zeros([9,9]))
Q_table = {map:range(7)}

def capable_search(nowmap):
    path = []
    for i in range(7):
        if nowmap(i,5) == 0:
            path.append(i)
    return path

def enemy_action(nowmap):
    path = capable_search(nowmap)
    return True

def put(nowmap,action,player):
    for i in range(7):
        if nowmap[action,i] != 0:
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

for i in range(1):
    #ゲーム初期化
    judge = 0
    map = np.zeros(7)
    #ゲームは21手で終わる
    for j in range(21):
        #打てる手の検索
        path = capable_search(map)
        #ランダムに打ち手を決める
        hit = np.random.choice(path)
        map = put(map,hit)
        #勝利確認
        judge = result_judge(map)
        if judge != 0:
            break
        #敵の打ち手を決める
        hit = enemy_action(map)
        #敗北確認
        #Q値更新
        #勝負が終わってないならループ
print("dsa")
#できたQテーブルを出力
