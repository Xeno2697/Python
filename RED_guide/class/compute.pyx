import numpy as np
def compute(loop_a, loop_b):
    result = 0
    for a in range(loop_a):
        for b in range(loop_b):
            result += 1
    return result