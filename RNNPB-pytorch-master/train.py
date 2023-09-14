from __future__ import print_function
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from RNNPB import RNNPB

class RMSLELoss(nn.Module):

    def __init__(self, epsilon=1e-2):
        super().__init__()
        self.to("cuda")
        self.mse_loss = nn.MSELoss()
        self.epsilon = epsilon

    def forward(self, y_pred, y_true):
        clamped_y_pred = torch.clamp(y_pred, min=1e-12)
        log_y_pred = torch.log1p(clamped_y_pred)
        log_y_true = torch.log1p(torch.clamp(y_true, min=1e-12))
        msle = self.mse_loss(log_y_pred, log_y_true)
        # ゼロ除算が生じないように小さな値を足す
        rmsle_loss = torch.sqrt(msle + self.epsilon)
        return rmsle_loss

if __name__ == '__main__':
    
    torch.autograd.set_detect_anomaly(False)#TrueにするとNanエラー検出
    # set ramdom seed to 0
    np.random.seed(5)
    torch.manual_seed(5)
    # load data and make training set
    data = torch.load('traindata.pt')
    input = Variable(torch.from_numpy(data[:, :, :-1]), requires_grad=False)#Exclude one at the end.
    input.cuda()
    target = Variable(torch.from_numpy(data[:, :, 1:].transpose(0,2,1)), requires_grad=False)#Exclude one at the start
    # build the model
    try:
        seq = torch.load('model.pth')
    except:
        seq = RNNPB()
        seq.double()
        seq.cuda()
    #seq.cuda()
    criterion = RMSLELoss()
    criterion.cuda()
    # use LBFGS as optimizer since we can load the whole data to train
    optimizer = optim.LBFGS(seq.parameters(),lr=0.5)
    pb = np.zeros(100)
    print(list(seq.parameters()))
    #begin to train
    for i in range(10):
        print('STEP: ', i)
        def closure():
            optimizer.zero_grad()
            out = seq.forward(input)
            loss = criterion(out.cuda(), target.cuda())#アンダーフロー回避
            print('loss:', loss.data.cpu().numpy())
            loss.cuda().backward()
            return loss
        optimizer.step(closure)

        # begin to predict
        #pred = seq.forward(input[:], GENERATE=True)
        # When you want to test with a single Parametric bias value
        pb = seq.pb.data.cpu().numpy().copy()
        
        #seq.pb.data = pb[0].view(1, 2)
        #pred = seq.forward(input[0].resize(1, 99), GENERATE=True)
        #seq.pb.data=pb

        #y = pred.data.cpu().numpy()
        # draw the result
        #plt.cla()
        
        #plt.title('Predict future values for time sequences\n(Dashlines are true values)', fontsize=30)
        #plt.xlabel('x', fontsize=20)
        #plt.ylabel('y', fontsize=20)
        #plt.xticks(fontsize=20)
        #plt.yticks(fontsize=20)

        
        #plt.plot(np.arange(input.size(1)), y[0], 'r', linewidth=2.0)
        #plt.plot(np.arange(input.size(1)), y[1], 'g', linewidth=2.0)
        #plt.plot(np.arange(input.size(1)), y[2], 'b', linewidth=2.0)

        #plt.plot(np.arange(input.size(1)),target.data[0].numpy(),'r:',linewidth=2.0)
        #plt.plot(np.arange(input.size(1)), target.data[1].numpy(), 'g:',linewidth=2.0)
        #plt.plot(np.arange(input.size(1)), target.data[2].numpy(), 'b:',linewidth=2.0)

        
        #plt.savefig('results/predict%d.pdf' % i)
        #plt.close()
    print("normal")
    print(pb[:14,:])
    print("collision")
    print(pb[15:,:])
    plt.figure(figsize=(30, 10))
    plt.scatter(pb[:14,0],pb[:14,1],c="b")
    plt.scatter(pb[15:,0],pb[15:,1],c="r")
    plt.show()
    torch.save(seq, open('model.pth', 'wb'))