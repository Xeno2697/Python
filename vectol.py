
"""
(2) 2つの点電荷(電気双極子)が作る静電場
"""

import numpy as np
import matplotlib.pyplot as plt

plt.figure()


LX, LY=2,2

gridwidth=0.2 
X, Y= np.meshgrid(np.arange(-LX, LX, gridwidth), np.arange(-LY, LY,gridwidth)) 

R = np.sqrt(X**2+Y**2)

#2つの点電荷の位置座標と電荷
X1,Y1=1.1,0
Q1=0.2
R1=np.sqrt((X-X1)**2+(Y-Y1)**2)
plt.plot(X1,Y1,'o',color='blue')

X2,Y2=-1.1,0
Q2=-0.2
R2=np.sqrt((X-X2)**2+(Y-Y2)**2)
plt.plot(X2,Y2,'o',color='blue')
##

#ベクトル関数の設定。2電荷分。
U = Q1*(X-X1)*(R1)+Q2*(X-X2)*(R2)
V = Q1*(Y-Y1)*(R1)+Q2*(Y-Y2)*(R2)

plt.quiver(X,Y,U,V,color='red',angles='xy',scale_units='xy', scale=6.5)


plt.xlim([-LX,LX])
plt.ylim([-LY,LY])

# グラフ描画
plt.grid()
plt.draw()
plt.show()
