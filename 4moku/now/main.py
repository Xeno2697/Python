from board import board
from Qplayer import Qplayer
from easyAI import eAI
from tqdm import tqdm
import keyboard

class main:
    def __init__(self,X,Y,winnum) -> None:
        self.X = X
        self.Y = Y
        self.board = board(X,Y,winnum)
        self.Qplayer = Qplayer(self.board,0.45,0.90,0.05)
        self.easyai = eAI()

        return

    def start(self,time):
        qwin = 0
        ewin = 0
        win1 = 0
        win2 = 0
        print("To cancel, please push [c + ctrl] key ")
        try:
          for i in tqdm(range(time)):
            #EvsQ
            self.board.reset()
            for j in range((int)((self.X*self.Y)/2)):
                c = self.easyai.choice(self.board,False)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,False,1)
                    ewin += 1
                    break
                else:
                    self.Qplayer.learn(self.board,c%10000,False,0)
                    self.board.push(c,1)
                
                c = self.Qplayer.choice(self.board,True)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,True,1)
                    qwin += 1
                    break
                else:
                    self.Qplayer.learn(self.board,c%10000,True,0)
                    self.board.push(c,-1)

            #QvsE
            self.board.reset()
            for j in range((int)((self.X*self.Y)/2)):
                c = self.Qplayer.choice(self.board,False)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,False,1)
                    qwin += 1
                    break
                else:
                    self.Qplayer.learn(self.board,c%10000,False,0)
                    self.board.push(c,1)

                c = self.easyai.choice(self.board,True)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,True,1)
                    ewin += 1
                    break
                else:
                    self.Qplayer.learn(self.board,c%10000,True,0)
                    self.board.push(c,-1)
            
            #QvsQ
            self.board.reset()
            for j in range(int((self.X*self.Y)/2)):
                c = self.Qplayer.choice(self.board,False)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,False,1)
                    break
                else:
                    self.Qplayer.learn(self.board,c,False,0)
                    self.board.push(c,1)
                
                c = self.Qplayer.choice(self.board,True)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,True,1)
                    break
                else:
                    self.Qplayer.learn(self.board,c,True,0)
                    self.board.push(c,-1)
            #self.board.print()
            #times = 1000
            #if i % times == times-1:
            #    print(i+1,end="")
            #    print("_",end="")
            #    print((qwin-win1)*100/(ewin-win2+qwin-win1),end="")
            #    print("%")
            #    win1 = qwin
            #    win2 = ewin
        except KeyboardInterrupt:
            print("canceled because pushed [c+ctrl] key")
            print("please wait for writing... Don't Eleminate")
            self.Qplayer.csv_write()
            return
        
        print("EasyAI win ",end="")
        print(ewin)
        print("Qlearning win ",end="")
        print(qwin)

        self.Qplayer.csv_write()
        return