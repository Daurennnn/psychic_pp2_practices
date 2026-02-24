import math
import random

degree = 100
print(degree / 180 * math.pi)

width_top, width_bottom, height = 5, 4, 2
print((width_bottom + width_top) / 2 * height)


arr = list(range(1, 20))
random.shuffle(arr)
print(arr)