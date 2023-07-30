import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import collections
import matplotlib.patches as pat
import numpy as np
from field import Field
from world import World
import tqdm

MAP_SIZE = 80
RED_NUM = 30
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
redlist.set_initial_anchor()
heatmap_value = np.zeros((MAP_SIZE,MAP_SIZE))

#redlist2 = World(RED_NUM,MAP_SIZE)

#シミュレーションターン数
def heatmap():
    for i in range(RED_NUM):
        x = redlist.list[i].position[0]
        y = redlist.list[i].position[1]
        x = round(x)
        y = round(y)
        if(x >= MAP_SIZE):
            x = MAP_SIZE-1
        if(y >= MAP_SIZE):
            y = MAP_SIZE-1
        heatmap_value[x,y] += 1
def rate_of_coverage():
    a = 0
    for i in range(MAP_SIZE):
        for j in range(MAP_SIZE):
            if(heatmap_value[i,j] > 0):
                a += 1
    return (a / MAP_SIZE / MAP_SIZE)

ims = []
fig = plt.figure(figsize=(12, 12), dpi=120)
ax = fig.add_subplot(221, aspect=1)
ax2 = fig.add_subplot(122)
ax3 = fig.add_subplot(223, aspect=1)
lines = [[(redlist.field.walls[i,1], redlist.field.walls[i,0]), (redlist.field.walls[i,3], redlist.field.walls[i,2])] for i in range(redlist.field.walls.shape[0])]
lc = collections.LineCollection(lines, linewidths=2)
plt.xlim(0,MAP_SIZE)
plt.ylim(0,MAP_SIZE)
ax.add_collection(lc)



def draw_red_behavior():
        xy = []
        anker_bool = []
        number_to_container = []
        blood_vectol = []
        for j in range(redlist.n):
            xy.append(redlist.list[j].position)
            anker_bool.append(redlist.list[j].mode == 1)
            number_to_container.append(redlist.list[j].number_to_container)
            blood_vectol.append(redlist.list[j].anker_vectol)
        xy = np.array(xy)
        blood_vectol=np.array(blood_vectol)
        number_to_container = np.array(number_to_container)
        xy_anker = xy[anker_bool]
        blood_vectol = blood_vectol[anker_bool] 
        number_to_container = number_to_container[anker_bool]
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
        lc = collections.LineCollection(line, linewidths = width, color = (0.0,0.5,0.2,0.2))
        blood_norm = np.linalg.norm(blood_vectol, axis=1, ord=2)
        blood_norm += 0.001
        return [
                ax.scatter(xy[:,0],xy[:,1],c="red"),
                ax.scatter(xy_anker[:,0],xy_anker[:,1],c = number_to_container,vmin=0, vmax=9, cmap="CMRmap"),
                ax.add_collection(lc)
                #plt.quiver(xy_anker[:,0], xy_anker[:,1], blood_vectol[:,0]/blood_norm*30, blood_vectol[:,1]/blood_norm*30, blood_norm, color='red', angles='xy',scale_units='xy', scale=8.0),
                #plt.scatter(redlist.container.position[0],redlist.container.position[1],c="black", s= 200),
                ]
def draw_heatmap():
    return [ax.pcolor(heatmap_value, cmap=plt.cm.BuGn, vmax = 20)]
rate = []

def fanc(i):
    if((i+1)%5 == 0):
        i = 1
    else:
        i = 0
    for j in range(80):
        redlist.action(4)
        heatmap()

    xy = []
    anker_bool = []
    number_to_container = []
    #blood_vectol = []
    vec = np.zeros(2)
    vec_pos = np.zeros(2)
    for j in range(redlist.n):
        xy.append(redlist.list[j].position)
        anker_bool.append(redlist.list[j].mode == 1)
        number_to_container.append(redlist.list[j].number_to_container)
        if(redlist.list[j].number_to_container == 0):
            vec = redlist.list[j].anker_vectol
            vec_pos = redlist.list[j].position
    #    blood_vectol.append(redlist.list[j].anker_vectol)
    xy = np.array(xy)
    #blood_vectol=np.array(blood_vectol)
    number_to_container = np.array(number_to_container)
    xy_anker = xy[anker_bool]
    #blood_vectol = blood_vectol[anker_bool] 
    number_to_container = number_to_container[anker_bool]
    xy = xy[np.logical_not(anker_bool)]
    #line = []
    #width = []
    #pathsizemax = 0.0
    #for j in range(redlist.n):
    #        for k in range(redlist.n - j-1):
    #            if(redlist.path.connect[j][j+k+1]):
    #                a = redlist.list[j].position
    #                b = redlist.list[j+k+1].position
    #                line.append([a,b])
    #                width.append(redlist.path.size[j,j+k+1])
    #                if(pathsizemax<redlist.path.size[j,j+k+1]):
    #                    pathsizemax = redlist.path.size[j,j+k+1]
    #for j in range(len(width)):
    #    width[j] /= pathsizemax
    #    width[j] *= 10
    #blood_norm = np.linalg.norm(blood_vectol, axis=1, ord=2)
    #blood_norm += 0.001
    
    ax.cla()
    ax2.cla()
    ax3.cla()
    
    ax.add_collection(lc)
    ax.set_xlim((0.0,float(MAP_SIZE)))
    ax.set_ylim((0.0,float(MAP_SIZE)))
    #ax3.add_collection(lc)
    ax3.pcolor(heatmap_value, cmap=plt.cm.gray, vmax = 20)
    #lcc = collections.LineCollection(line, linewidths = width, color = (0.0,0.5,0.2,0.2))
    #ax.quiver(xy_anker[:,1], xy_anker[:,0], blood_vectol[:,1]/blood_norm*30, blood_vectol[:,0]/blood_norm*30, blood_norm, color='red', angles='xy',scale_units='xy', scale=8.0)
    ax.quiver(vec_pos[1], vec_pos[0], vec[1], vec[0], color='red', angles='xy',scale_units='xy', scale=50)
    ax3.set_xlim((0.0,float(MAP_SIZE)))
    ax3.set_ylim((0.0,float(MAP_SIZE)))
    ax.scatter(xy[:,1],xy[:,0],c="green")
    ax.scatter(xy_anker[:,1],xy_anker[:,0],c = number_to_container,vmin=0, vmax=8, cmap="CMRmap")
    #ax.add_collection(lcc)
    ax3.plot(redlist.cont_path[:,1],redlist.cont_path[:,0],c = "red")
    
    
    x = np.linspace(0, len(rate), len(rate)+1)
    rate.append(rate_of_coverage())
    y = np.array(rate)
    ax2.plot(x,y,color="g")
    ax2.set_ylim((0.0,1.0))
    
    if(i == 1):
        redlist.virtual_container_control()

anim = animation.FuncAnimation(fig, fanc, frames = range(200), interval=1)
# gif 画像として保存する。
print("Saving...")
#anim.save("animation3.gif", writer="pillow")
plt.show()
anim.save('sample.gif', writer="pillow")

"""
for i in tqdm.tqdm(range(8000)):
    redlist.action(4)
    heatmap()
    if(i%450 == 400):
        redlist.virtual_container_control()
    if(i%40 == 0):
        ims.append(draw_red_behavior())


ani = animation.ArtistAnimation(fig, ims, interval=100.0)
print("showing...")
plt.show()
print("saving...")
ani.save('sample.gif', writer="pillow")
print("saved.")
"""