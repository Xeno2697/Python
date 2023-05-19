import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import collections
import matplotlib.patches as patches
import numpy as np
import random
import math

MAP_SIZE = 80
RED_NUM = 30
RED_POS_X = 20.0
RED_POS_Y = 30.0
CONTAINER_POS_X = RED_POS_X
CONTAINER_POS_Y = RED_POS_Y
RED_MOVE_Alpha = 1.0
UWB_DISTANCE_MAX = 10.0
UWB_DISTANCE_MIN = 0.5

BLOOD_BLEEDING = 50 #新規領域開拓時の引き寄せ力
BLOOD_CURE = 0.2
BLOOD_SKINNY = 0.2
BLOOD_FAT = 0.2

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

class container:
    def __init__(self):
        self.position = np.array([CONTAINER_POS_X,CONTAINER_POS_Y])
        self.move_vectol = np.array((0.0,0.0))
        self.bool = True
    
    def move(self,vectol):
        if(vectol is False):
            self.position += 0
        else:
            d = np.linalg.norm(vectol)
            if(d > 0.01):
                self.move_vectol = vectol/d
            else:
                self.move_vectol = np.zeros(2)
            self.position += self.move_vectol * 0.2
        
        
        
class blood_path:
    def __init__(self,n = RED_NUM):
        self.n = n
        self.connect = np.array([[False for i in range(n)] for j in range(n)])
        self.blood = np.zeros((n,n))
        self.size = np.zeros((n,n))
        self.toconnect(0,[1],[1])
        self.toconnect(1,[2],[1])
        self.toconnect(0,[2],[1])
        
    def toconnect(self, a, b, l = [1.0]):
        if(type(b) is int):
            b = np.array([b])
        for i in range(len(b)):
            self.connect[a,b[i]] = True
            self.connect[b[i],a] = True
            self.size[a,b[i]] = 1.0/l[i]
            self.size[b[i],a] = 1.0/l[i]       
    def disconnect(self,a):
        self.connect[a,:] = np.zeros(self.n)
        self.connect[:,a] = np.zeros(self.n)
        self.blood[a,:] = np.zeros(self.n)
        self.blood[:,a] = np.zeros(self.n)
        self.size[a,:] = np.zeros(self.n)
        self.size[:,a] = np.zeros(self.n)
    #血流調整、および血流ベクトル計算  
    def blood_regulation(self,i,inblood = 0.0):
        #流入量計算
        q = self.blood[:,i].sum()
        #流入量/パス数　＝パス流出量
        n = self.size[i,:].sum()
        #血液輸出
        self.blood[i,:] = ( q + inblood - 0.1) * self.size[i,:] / n
        #血管幅増減
        self.size[i,:] = np.abs(self.blood[i,:] - self.blood[:,i]) * BLOOD_FAT + ((1-BLOOD_SKINNY) * self.size[i,:])
        self.size[:,i] = np.abs(self.blood[i,:] - self.blood[:,i]) * BLOOD_FAT + ((1-BLOOD_SKINNY) * self.size[:,i])
  
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
        self.position = np.array((x,y),dtype=float)
        self.anker = False
        self.anker_number = 0
        self.anker_inblood = 0.0 #負にするとREDが寄ってくる、正にすると離れる
        self.anker_vectol = np.array([0,0])
        self.move_vectol = np.array([1,0])
        self.time = 0
        self.back = False
        self.num = 0
        
    def forward(self,power = 1.0):
        self.position += self.move_vectol * power
    def rotate(self, rad_abs):
        self.move_vectol = np.array([math.cos(rad_abs), math.sin(rad_abs)])
    def direction_reversal(self):
        self.back = True
        self.move_vectol *= -1
    def move_random(self,logimap:logicalmap, vectol = np.zeros(2), alpha = RED_MOVE_Alpha):
            if(random.random() < 0.4 and not self.back):
                dis = np.linalg.norm(vectol,ord=2)
                angle = 0.0
                if(dis == 0):
                    angle = (random.random()-0.5)*2.0*math.pi
                else:
                    rad = math.atan2(vectol[1], vectol[0])
                    angle = random.gauss(rad, math.pi/2*alpha)
                self.rotate(angle)
            
            next_pos = self.position + self.move_vectol
            i = round(next_pos[0])
            j = round(next_pos[1])
            if(logimap.map[i][j] == 0):
                self.forward()
            else:
                self.direction_reversal()
                self.forward()
                
class RED_list:
    def __init__(self,n):
        self.n = n
        self.container = container()
        self.path = blood_path(n)
        self.list = [0 for _ in range(n)]
        for i in range(n):
            self.list[i] = RED(RED_POS_X,RED_POS_Y)
        for i in [0,1,2]:
            self.list[i].anker = True
        self.list[1].anker_inblood = -BLOOD_BLEEDING
        self.list[1].position[0] = RED_POS_X+5
        self.list[2].position[1] = RED_POS_Y+5

    #REDから見通し出来るかつ、通信可能距離に存在するアンカーのリストを取得        
    def search(self,i):
        vectol = np.zeros(2)
        marker_list = []
        for j in range(self.n):
            if(self.list[j].anker):
                d = self.list[j].position - self.list[i].position
                norm = np.linalg.norm(d,ord=2)
                if(UWB_DISTANCE_MAX > norm):
                    self.list[j].num += 1
                    marker_list.append(np.array([ j , d , norm], dtype=object))
                    if(self.list[j].anker_vectol[1] != math.nan):
                        vectol += self.list[j].anker_vectol
        if(vectol[1] == math.nan):
            return np.zeros(1), np.zeros(2)
        return np.array(marker_list), vectol
    
    def container_search(self,pos = np.zeros(2)):
        vectol = np.array([0.0,0.0])
        for j in range(self.n):
            if(self.list[j].anker):
                d = self.list[j].position - pos
                norm = np.linalg.norm(d,ord=2)
                if(norm < UWB_DISTANCE_MAX and not math.isnan(self.list[j].anker_vectol[1]) and self.list[j].anker_number == 1):
                    d = np.linalg.norm(self.list[j].anker_vectol)
                    if(norm < 0.01):
                        return self.list[j].anker_vectol
                    if(d == 0.0):
                        return self.list[j].position - pos
                    else:
                        vectol += self.list[j].anker_vectol/norm
        d = np.linalg.norm(vectol,ord=2)
        if(d > 0):
            vectol /= d
            return vectol
        else:
            return False
    
    #アンカー探索結果から、アンカーになるか判断、およびアンカー変化プロセス
    def judge_anker(self,i):
        marker_list, vectol = self.search(i)
        n = marker_list.shape[0]
        if(n >= 3):
            self.list[i].back = False
            if( marker_list[:, 2].min() > 5.0):
                self.list[i].anker = True
                self.list[i].anker_inblood = -BLOOD_BLEEDING
                self.path.toconnect(i, marker_list[:,0].tolist(),marker_list[:,2].tolist())
        elif(n <= 2):
            self.list[i].direction_reversal()
        if(n <= 1):
            print("Error: no anker")
    def return_vectol(self,i):
        vectol = np.zeros(2)
        j = self.path.blood[i,:].argmax()
        vectol = self.list[j].position - self.list[i].position
        d = np.linalg.norm(vectol,ord=2)
        if(d == 0):
            return np.zeros(2)
        vectol = vectol / d
        return vectol
    def return_number(self,i):
        a = self.list[i].anker_number
        if(a > 0):
            if(a == 1):
                for j in range(self.n):
                    if(self.path.connect[i,j] == True):
                        if(self.list[j].anker_number == 0 or self.list[j].anker_number > 1):
                            self.list[j].anker_number = 2
                f = self.path.size[i,:] * (((self.path.blood[i, :] - self.path.blood[:, i])>0))
                next_anker =  f.argmax()
                if(f[next_anker] > 0.1):
                    self.list[next_anker].anker_number = 1
            else:
                for j in range(self.n):
                    if(self.path.connect[i,j] == True):
                        if(self.list[j].anker_number == 0 or self.list[j].anker_number > a+1):
                            self.list[j].anker_number = a+1
        else:
            if(i == 0):
                self.list[i].anker_number = 1          
    #コンテナ付近では、出血に応じた量の造血を行い、貧血を治すと同時に、コンテナ中心とした流れを生み出す。
    def hematopoiesis(self,i):
            if(i == 0):
                self.list[i].anker_inblood = -np.sum(self.path.blood[:,i])
    ##血流ベクトル計算  
    def vectol_blood(self,i):
        blood = self.path.blood[i, :] - self.path.blood[:, i]
        vectol = np.zeros(2)
        for j in range(self.n):
            v = self.list[j].position - self.list[i].position
            no = np.linalg.norm(v,ord = 2)
            if(no != 0.0):
                vectol += v * blood[j] / no
        return vectol
            
    #毎ターンの行動
    def action(self,logimap:logicalmap,mode = 0):
        if(mode == 0):
            #拡散モード
            for j in range(redlist.n):
                if(self.list[j].anker):
                    #距離照会数だけ、出血量の低下
                    if(self.list[j].anker_inblood < 0):
                        self.list[j].anker_inblood += self.list[j].num * 0.1 #+ BLOOD_CURE
                    self.list[j].num = 0
                    self.hematopoiesis(j)
                    self.path.blood_regulation(j,self.list[j].anker_inblood)
                    self.list[j].anker_vectol = self.vectol_blood(j)
                    #self.judge_patroler(j)
                else:
                    #アンカー探索と、血流ベクトル取得、移動、アンカー変化判定
                    anker_list,vectol = self.search(j)
                    self.list[j].move_random(logimap,vectol)
                    self.list[j].time += 1
                    self.judge_anker(j)
        elif(mode == 1):
            #探査から運搬モードへ切り替える際の初期設定。
            #各アンカーに、番号を割り振る。
            for i in range(redlist.n):
                if(self.list[i].anker):
                    #アンカーは、帰り道を指し示す
                    self.list[i].anker_vectol = self.return_vectol(i) * 10
                    #番号の決定
                    self.return_number(i)
                #else:
                    #ムーバーは、停止。
        elif(mode == 2):
            #運搬モード中の動作
            for i in range(redlist.n):
                if(self.list[i].anker):
                    #コンテナが近くにある、またはあったとき、行き先を指し示す
                    if(self.list[i].anker_number == 1):
                        vec = self.container.position - self.list[i].position
                        d = np.linalg.norm(vec, ord=2)
                        if(d < 10.0):
                            f = self.path.size[i,:] * ((self.path.blood[i, :] - self.path.blood[:, i]) > 0)
                            argmax = f.argmax()
                            if(f[argmax] > 0.1):
                                vec = self.list[argmax].position - self.list[i].position
                                self.list[i].anker_vectol = vec * 200
                            else:
                                self.list[i].anker_vectol = np.zeros(2)
                    elif(self.list[i].anker_number > 2):
                        #番号が大きい順に、切り替え
                        self.list[i].time += 1
                        if(self.list[i].time >0):
                            self.list[i].time = 0
                            self.list[i].anker = False
                            self.path.disconnect(i)
                else:
                    vec = self.container.position - self.list[i].position
                    dis = np.linalg.norm(vec, ord=2)
                    if(dis < UWB_DISTANCE_MAX):
                        self.list[i].move_random(logimap,vec,0.05)
                        return
                    else:
                        anker_list,vectol = self.search(i)
                        self.list[i].move_random(logimap,vectol,0.2)
                    return
        elif(mode == 3):
            for i in range(redlist.n):
                return
                    
redlist = RED_list(RED_NUM)
logimap = logicalmap()
logimap.map_set(MAP_SIZE+1 , MAP_SIZE+1)
ims = []
fig = plt.figure(figsize=(12, 12), dpi=120)
ax = fig.add_subplot(aspect='1')
#シミュレーションターン数
for i in range(500):
    #全ユニット行動
    rnd = i%500
    if(i < 200):
        #探索モード
        redlist.action(logimap,0)
    elif(i < 250):
        #タスク割り振りモード
        redlist.action(logimap,1)
    elif(i < 450):
        #コンテナ移動
        redlist.action(logimap,2)
        redlist.container.move(redlist.container_search(redlist.container.position))
    
    if(i%10== 0):
        xy = []
        anker_bool = []
        anker_number = []
        blood_vectol = []
        for j in range(redlist.n):
            xy.append(redlist.list[j].position)
            anker_bool.append(redlist.list[j].anker)
            anker_number.append(redlist.list[j].anker_number)
            blood_vectol.append(redlist.list[j].anker_vectol)
        xy = np.array(xy)
        blood_vectol=np.array(blood_vectol)
        anker_number = np.array(anker_number)
        xy_anker = xy[anker_bool]
        blood_vectol = blood_vectol[anker_bool] 
        anker_number = anker_number[anker_bool]
        xy = xy[np.logical_not(anker_bool)]
        line = []
        width = []
        for j in range(redlist.n):
            for k in range(redlist.n - j-1):
                if(redlist.path.connect[j][j+k+1]):
                    a = redlist.list[j].position
                    b = redlist.list[j+k+1].position
                    line.append([a,b])
                    width.append(redlist.path.size[j,j+k+1] * 0.1)
        lc = collections.LineCollection(line, linewidths = width, color = (0.0,1.0,0.0,0.2))
        blood_norm = np.linalg.norm(blood_vectol, axis=1, ord=2)
        ims.append([
                    plt.scatter(xy[:,0],xy[:,1],c="red"),
                    plt.scatter(xy_anker[:,0],xy_anker[:,1],c = anker_number, cmap="winter"),
                    ax.add_collection(lc),
                    plt.quiver(xy_anker[:,0], xy_anker[:,1], blood_vectol[:,0]/blood_norm*30, blood_vectol[:,1]/blood_norm*30, blood_norm, cmap='Reds', angles='xy',scale_units='xy', scale=8.0),
                    plt.scatter(redlist.container.position[0],redlist.container.position[1],c="yellow", s= 200)
                    ])#,ax.imshow(logimap.map)])
        print(i)
plt.xlim(0,MAP_SIZE)
plt.ylim(0,MAP_SIZE)
ani = animation.ArtistAnimation(fig, ims, interval=100.0)
ani.save('sample.gif', writer="pillow")
plt.show()
