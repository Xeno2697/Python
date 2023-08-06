from __future__ import print_function
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from RNNPB import RNNPB


class RMSLELoss(nn.Module):

    def __init__(self, epsilon=1e-5):
        super().__init__()
        self.mse_loss = nn.MSELoss()
        self.epsilon = epsilon

    def forward(self, y_pred, y_true):
        clamped_y_pred = torch.clamp(y_pred, min=0.)
        log_y_pred = torch.log1p(clamped_y_pred)
        log_y_true = torch.log1p(y_true)
        msle = self.mse_loss(log_y_pred, log_y_true)
        # ゼロ除算が生じないように小さな値を足す
        rmsle_loss = torch.sqrt(msle + self.epsilon)
        return rmsle_loss

if __name__ == '__main__':
    torch.autograd.set_detect_anomaly(True)
    # set ramdom seed to 0
    np.random.seed(0)
    torch.manual_seed(0)
    # load data and make training set
    data = torch.load('traindata.pt')
    input = Variable(torch.from_numpy(data[:, :, :-1]), requires_grad=False)#Exclude one at the end.
    
    target = Variable(torch.from_numpy(data[:, :, 1:].transpose(0,2,1)), requires_grad=False)#Exclude one at the start
    # build the model
    seq = RNNPB()
    seq.double()
    #seq.cuda()
    criterion = nn.MSELoss()
    # use LBFGS as optimizer since we can load the whole data to train
    optimizer = optim.LBFGS(seq.parameters(),lr=0.5,)

    print(list(seq.parameters()))
    #begin to train
    for i in range(500):
        print('STEP: ', i)
        def closure():
            optimizer.zero_grad()
            out = seq.forward(input)
            loss = criterion(out, target)
            print('loss:', loss.data.cpu().numpy())
            loss.backward()
            return loss
        optimizer.step(closure)

        # begin to predict
        #pred = seq.forward(input[:], GENERATE=True)
        # When you want to test with a single Parametric bias value
        pb = seq.pb.data
        print(pb)
        #seq.pb.data = pb[0].view(1, 2)
        #pred = seq.forward(input[0].resize(1, 99), GENERATE=True)
        #seq.pb.data=pb

        #y = pred.data.cpu().numpy()
        # draw the result
        #plt.cla()
        #plt.figure(figsize=(30, 10))
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

        #plt.show()
        #plt.savefig('results/predict%d.pdf' % i)
        #plt.close()
    #torch.save(data, open('traindata.pt', 'wb'))