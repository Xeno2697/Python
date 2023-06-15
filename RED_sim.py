import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import collections
import matplotlib.patches as pat
import numpy as np
import random
import math

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

class container:
    def __init__(self):
        self.position = np.array([CONTAINER_POS_X,CONTAINER_POS_Y])
        self.move_vectol = np.array((0.0,0.0))
        self.bool = True    
    def move(self,vectol):
        if(vectol is False):
            self.position += 0
        else:
            d = np.linalg.norm(vectol,ord=2)
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
        self.reducation = np.array([[0 for i in range(n)] for j in range(n)])
        self.toconnect(0,[1],[1])
        self.toconnect(1,[2],[0.4])
        self.toconnect(0,[2],[1])    
    def toconnect(self, a, b, l = [1.0],d = [0.0]):
        if(type(b) is int):
            b = np.array([b])
        n = 3
        if(len(b) < n):
            n = len(b)
        for i in range(n):
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
    def reset(self):
        self.connect = np.array([[False for i in range(self.n)] for j in range(self.n)])
        self.blood = np.zeros((self.n,self.n))
        self.size = np.zeros((self.n,self.n))
        #self.toconnect(0,[1],[1])
        #self.toconnect(1,[2],[1])
        #self.toconnect(0,[2],[1])
    def blood_regulation(self,i,inblood = 0.0):
        #流入量計算
        q = self.blood[:,i].sum()
        #流入量/パス数　＝パス流出量
        n = self.size[i,:].sum()
        #血液輸出
        self.blood[i,:] = ( q + inblood - 0.1) * self.size[i,:] / n
        #血管幅増減
        self.size[i,:] = np.abs(self.blood[i,:] - self.blood[:,i]) * BLOOD_FAT + ((1-(BLOOD_SKINNY+self.reducation[i,:])) * self.size[i,:])
        self.size[:,i] = np.abs(self.blood[i,:] - self.blood[:,i]) * BLOOD_FAT + ((1-(BLOOD_SKINNY+self.reducation[i,:])) * self.size[:,i])
class logicalmap:
    def __init__(self):
        self.obstacles = np.array([[0,0,0]])
        self.x = np.linspace(0, 80, 200) #等間隔でデータを０から２０まで20個作成
        self.y = np.linspace(0, 80, 200) #等間隔でデータを０から２０まで20個作成
        self.x, self.y = np.meshgrid(self.x, self.y)
        self.z = logicalmap.value(self.x,self.y)
    def obstacle_set(self,x,y,r):
        self.obstacles = np.append(self.obstacles, np.array([[x,y,r]]), axis=0) 
    def collision_judge(self,x,y):
        for i in self.obstacles:
            vec = np.array([x-i[0],y-i[1]])
            nor = np.linalg.norm(vec,ord=2)
            if(nor < i[2]):
                return True
        if(x < 0 or x > MAP_SIZE or y < 0 or y > MAP_SIZE):
            return True
        return False
    def value(x,y):
        return np.clip(a = np.cos((x-40)*1.5/30)-y/90,a_min=0,a_max=100)         
class RED: 
    def __init__(self,x,y):
        self.position = np.array((x,y),dtype=float)
        self.anker = False
        #収束用パラメータ
        self.number_to_goal = 0
        self.number_to_road = 0
        self.number_to_container = 0
        self.time = 0
        #拡散用パラメータ
        self.anker_inblood = 0.0 #負にするとREDが寄ってくる、正にすると離れる
        self.anker_vectol = np.array([0,0])
        self.move_vectol = np.array([1,0])
        
        self.back = False
        self.num = 0
    def change_to_mover(self):
        self.anker = False
        self.anker_inblood = 0.0
        self.anker_vectol = np.array([0,0])
        self.back = False
        self.num = 0
        self.number_to_goal = 0
        self.number_to_road = 0
        self.number_to_container = 0
        self.direction_reversal()
        self.forward()
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
            if(not logimap.collision_judge(next_pos[0],next_pos[1])):
                self.forward()
            else:
                self.direction_reversal()
                self.forward()
    def move_to_xy(self,x,y):
        vec = np.array([x,y]) - self.position
        dis = np.linalg.norm(vec,ord=2)
        angle = 0.0
        if(dis != 0):
            rad = math.atan2(vec[1], vec[0])
            self.rotate(rad)
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
    def restart(self):
        for i in range(self.n):
            self.list[i].number_to_goal = 0
            self.list[i].number_to_road = 0
            self.list[i].number_to_container = 0
            self.list[i].time = 0
            self.list[i].anker_inblood = 0.0
            self.list[i].back = False
            self.list[i].num = 0
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
            return np.zeros(2), np.zeros(2)
        if(marker_list is []):
            return np.zeros(2), np.zeros(2)
        elif(len(marker_list)>= 3):
            self.list[i].back = False
        return np.array(marker_list), vectol
    #運搬方向を返す(ノルムは不定)
    def container_search(self):
        goal = 100
        road = 10
        vec = np.zeros(2)
        for j in range(self.n):
            if(self.list[j].anker):
                d = self.list[j].position - self.container.position
                norm = np.linalg.norm(d,ord=2)
                if(norm < UWB_DISTANCE_MAX and goal > self.list[j].number_to_goal):
                    goal = self.list[j].number_to_goal
                    road = self.list[j].number_to_road
                    vec = d
                elif(norm < UWB_DISTANCE_MAX and goal == self.list[j].number_to_goal and self.list[j].number_to_goal <= road):
                    goal = self.list[j].number_to_goal
                    road = self.list[j].number_to_road
                    vec = d
        if(goal < 100):
            return vec
        else:
            return False
    #運搬できる台数が存在するか
    def capacity_check(self):
        num = 0
        for j in range(self.n):
            if(not self.list[j].anker):
                d = self.list[j].position - self.container.position
                norm = np.linalg.norm(d,ord=2)
                if(norm < UWB_DISTANCE_MAX):
                    num += 1
        return (num >= NUM_TO_TRANSPORT)
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
    """
    def return_vectol(self,i):
        vectol = np.zeros(2)
        j = self.path.blood[:,i].argmax()
        vectol = self.list[j].position - self.list[i].position
        d = np.linalg.norm(vectol,ord=2)
        if(d == 0):
            return np.zeros(2)
        vectol = vectol / d
        return vectol
    """
    def return_number(self,i):
        #運搬路にどの程度寄与してるか判定し、運送協力に向かうか、もしくはアンカーであるべきかどうか
        if(self.list[i].number_to_road > 0):
            if(self.list[i].number_to_road == 1):
                for j in range(self.n):
                    if(self.path.connect[i,j] == True):
                        if(self.list[j].number_to_road != 1):
                            #ルート近くのアンカーを2にする
                            self.list[j].number_to_road = 2
                f = self.path.size[i,:] * (((self.path.blood[i, :] - self.path.blood[:, i])>0.0))
                next_anker =  f.argmax()
                if(f[next_anker] > 0.0):
                    #次のルートアンカーを1にする
                    self.list[next_anker].number_to_road = 1
                else:
                    #自身は運搬路の終点である
                    #ゴールからの経由アンカー数を設定
                    self.list[i].number_to_goal = 1
            else:
                for j in range(self.n):
                    if(self.path.connect[i,j] == True):
                        if((self.list[j].number_to_road <= 0) or (self.list[j].number_to_road > self.list[i].number_to_road + 1 )):
                            #近くのアンカーより一つ上の値にセット
                            self.list[j].number_to_road = self.list[i].number_to_road + 1
        #コンテナまでの経由ノード数を取得
        if(self.list[i].number_to_goal >= 1):
            for j in range(self.n):
                if(self.path.connect[i,j] == True):
                    if((self.list[j].number_to_goal > self.list[i].number_to_goal + 1) or (self.list[j].number_to_goal == 0)):
                        self.list[j].number_to_goal = self.list[i].number_to_goal + 1
        
        elif(self.list[i].number_to_road == 0):
            vec = self.container.position - self.list[i].position
            nor = np.linalg.norm(vec,ord=2)
            if(nor < 2.5):
                #コンテナ近くのアンカーを1にする
                self.list[i].number_to_road = 1
            else:
                self.list[i].number_to_road = -1       
    #コンテナ付近では、出血に応じた量の造血を行い、貧血を治すと同時に、コンテナ中心とした流れを生み出す。
    def hematopoiesis(self,i):
        d = np.linalg.norm(self.list[i].position - self.container.position)
        if(d < 5.0):
            self.list[i].anker_inblood = -np.sum(self.path.blood[:,i]) * 0.4
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
        if(mode == 0):# 拡散モード
            for j in range(self.n):
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
                    self.judge_anker(j)
        elif(mode == 1):# 運搬準備モード
            #各アンカーに、番号を割り振る。
            for i in range(self.n):
                if(self.list[i].anker):
                    #アンカーは、帰り道を指し示す # この手法は曖昧、大雑把過ぎて、帰還行動の指針には不向き
                    #self.list[i].anker_vectol = self.return_vectol(i) * 10
                    #番号の決定
                    self.return_number(i)
                #else:
                    #ムーバーは、停止。
        elif(mode == 2):# 収束、運搬モード中の動作
            for i in range(self.n):
                if(self.list[i].anker):
                    #実装時には、ここには足軽から得た路線環境を得て、最悪の場合、道を断つ
                    #アンカーが、もう誰の足軽にも役立たないと考えられるとき、自身をアンカーから足軽に変える
                    #今回は、Way数から判定して
                    # いるが、この手法はデッドロックを誘発し、耐故障性が低いと考えられるため、今後検証が必要。
                    if(self.list[i].number_to_road > 2):
                        self.list[i].time += 1
                        if(self.list[i].time >= (8-self.list[i].number_to_road)*40):
                            self.path.disconnect(i)
                            self.list[i].change_to_mover()
                        #s = self.path.connect[i,:].sum()
                        #if(s <= 3):
                        #    if(self.list[i].time == 0):
                        #        self.list[i].time = 4
                        #    elif(self.list[i].time == 1):
                        #        self.list[i].anker = False
                        #        self.path.disconnect(i)
                        #    self.list[i].time -= 1
                else:
                    vec = self.container.position - self.list[i].position
                    dis = np.linalg.norm(vec, ord=2)
                    if(dis < UWB_DISTANCE_MAX):
                        self.list[i].move_to_xy(self.container.position[0],self.container.position[1])
                    else:
                        anker_list,vectol = self.search(i)
                        next_ank = 0
                        road = 100
                        goal = 0
                        if(anker_list.ndim == 2):
                            for j in anker_list[:,0]:
                                if(road > self.list[j].number_to_road):
                                    next_ank = j
                                    road = self.list[j].number_to_road
                                if(self.list[j].number_to_road == 1):
                                    if(goal < self.list[j].number_to_goal):
                                        next_ank = j
                                        goal = self.list[j].number_to_goal
                            self.list[i].move_to_xy(self.list[next_ank].position[0],self.list[next_ank].position[1])
        elif(mode == 3):
            #ゴールから遠い順に集合
            for i in range(self.n):
                if(self.list[i].anker):
                    if(self.list[i].number_to_goal >= 3):
                        self.list[i].time += 1
                        if(self.list[i].time >= (8 - self.list[i].number_to_goal)*40):
                            self.path.disconnect(i)
                            self.list[i].change_to_mover()
                else:
                    vec = self.container.position - self.list[i].position
                    dis = np.linalg.norm(vec, ord=2)
                    if(dis < UWB_DISTANCE_MAX):
                        self.list[i].move_to_xy(self.container.position[0],self.container.position[1])
                    else:
                        anker_list,vectol = self.search(i)
                        next_ank = 0
                        road = 100
                        goal = 0
                        if(anker_list.ndim == 2):
                            for j in anker_list[:,0]:
                                if(road > self.list[j].number_to_road):
                                    next_ank = j
                                    road = self.list[j].number_to_road
                                if(self.list[j].number_to_road == 1):
                                    if(goal < self.list[j].number_to_goal):
                                        next_ank = j
                                        goal = self.list[j].number_to_goal
                            self.list[i].move_to_xy(self.list[next_ank].position[0],self.list[next_ank].position[1])
                    
redlist = RED_list(RED_NUM)
logimap = logicalmap()
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
#シミュレーションターン数
for i in range(1000):
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
    elif(rnd < 700):
        #コンテナ移動
        redlist.action(logimap,2)
        if(redlist.capacity_check()):
            redlist.container.move(redlist.container_search())
    elif(rnd < 1000):
        #全アンカー集合
        redlist.action(logimap,3)
    if(i%100==0):
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
                    plt.contourf(logimap.x,logimap.y,logimap.z,cmap='Blues',levels=20)
                    ])#,ax.imshow(logimap.map)])
        print(i)
plt.xlim(0,MAP_SIZE)
plt.ylim(0,MAP_SIZE)
ani = animation.ArtistAnimation(fig, ims, interval=1000.0)
print("saving...")
plt.show()
#ani.save('sample.gif', writer="pillow")
print("done.")