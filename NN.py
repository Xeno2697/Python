def forward_move(turn:float, forward:float):
    R = 0
    L = 0
    offset = 0.2
    max_duty = 0.7
    if(forward < offset and forward > -offset):
        if(turn > 0):
            R = int((-turn*70)*(abs(forward)-offset)*-70/offset)
            L = int(turn*70)
        else:
            R = int(-turn*70)
            L = int((turn*70)*(abs(forward)-offset)*-70/offset)
    else:
        if(turn > 0):
            R = int(((forward*0.7)-(turn*offset))*100)
            L = int((turn*(max_duty-offset) + forward)*100)
            if(L > max_duty*100):
                L = int(max_duty*100)
        else:
            R = int((-turn*(max_duty-offset) + forward)*100)
            if(R > max_duty*100):
                R = int(max_duty*100)
            L = int((forward*0.7)-(-turn*offset))*100
    #wheel RL
def P_rotate_move(degree, angle, forward):
    turn = degree - angle
    if(turn > 180):
        turn = (turn - 360)%360
    elif(turn < -180):
        turn = (turn + 360)%360
    turn /= 45
    if(turn > 1.0):
        turn = 1.0
    forward_move(turn,forward)