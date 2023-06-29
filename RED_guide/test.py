import time
import compute_sample as cs

start = time.time()
result = cs.compute(10000,10000)

end = time.time()
print(result)
print("The time takes is {}".format(end-start))