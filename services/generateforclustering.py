from Clustering import Clustering
import random
import time
import matplotlib.pyplot as plt 
from tqdm import tqdm

# import matplotlib.pyplot as plt
timet = []
deliveries = []
for p in tqdm(range(1,51)):
    no_of_riders = p
    no_of_deliveries = p*20
    deliveries.append(no_of_deliveries)
    item_lat_long = []
    item_dims = []
    riders_vol = []

    for i in range(no_of_deliveries):
        lat = random.uniform(1,30)
        long = random.uniform(50,100)

        item_lat_long.append((lat,long))

    for i in range(no_of_deliveries):
        l = random.uniform(10,20)
        b = random.uniform(10,20)
        h = random.uniform(10,20)
        item_dims.append((l,b,h))

    for i in range(no_of_riders):
        riders_vol.append(random.uniform(75000,400000))


    cluster = Clustering(item_dims,item_lat_long,no_of_riders,riders_vol)
    start_time = time.time()
    temp = cluster.distribute()
    print(temp)
    diff_time = time.time()-start_time
    timet.append(diff_time)
    
print(timet)
plt.ylabel("Time taken to distribute deliveries to riders")
plt.xlabel("Number of deliveries")
plt.title("Time vs no. of deliveries")
plt.plot(deliveries,timet)
plt.show()