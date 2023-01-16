from Clustering import Clustering
import random
import time
import matplotlib.pyplot as plt 

# import matplotlib.pyplot as plt

no_of_riders = 5
no_of_deliveries = 10000

item_lat_long = []
item_dims = []
riders_vol = []

# x = []
# y = []
for i in range(no_of_deliveries):
    lat = random.uniform(1,30)
    long = random.uniform(50,100)
    # x.append(lat)
    # y.append(long)
    item_lat_long.append((lat,long))

for i in range(no_of_deliveries):
    l = random.uniform(10,20)
    b = random.uniform(10,20)
    h = random.uniform(10,20)
    item_dims.append((l,b,h))

for i in range(no_of_riders):
    riders_vol.append(random.uniform(75000,400000))


cluster = Clustering(item_dims,item_lat_long,no_of_riders,riders_vol)


# index = []
# x1 = []
# y1 = []
# for i in range(no_of_riders):
#             while True:
#                 a = random.randint(0,len(item_lat_long)-1)
#                 if a not in index:
#                     x1.append( item_lat_long[a][0])
#                     y1.append(item_lat_long[a][1])
#                     break

# plt.scatter(x,y)
# plt.scatter(x1,y1)
# plt.show()
start_time = time.time()
temp = cluster.distribute()
print(temp)
print("Time taken: ",time.time()-start_time)

x = []
y = []
count = 0
# plt.scatter(x = 'latitude', y = 'longitude', c=no_of_riders, s=50, cmap='viridis')
for i in temp:
    for j in i:
        x.append(item_lat_long[j][0])
        y.append(item_lat_long[j][1])
        count+=1
    plt.scatter(x,y)
    x = []
    y = []

# plt.scatter(x = 'latitude', y = 'longitude', c=no_of_riders, s=50, cmap='viridis')
# plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5)
print("number of deliveries: ",count)
plt.show()