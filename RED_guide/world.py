import numpy as np
import math

from container import Container
from field import Field
from red import Red
from path import Path

MAP_SIZE = 80
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
class World:
    def __init__(self,n,mapsize):
        self.n = n
        self.container = Container(CONTAINER_POS_X,CONTAINER_POS_Y)
        self.path = Path(n)
        self.field = Field(mapsize)
        self.field.set_wall(40,0,40,60)
        
        self.list = [0 for _ in range(n)]
        for i in range(n):
            self.list[i] = Red(RED_POS_X-1,RED_POS_Y-1)
        for i in [0,1,2]:
            self.list[i].mode = 1
        self.list[1].number_to_container = 1
        self.list[2].number_to_container = 1
        self.list[0].position[0] = RED_POS_X
        self.list[0].position[1] = RED_POS_Y
        self.list[1].position[0] = RED_POS_X+5
        self.list[1].position[1] = RED_POS_Y
        self.list[2].position[0] = RED_POS_X
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
    def search(self,i):#REDから見通し出来るかつ、通信可能距離に存在するアンカー情報DictのListを取得  
        vectol = np.zeros(2)
        marker_list = []
        for j in range(self.n):
            if(j == i):
                continue
            if(self.list[j].mode == 1):
                vec_pos = self.list[j].position - self.list[i].position
                distance = np.linalg.norm(vec_pos,ord=2)
                if(UWB_DISTANCE_MAX > distance):
                    fieldvalue = Field.value((self.list[i].position[0]-self.list[j].position[0])/2,(self.list[i].position[1]-self.list[j].position[1])/2)
                    blood = (self.path.blood[i][j]-self.path.blood[j][i])/2
                    marker_list.append({
                        'number' : j ,
                        'position_vectol' : vec_pos,
                        'distance' : distance,
                        'field_value' : fieldvalue,
                        'anker_vectol' : self.list[j].anker_vectol,
                        'blood' : blood,
                        'number_to_container' : self.list[j].number_to_container
                        })
                    if(self.list[j].anker_vectol[1] != math.nan):
                        vectol += self.list[j].anker_vectol
        if(vectol[1] == math.nan):
            return np.zeros(2), np.zeros(2)
        if(marker_list is []):
            return np.zeros(2), np.zeros(2)
        elif(len(marker_list)>= 3):
            self.list[i].back = False
        return marker_list
    def search_direction(self,data):#周りのアンカーベクトルから、自己進行方向を決める
        if(len(data)<3):
            return False
        n = 0
        vec_sum = np.zeros(2)
        for i in range(len(data)):
            if(data[i]['anker_vectol'][0] is not None):
                distance = data[i]['distance']
                anker_vectol = data[i]['anker_vectol']
                position_vectol = data[i]['position_vectol']
                naiseki = np.dot(anker_vectol,position_vectol)
                vec_sum += (anker_vectol+(position_vectol/distance*0.2))*0.1
                n += 1
        if(n == 0):
            return False
        return vec_sum/n  
    def container_search(self):#運搬方向を返す(ノルムは不定)
        goal = 100
        road = 10
        vec = np.zeros(2)
        for j in range(self.n):
            if(self.list[j].mode == 1):
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
    def capacity_check(self):#運搬できる台数が存在するか
        num = 0
        for j in range(self.n):
            if(not self.list[j].mode == 1):
                d = self.list[j].position - self.container.position
                norm = np.linalg.norm(d,ord=2)
                if(norm < UWB_DISTANCE_MAX):
                    num += 1
        return (num >= NUM_TO_TRANSPORT)
    def judge_anker(self,i):#アンカー探索結果から、アンカーになるか判断、およびアンカー変化プロセス
        marker_list =  self.search(i)
        n = len(marker_list)
        if(n >= 3):
            self.list[i].back = False
            distance = UWB_DISTANCE_MAX
            for j in range(n):
                if(distance > marker_list[j]['distance']):
                    distance = marker_list[j]['distance']
            if( distance > 5.0):
                self.list[i].mode = 1
                self.list[i].anker_inblood = -BLOOD_BLEEDING
                vec_sum = np.zeros(2)
                for j in range(n):
                    self.path.toconnect(i, [marker_list[j]['number']], [marker_list[j]['distance']], [0.0])
                    '''
                    distance = marker_list[j]['distance']
                    anker_vectol = marker_list[j]['anker_vectol']
                    position_vectol = marker_list[j]['position_vectol']
                    naiseki = np.dot(anker_vectol,position_vectol)
                    vec_sum += (anker_vectol+(-position_vectol/distance*0.5))*0.1
                self.list[i].anker_vectol = vec_sum/np.linalg.norm(vec_sum)
                '''
        elif(n <= 2):
            self.list[i].direction_reversal()
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
    def hematopoiesis(self,i): #コンテナ付近では、出血に応じた量の造血を行い、貧血を治すと同時に、コンテナ中心とした流れを生み出す。
        #d = np.linalg.norm(self.list[i].position - self.container.position)
        #if(d < 5.0):
        if(self.list[i].number_to_container == 0):
            self.list[i].anker_inblood = -np.sum(self.path.blood[:,i]) * 0.4  
    def virtual_container_control(self,i):
        if(self.list[i].number_to_container == 0):
            search_data = self.search(i)
            t = np.zeros(2)
            f = np.zeros(2)
            for i in range(len(search_data)):
                if(self.number_to_container > search_data[i]['number_to_container']+1):
                    self.number_to_container = search_data[i]['number_to_container']+1
                if(search_data[i]['anker_vectol'][0] is not None):
                    blood = search_data[i]['blood']
                    if(blood > 0):
                        t += blood * search_data[i]['position_vectol']/search_data[i]['distance']
    def vectol_blood(self,i):#血流ベクトル計算 
        blood = self.path.blood[i, :] - self.path.blood[:, i]
        vectol = np.zeros(2)
        for j in range(self.n):
            v = self.list[j].position - self.list[i].position
            no = np.linalg.norm(v,ord = 2)
            if(no != 0.0):
                vectol += v * blood[j] / no
        return vectol     
    def action(self,mode = 0):#毎ターンの行動
        """
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
        """
        if(mode == 4):
            for i in range(self.n):
                if(np.isnan(self.list[i].position[0])):
                    print("Error: position is NaN.")
                if(self.list[i].mode == 1):
                    #自身の番号、ベクトルを変化させる
                    data = self.search(i)
                    next_mode = self.list[i].action_anker(self.path, data)
                    if(next_mode == 2):
                        self.path.disconnect(i)
                    else:
                        self.hematopoiesis(i)
                        self.path.blood_regulation(i,self.list[i].anker_inblood)
                    #self.list[i].anker_vectol = self.vectol_blood(i)
                    #最後尾にいるかつ、周りにMoverがいないとき、Moverになる。
                elif(self.list[i].mode == 0):
                    data = self.search(i)
                    next_mode = self.list[i].action_mover(self.field, data)
                    if(next_mode == 1):
                        for j in range(len(data)):
                            self.path.toconnect(i, [data[j]['number']], [data[j]['distance']], [0.0])
                elif(self.list[i].mode == 2):
                    next_mode = self.list[i].action_returnee(self.field, self.search(i))