import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import collections
import matplotlib.patches as pat
import numpy as np
from field import Field
from world import World

MAP_SIZE = 80
RED_NUM = 60

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
 
                  
redlist = World(RED_NUM,MAP_SIZE)
ims = []
fig = plt.figure(figsize=(6, 6), dpi=120)
ax = fig.add_subplot(aspect='1')
for i in range(redlist.field.obstacles.shape[0]):
    ax.add_patch(pat.Circle(xy = (redlist.field.obstacles[i,0], redlist.field.obstacles[i,1]), radius = redlist.field.obstacles[i,2], fill = True, color = 'black'))
#ax.contourf(redlist.field.x,redlist.field.y,redlist.field.z,cmap='Blues',levels=20)
#シミュレーションターン数
for i in range(200):
    redlist.action(4)
    if(i%3==0):
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
        pathsizemax = 0.0
        for j in range(redlist.n):
            for k in range(redlist.n - j-1):
                if(redlist.path.connect[j][j+k+1]):
                    a = redlist.list[j].position
                    b = redlist.list[j+k+1].position
                    line.append([a,b])
                    width.append(redlist.path.size[j,j+k+1])
                    if(pathsizemax<redlist.path.size[j,j+k+1]):
                        pathsizemax = redlist.path.size[j,j+k+1]
        for j in range(len(width)):
            width[j] /= pathsizemax
            width[j] *= 10
        lc = collections.LineCollection(line, linewidths = width, color = (0.0,0.7,0.5,0.3))
        blood_norm = np.linalg.norm(blood_vectol, axis=1, ord=2)
        blood_norm += 0.001
        ims.append([
                    plt.scatter(xy[:,0],xy[:,1],c="red"),
                    plt.scatter(xy_anker[:,0],xy_anker[:,1],c = number_to_road, cmap="rainbow"),
                    ax.add_collection(lc),
                    plt.quiver(xy_anker[:,0], xy_anker[:,1], blood_vectol[:,0]/blood_norm*30, blood_vectol[:,1]/blood_norm*30, blood_norm, color='red', angles='xy',scale_units='xy', scale=8.0),
                    #plt.scatter(redlist.container.position[0],redlist.container.position[1],c="black", s= 200),
                    ])#,ax.imshow(redlist.field.map)])
        print(i)
plt.xlim(0,MAP_SIZE)
plt.ylim(0,MAP_SIZE)
ani = animation.ArtistAnimation(fig, ims, interval=100.0)
print("saving...")
plt.show()
#ani.save('sample.gif', writer="pillow")
print("done.")