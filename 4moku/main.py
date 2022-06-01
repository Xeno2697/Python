import numpy as np
from board import board as bd

#自駒は１、敵駒は２

gamma = 0.9#割引率（数手後の報酬の減少係数）
alpha = 0.2#学習率（今回の試行の結果を今までに対してどの程度重視するか）
beta = 0.1#突然変異発生率

