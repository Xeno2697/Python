#! /usr/bin/env python3
# coding: utf-8
import sys
import socket
import time
import pigpio
import MotorControl
import FloorLight
import DistanceSensor
import cv2
import FloorImage
import CameraCheck
import base64

CeilCamera_status, FloorCamera_status = CameraCheck.check_cameras()

class Wheel:
    __sec_per_deg = 1.12 / 360.0

    def __init__(self, gpio: pigpio.pi):
        self.__gpio = gpio
        self.__distance_sensor = DistanceSensor.DistanceSensor(self.__gpio)
        self.__left_motor = MotorControl.BD6231(self.__gpio, 27, 22)
        self.__right_motor = MotorControl.BD6231(self.__gpio, 19, 26)
        self.__find_obstacle_twice = False

    def set_duty_bias(self, left_bias: int, right_bias: int) -> None:
        self.__left_motor.set_duty_bias(left_bias)
        self.__right_motor.set_duty_bias(right_bias)

    def stop(self) -> None:
        self.__left_motor.break_rotation()
        self.__right_motor.break_rotation()
        self.__left_motor.stop_rotation()
        self.__right_motor.stop_rotation()

    def stop_gently(self) -> None:
        # DUTYが40 %くらいでほぼすすまないから一旦これくらいで
        for i in range(7, 3, -1):
            self.forward_pwm(i * 10)
            time.sleep(0.5)
        self.stop()

    def forward(self) -> None:
        self.__left_motor.backward_rotation()
        self.__right_motor.forward_rotation()

    def forward_pwm(self, duty: int):
        self.__left_motor.backward_rotation_pwm(duty)
        self.__right_motor.forward_rotation_pwm(duty)
        
    def custom_pwm(self, L,R):
        if(L>0):
            self.__left_motor.backward_rotation_pwm(L)
        elif(L==0):
            self.__left_motor.stop_rotation()
        else:
            self.__left_motor.forward_rotation_pwm(-L)
        if(R>0):
            self.__left_motor.forward_rotation_pwm(R)
        elif(L==0):
            self.__left_motor.stop_rotation()
        else:
            self.__left_motor.backward_rotation_pwm(-R)

    def forward_sec(self, seconds: float):
        loop_count = seconds / 0.1
        time_start = time.perf_counter()
        obstacle_flag = 0
        forward_time = 0
        for i in range(int(loop_count / 2)):
            try:
                # 障害物が無いか確認
                # 細かくループを刻むことで，擬似的にthreadingのような動作を行う
                self.__distance_sensor.obstacle_monitoring()
                self.forward()
                time.sleep(0.1)
            except DistanceSensor.FindObstacle:
                if not self.__find_obstacle_twice:
                    self.__find_obstacle_twice = True
                    continue
                print("Find obstacle!")
                time_end = time.perf_counter()
                forward_time = time_end - time_start
                obstacle_flag = 1
                self.__find_obstacle_twice = False
                self.stop_gently()
                """
                # ランダムで左か右を向く
                if random.random() < 0.5:
                    self.pivot_turn_left_deg(90)
                else:
                    self.pivot_turn_right_deg(90)
                    break
                # ここまで
                """

                # 少し戻す場合
                self.turn_right_sec(0.5)
                self.stop()
                self.turn_left_sec(0.5)
                self.stop()
                time.sleep(0.5)
                break
                # ここまで
        
        if obstacle_flag == 0:
            self.stop_gently()
            time_end = time.perf_counter()
            forward_time = time_end - time_start

        return obstacle_flag, forward_time

    def turn_right(self) -> None:
        self.__left_motor.stop_rotation()
        self.__right_motor.backward_rotation()

    def turn_right_sec(self, seconds: float) -> None:
        self.turn_left()
        time.sleep(seconds)
        self.stop()

    def turn_left(self) -> None:
        self.__left_motor.forward_rotation()
        self.__right_motor.stop_rotation()

    def turn_left_sec(self, seconds: float) -> None:
        self.turn_right()
        time.sleep(seconds)
        self.stop()

    def pivot_turn_right(self) -> None:
        self.__left_motor.backward_rotation()
        self.__right_motor.backward_rotation()

    def pivot_turn_right_sec(self, seconds: float) -> None:
        self.pivot_turn_left()
        time.sleep(seconds)
        self.stop()

    def pivot_turn_right_deg(self, degree: float) -> None:
        turn_time = degree * self.__sec_per_deg
        self.pivot_turn_left_sec(turn_time)

    def pivot_turn_left(self) -> None:
        self.__left_motor.forward_rotation()
        self.__right_motor.forward_rotation()

    def pivot_turn_left_sec(self, seconds: float) -> None:
        self.pivot_turn_right()
        time.sleep(seconds)
        self.stop()

    def pivot_turn_left_deg(self, degree: float) -> None:
        turn_time = degree * self.__sec_per_deg
        self.pivot_turn_right_sec(turn_time)

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

        self.udpClntSock.sendto(data, self.DstAddr)  

def main(wheel : Wheel):
    # UDP受信用のソケット
    HOST = ''       # ブロードキャストパケットなので空
    PORT = 50000    # 50000番固定
    camera = FloorImage.FloorImage()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(0.5)
    udp = udpsend()
    # search Broker IPAdress using UDP
    i = 0
    while True:
        Lx,Ly,Rx,Ry = search()
        wheel.custam_pwm(Ly,Ry)
        i+=1
        if(i > 1000):
            i=0
            floorCamera = cv2.VideoCapture(int(FloorCamera_status))
            isSucceed, frame = floorCamera.read()
            try:        
                Image = base64.b64encode(frame).decode('utf-8')
                udp.send(Image)
            except Exception as e:
                print("Upload error(image)")
                print(e)


def search():
    # UDP受信用のソケット
    HOST = ''       # ブロードキャストパケットなので空
    PORT = 50003    # 50003番固定
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(0.5)

    # アルゴリズムを起動命令をまつ
    while True:
        print('Wait for Broker IP')
        # 受信したUDPパケットを解析
        try:
            message_raw, address = sock.recvfrom(1024)
            message = message_raw.decode('utf-8').rstrip('\n')
            Lx = message.split('_')[0]
            Ly = message.split('_')[1]
            Rx = message.split('_')[2]
            Ry = message.split('_')[3]
            return Lx,Ly,Rx,Ry
        except socket.timeout:
            continue

if __name__ == '__main__':
    gpio = pigpio.pi()
    wheel = Wheel(gpio)
    main(wheel)