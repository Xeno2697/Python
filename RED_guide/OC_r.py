from socket import *
import pygame
from pygame.locals import *
import sys

import time
#Initialize JOYSTICK
pygame.init()
pygame.joystick.init()
joy = pygame.joystick.Joystick(0)
joy.init()
print("Number of Button : " + str(joy.get_numbuttons()))
print("Number of Axis : " + str(joy.get_numaxes()))
print("Number of Hats : " + str(joy.get_numhats()))

## UDP送信クラス
class udpsend():
    def __init__(self):

        SrcIP = "192.168.1.110"                             # 送信元IP
        SrcPort = 22                                # 送信元ポート番号
        self.SrcAddr = (SrcIP,SrcPort)                  # アドレスをtupleに格納

        DstIP = "192.168.1.233"                             # 宛先IP
        DstPort = 50003                                 # 宛先ポート番号
        self.DstAddr = (DstIP,DstPort)                  # アドレスをtupleに格納

        self.udpClntSock = socket(AF_INET, SOCK_DGRAM)  # ソケット作成
        self.udpClntSock.bind(self.SrcAddr)             # 送信元アドレスでバインド

    def send(self,data):
        data = data.encode('utf-8')                     # バイナリに変換

        self.udpClntSock.sendto(data, self.DstAddr)     # 宛先アドレスに送信

udp = udpsend()
while True:
    for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
    axLx = int(joy.get_axis(0)*70)
    axLy = int(-joy.get_axis(1)*70)
    axRx = int(joy.get_axis(2)*70)
    axRy = int(-joy.get_axis(3)*70)
    massage = str(axLx)+"_"+str(axLy)+"_"+str(axRx)+"_"+str(axRy)
    #print(str(axLx)+"_"+str(axLy)+"_"+str(axRx)+"_"+str(axRy))
    udp.send(massage)