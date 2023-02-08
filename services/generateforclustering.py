from Clustering import Clustering
import random
import time
import matplotlib.pyplot as plt 
from tqdm import tqdm
from datetime import datetime,timedelta

# import matplotlib.pyplot as plt
timet = []
deliveries = []
# for p in tqdm(range(1,51)):
no_of_riders = 10
no_of_deliveries = 50*10
deliveries.append(no_of_deliveries)
item_lat_long = []
item_dims = []
riders_vol = []
edd = []

x = []
y = []
for i in range(no_of_deliveries):
    lat = random.uniform(1,30)
    long = random.uniform(50,100)
    x.append(lat)
    y.append(long)
    item_lat_long.append((lat,long))
    edd.append(str(datetime.now()+timedelta(days=random.randint(-3,3))))

for i in range(no_of_deliveries):
    l = random.uniform(10,20)
    b = random.uniform(10,20)
    h = random.uniform(10,20)
    item_dims.append((l,b,h))

for i in range(no_of_riders):
    riders_vol.append(random.uniform(75000,400000))


cluster = Clustering(item_dims,item_lat_long,no_of_riders,riders_vol,edd,(30,100))
values = cluster.distribute()

index = []
x1 = []
y1 = []
# for i in range(no_of_riders):
#     while True:
#         a = random.randint(0,len(item_lat_long)-1)
#         if a not in index:
#             x1.append( item_lat_long[a][0])
#             y1.append(item_lat_long[a][1])
#             break

for i in values:
    for j in i:
        x1.append(item_lat_long[j][0])
        y1.append(item_lat_long[j][1])
    plt.scatter(x1,y1)
    plt.xlabel('Latitude of delivery points')
    plt.ylabel('Longitude of delivery points')
    plt.title('Delivery points for each rider')
    x1 = []
    y1 = []

# plt.scatter(x,y)

plt.show()
    # start_time = time.time()
    # temp = cluster.distribute()
    # print(temp)
    # diff_time = time.time()-start_time
    # timet.append(diff_time)
    # print("Time taken: ",time.time()-start_time)

    # x = []
    # y = []
    # count = 0
    # # plt.scatter(x = 'latitude', y = 'longitude', c=no_of_riders, s=50, cmap='viridis')
    # for i in temp:
    #     for j in i:
    #         x.append(item_lat_long[j][0])
    #         y.append(item_lat_long[j][1])
    #         count+=1
    #     plt.scatter(x,y)
    #     x = []
    #     y = []

    # plt.scatter(x = 'latitude', y = 'longitude', c=no_of_riders, s=50, cmap='viridis')
    # plt.scatter(centers[:, 0], centers[:, 1], c='black', s=200, alpha=0.5)
    # print("number of deliveries: ",count)
    # plt.show()
# print(timet)
# plt.ylabel("Time taken to distribute deliveries to riders")
# plt.xlabel("Number of deliveries")
# plt.title("Time vs no. of deliveries")
# plt.plot(deliveries,timet)
# plt.show()