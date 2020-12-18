
# import numpy as np
#
# a_count = 0
# b_count = 0
#
# a = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# b = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#
# np.random.shuffle(a)
# np.random.shuffle(b)
#
# print(a)
# print(b)
#
# for i in range(100000):
#     c = i%10
#     while True:
#         if a[c] == 1:
#             a_count += 1
#             print("{} 调用 a方法".format(i))
#             break
#         elif b[c] == 1:
#             b_count += 1
#             print("{} 调用 b方法".format(i))
#             break
#         else:
#             c = c+1 if c <9 else 0
#
# print("a 调用次数 {}".format(a_count))
# print("b 调用次数 {}".format(b_count))

class A():
    pass

a = A()
b = A()
c = A()

d = []
d.append(b)
# d.append(a)
# d.append(a)
# print(d)
#
# d = [item for item in d if item !=a]
#
# print(d)
e= [a for _ in range(5)]
d.extend(e)
print(d)