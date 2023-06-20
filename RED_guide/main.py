import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import collections
import matplotlib.patches as pat
import numpy as np
from field import Field
from world import World

MAP_SIZE = 80
RED_NUM = 30
RED_POS_X = 20.0
RED_POS_Y = 30.0
CONTAINER_POS_X = RED_POS_X
CONTAINER_POS_Y = RED_POS_Y
CONTAINER_CAPABLE_DISTANCE = 1.0
NUM_TO_TRANSPORT = 1 #押し出すのに何台要るか
RED_MOVE_Alpha = 1.0
UWB_DISTANCE_MAX = 10.0
UWB_DISTANCE_MIN = 0.5

BLOOD_BLEEDING = 50 #新規領域開拓時の引き寄せ力
BLOOD_CURE = 0.2
BLOOD_SKINNY = 0.1
BLOOD_FAT = 0.3

#メモ
#
#道の運搬適切度＝血の流れやすさ＝Pathの「太さ」
#未探査率 ＝ 出血量 ＝ 引き込み圧力
#道幅増減 ＝ ｛通過血液量-過去の道幅×減少定数｝×時間経過
#運搬路＝血が多く通う道＝Pathがもっとも太い

#今後やるべきこと
#コンテナと、その自発移動
#地形に走りやすさ、障害物の設置
#Path太さ導入
#走りやすさを、通ったREDが評価するシステム
#アンカー指示がないなったREDがPath巡回するシステム
 
                  
redlist = World(RED_NUM)
logimap = Field(MAP_SIZE)
ims = []
fig = plt.figure(figsize=(6, 6), dpi=100)
ax = fig.add_subplot(aspect='1')
logimap.obstacle_set(50,50,5)
logimap.obstacle_set(10,40,5)
logimap.obstacle_set(30,20,5)
logimap.obstacle_set(25,60,5)
logimap.obstacle_set(0,0,5)
logimap.obstacle_set(70,0,5)
for i in range(logimap.obstacles.shape[0]):
    ax.add_patch(pat.Circle(xy = (logimap.obstacles[i,0], logimap.obstacles[i,1]), radius = logimap.obstacles[i,2], fill = True, color = 'black'))
ax.contourf(logimap.x,logimap.y,logimap.z,cmap='Blues',levels=20)
#シミュレーションターン数
for i in range(10000):
    #全ユニット行動
    rnd = i%1000
    if(rnd == 0):
        redlist.restart()
    elif(rnd < 350):
        #拡散、探索モード
        redlist.action(logimap,0)
    elif(rnd < 370):
        #タスク割り振りモード
        redlist.action(logimap,1)
    #elif(i == 250):
    #    redlist.path.reset()
    elif(rnd < 800):
        #コンテナ移動
        redlist.action(logimap,2)
        if(redlist.capacity_check()):
            redlist.container.move(redlist.container_search())
    elif(rnd < 1000):
        #全アンカー集合
        redlist.action(logimap,3)
    if(i%300==0):
        xy = []
        anker_bool = []
        number_to_road = []
        blood_vectol = []
        for j in range(redlist.n):
            xy.append(redlist.list[j].position)
            anker_bool.append(redlist.list[j].anker)
            number_to_road.append(redlist.list[j].number_to_road)
            blood_vectol.append(redlist.list[j].anker_vectol)
        xy = np.array(xy)
        blood_vectol=np.array(blood_vectol)
        number_to_road = np.array(number_to_road)
        xy_anker = xy[anker_bool]
        blood_vectol = blood_vectol[anker_bool] 
        number_to_road = number_to_road[anker_bool]
        xy = xy[np.logical_not(anker_bool)]
        line = []
        width = []
        for j in range(redlist.n):
            for k in range(redlist.n - j-1):
                if(redlist.path.connect[j][j+k+1]):
                    a = redlist.list[j].position
                    b = redlist.list[j+k+1].position
                    line.append([a,b])
                    width.append(redlist.path.size[j,j+k+1] * 0.1 + 1)
        lc = collections.LineCollection(line, linewidths = width, color = (0.0,1.0,0.0,0.1))
        blood_norm = np.linalg.norm(blood_vectol, axis=1, ord=2)
        blood_norm += 0.001
        ims.append([
                    plt.scatter(xy[:,0],xy[:,1],c="red"),
                    plt.scatter(xy_anker[:,0],xy_anker[:,1],c = number_to_road, cmap="rainbow"),
                    ax.add_collection(lc),
                    plt.quiver(xy_anker[:,0], xy_anker[:,1], blood_vectol[:,0]/blood_norm*30, blood_vectol[:,1]/blood_norm*30, blood_norm, cmap='Reds', angles='xy',scale_units='xy', scale=8.0),
                    plt.scatter(redlist.container.position[0],redlist.container.position[1],c="black", s= 200),
                    ])#,ax.imshow(logimap.map)])
        print(i)
plt.xlim(0,MAP_SIZE)
plt.ylim(0,MAP_SIZE)
ani = animation.ArtistAnimation(fig, ims, interval=100.0)
print("saving...")
plt.show()
ani.save('sample.gif', writer="pillow")
print("done.")