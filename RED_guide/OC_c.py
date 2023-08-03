#! /usr/bin/env python3
# coding: utf-8
import sys
import socket
import time
import cv2

## UDP送信クラス
class udpsend():
    def __init__(self):

        SrcIP = "192.168.1.233"                             # 送信元IP
        SrcPort = 22                                # 送信元ポート番号
        self.SrcAddr = (SrcIP,SrcPort)                  # アドレスをtupleに格納

        DstIP = "192.168.1.110"                             # 宛先IP
        DstPort = 22                                 # 宛先ポート番号
        self.DstAddr = (DstIP,DstPort)                  # アドレスをtupleに格納

        self.udpClntSock = socket(AF_INET, SOCK_DGRAM)  # ソケット作成
        self.udpClntSock.bind(self.SrcAddr)             # 送信元アドレスでバインド

    def send(self,data):
        data = data.encode('utf-8')                     # バイナリに変換

        self.udpClntSock.sendto(data, self.DstAddr)     # 宛先アドレスに送信

def main():
    # UDP受信用のソケット
    HOST = ''       # ブロードキャストパケットなので空
    PORT = 50000    # 50000番固定
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(0.5)
    
    # search Broker IPAdress using UDP
    #while True:
        image = search()
        cv2.imshow("Camera", image)
        


def search():
    # UDP受信用のソケット
    HOST = ''       # ブロードキャストパケットなので空
    PORT = 50003    # 50003番固定
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(0.5)

    # アルゴリズムを起動命令をまつ
    while True:
        #print('Wait for Broker IP')
        # 受信したUDPパケットを解析
        try:
            message_raw, address = sock.recvfrom(1024)
            message = message_raw.decode('utf-8').rstrip('\n')
            return message
        except socket.timeout:
            continue

if __name__ == '__main__':
    main()