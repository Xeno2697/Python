import numpy as np
import matplotlib.pyplot as plt
import math
fig = plt.figure()
ax = fig.add_subplot(121)
x = np.linspace(0, 80, 200) #等間隔でデータを０から２０まで20個作成
y = np.linspace(0, 80, 200) #等間隔でデータを０から２０まで20個作成
x, y = np.meshgrid(x, y)  #ｘとｙからメッシュグリッドを作成
def fz(x, y):       #高さデータｚを作る関数fzを定義
    return np.clip(a = np.cos((x-40)*1.5/30)-y/90,a_min=0,a_max=100)
z = fz(x, y)        #関数fzを呼び出し高さデータｚを作成.

#ax = plt.contour(x,y,z,colors='black')    #等高線表示
#ax.clabel(fmt='%1.1f', fontsize=16)       #等高線の値を表示
plt.legend()
ax = plt.contourf(x,y,z,cmap='Blues',levels=20)   #等高線レベルに応じて色を塗る
ax2 = fig.add_subplot(122, projection="3d")
ax2.set_title("surface")
ax2.plot_surface(x, y, z)
#ax = plt.colorbar(label="height")  #カラーバー表示
plt.show()