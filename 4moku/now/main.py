from board import board
from Qplayer import Qplayer
from easyAI import eAI
from tqdm import tqdm

class main:
    def __init__(self,X,Y,winnum) -> None:
        self.X = X
        self.Y = Y
        self.board = board(X,Y,winnum)
        self.Qplayer = Qplayer(self.board)
        self.easyai = eAI()
        return

    def start(self,time):
        qwin = 0
        ewin = 0

        for i in range(time):
            self.board.reset()
            for j in range((int)((self.X+self.Y)/2)):
                c = self.easyai.choice(self.board,False)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,False,1)
                    ewin += 1
                    break
                else:
                    self.board.push(c,1)
                c = self.Qplayer.choice(self.board,True)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,True,1)
                    qwin += 1
                    break
                else:
                    self.board.push(c,-1)

            self.board.reset()
            for j in range((int)((self.X+self.Y)/2)):
                c = self.Qplayer.choice(self.board,False)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,False,1)
                    qwin += 1
                    break
                else:
                    self.board.push(c,1)
                c = self.easyai.choice(self.board,True)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,True,1)
                    ewin += 1
                    break
                else:
                    self.board.push(c,-1)
            
            self.board.reset()
            for j in range((int)((self.X+self.Y)/2)):
                c = self.Qplayer.choice(self.board,False)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,False,1)
                    break
                else:
                    self.board.push(c,1)
                c = self.Qplayer.choice(self.board,True)
                if c>=10000:
                    self.Qplayer.learn(self.board,c%10000,True,1)
                    break
                else:
                    self.board.push(c,-1)
            self.board.print()
        
        print("EasyAI win ",end="")
        print(ewin)
        print("Qlearning win ",end="")
        print(qwin)
        return