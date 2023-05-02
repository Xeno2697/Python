import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import collections
import numpy as np
import random
import math

RED_NUM = 30
RED_POS_X = 20
RED_POS_Y = 30
RED_MOVE_Alpha = 1.5
UWB_DISTANCE_MAX = 10.0
UWB_DISTANCE_MIN = 0.5

BLOOD_BLEEDING = 50 #新規領域開拓時の引き寄せ力

line = [[(RED_POS_X,RED_POS_Y+5),(RED_POS_X+5,RED_POS_Y)],[(RED_POS_X,RED_POS_Y),(RED_POS_X,RED_POS_Y+5)],[(RED_POS_X+5,RED_POS_Y),(RED_POS_X,RED_POS_Y)]]

#メモ
#道の運搬適切度＝血の流れやすさ＝Pathの「太さ」
#運搬路＝血が多く通う道＝Pathがもっとも太い

#今後やるべきこと
#コンテナと、その自発移動
#地形に走りやすさ、障害物の設置
#Path太さ導入
#走りやすさを、通ったREDが評価するシステム
#アンカー指示がないなったREDがPath巡回するシステム

class logicalmap:
    def __init__(self):
        self.map = [0]
    def map_set(self,x,y):
        self.map = [[0]*x]*y
        for i in range(y):
            if(i == 0 or i == y-1):
                self.map[i] = [1]*x
            else:
                for j in [0,x-1]:
                    self.map[i][j] = 1
                    
class RED: 
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.anker = False
        self.anker_inblood = 0
        self.anker_vectol = (0,0)
        self.num = 0
        
        
    def move_random(self,logimap:logicalmap, vectol = (0,0)):
        while(True):
            dis = math.sqrt( vectol[0]**2 + vectol[1]**2 )
            
            if(dis < 0.00000005):
                angle = (random.random()-0.5)*2.0*math.pi
            else:
                rad = math.atan2(vectol[1], vectol[0])
                angle = random.gauss(rad, math.pi/2*RED_MOVE_Alpha)
            x_move = math.cos(angle)
            y_move = math.sin(angle)
            i = round(self.x+x_move)
            j = round(self.y+y_move)
            if(logimap.map[j][i] == 0):
                self.x += x_move * 1.0
                self.y += y_move * 1.0
                break
            else:
                break
        

class RED_list:
    def __init__(self,n):
        self.n = n
        self.list = [0 for _ in range(n)]
        self.path = [[False for i in range(n)] for j in range(n)]
        self.path_blood = [[0 for i in range(n)] for j in range(n)]
        for i in range(n):
            self.list[i] = RED(RED_POS_X,RED_POS_Y)
        for i in range(3):
            self.list[i].anker = True
        self.list[0].anker_inblood = 0.0
        self.list[1].x = RED_POS_X+5
        self.list[2].y = RED_POS_Y+5
        self.path[0][1] = True
        self.path[0][2] = True
        self.path[1][0] = True
        self.path[1][2] = True
        self.path[2][0] = True
        self.path[2][1] = True

            
    def search(self,i):
        x = self.list[i].x
        y = self.list[i].y
        vectol_x = 0.0
        vectol_y = 0.0
        vectol_d = 0.0
        marker_list = []
        for j in range(self.n):
            if(self.list[j].anker):
                x_d = x - self.list[j].x
                y_d = y - self.list[j].y
                dis = math.sqrt((x_d**2)+(y_d**2))
                if(UWB_DISTANCE_MAX > dis):
                    marker_list.append((j,dis,x_d,y_d))
                    self.list[j].num += 0.02
                    vectol_x += self.list[j].anker_vectol[0]
                    vectol_y += self.list[j].anker_vectol[1]
            if (len(marker_list) != 0):
                vectol_x /= len(marker_list)
                vectol_y /= len(marker_list)
        return marker_list, (vectol_x,vectol_y)
    
    #アンカー探索結果から、アンカーになるか判断、およびアンカー変化プロセス
    def judge_anker(self,i):
        marker_list,vectol = self.search(i)
        n = len(marker_list)
        if(n == 2):
            #for j in range(n):
            #    if(marker_list[j][1] < UWB_DISTANCE_MIN):
            #        return
            self.list[i].anker = True
            self.list[i].anker_inblood = -BLOOD_BLEEDING
            self.path[i][marker_list[0][0]] = True
            self.path[marker_list[0][0]][i] = True
            self.path[i][marker_list[1][0]] = True
            self.path[marker_list[1][0]][i] = True
            line.append([(self.list[i].x,self.list[i].y),(self.list[marker_list[0][0]].x,self.list[marker_list[0][0]].y)])
            line.append([(self.list[i].x,self.list[i].y),(self.list[marker_list[1][0]].x,self.list[marker_list[1][0]].y)])
            
    #コンテナ付近では、出血に応じた量の造血を行い、貧血を治すと同時に、コンテナ中心とした流れを生み出す。
    def hematopoiesis(self,i):
        if(i == 0):
            #流入量計算
            q = 0
            n = 0
            for j in range(self.n):
                q += self.path_blood[j][i]
            q = -q
            for j in range(self.n):
                if(self.path[i][j]):
                    n+=1
            self.list[i].anker_inblood = q
            q /= n
            for j in range(self.n):
                if(self.path[i][j]):
                    self.path_blood[i][j] = q * 0.99 #overflow抑止        
    
    #血流調整、および血流ベクトル計算  
    def blood_regulation(self,i):
        #流入量計算
        q = self.list[i].anker_inblood
        n = 0
        for j in range(self.n):
            q += self.path_blood[j][i]
        #流入量/パス数　＝パス流出量
        for j in range(self.n):
            if(self.path[i][j]):
                n+=1
        q /= n
        vectol_x = 0
        vectol_y = 0
        for j in range(self.n):
            if(self.path[i][j]):
                self.path_blood[i][j] = q * 0.99 #overflow抑止
                x = self.list[j].x - self.list[i].x
                y = self.list[j].y - self.list[i].y
                d = math.sqrt(x**2+y**2)
                vectol_x += x*(q-self.path_blood[j][i])/d
                vectol_y += y*(q-self.path_blood[j][i])/d
        return (vectol_x,vectol_y)
                
    #毎ターンの行動
    def action(self,logimap:logicalmap):
        for j in range(redlist.n):
            if(not self.list[j].anker):
                #アンカー探索と、血流ベクトル取得、移動、アンカー変化判定
                anker_list,vectol = self.search(j)
                self.list[j].move_random(logimap,vectol)
                self.judge_anker(j)
            else:
                #距離照会数だけ、出血量の低下
                self.list[j].anker_inblood += self.list[j].num + 0.1
                self.list[j].num = 0
                if(self.list[j].anker_inblood>0):
                    self.list[j].anker_inblood=0
                self.hematopoiesis(j)
                self.list[j].anker_vectol = self.blood_regulation(j)
                
                
                 

redlist = RED_list(RED_NUM)
logimap = logicalmap()
logimap.map_set(51,51)
ims = []
fig = plt.figure(figsize=(8, 8), dpi=120)
ax = fig.add_subplot(aspect='1')
#シミュレーションターン数
for i in range(100):
    #全ユニット行動
    redlist.action(logimap)
    
    #描画
    x = []
    y = []
    x_anker = []
    y_anker = []
    x_anker_blood = []
    y_anker_blood = []
    for j in range(redlist.n):
        if(not redlist.list[j].anker):
            x.append(redlist.list[j].x)
            y.append(redlist.list[j].y)
        else:
            x_anker.append(redlist.list[j].x)
            y_anker.append(redlist.list[j].y)
            x_anker_blood.append(redlist.list[j].anker_vectol[0])
            y_anker_blood.append(redlist.list[j].anker_vectol[1])
    X = np.array(x_anker)
    Y = np.array(y_anker)
    U = np.array(x_anker_blood)
    V = np.array(y_anker_blood)
    lc = collections.LineCollection(line)
    ims.append([plt.scatter(x,y,c="red"),
                plt.scatter(x_anker,y_anker,c = "blue"),
                ax.add_collection(lc),
                plt.quiver(X,Y,U,V,color=(1.0,0.0,0.0,0.2), angles='xy',scale_units='xy', scale=5.0)])#,ax.imshow(logimap.map)])
    print(i)
plt.xlim(0,50)
plt.ylim(0,50)
ani = animation.ArtistAnimation(fig, ims, interval=10.0)
#ani.save('sample.gif', writer="pillow")
plt.show()