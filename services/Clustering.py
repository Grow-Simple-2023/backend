from typing import List,Tuple
import random as rd
import math

def distance(origin, destination)->float:
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
        math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d
class Clustering:
    
    item_dims: List[Tuple[float]]
    item_lat_long: List[Tuple[float]]
    no_riders: int
    rider_vol: List[float]
    
    def __init__(self, item_dims: List[Tuple[float]], item_lat_long: List[Tuple[float]], no_riders: int, rider_vol: List[float]) -> None:
        assert len(item_dims)>0
        assert len(item_dims)==len(item_lat_long)
        assert len(item_dims[0])==3
        assert len(item_lat_long[0])==2
        assert no_riders<len(item_dims)
        
        self.item_dims = item_dims
        self.item_lat_long = item_lat_long
        self.no_riders = no_riders
        self.rider_vol = rider_vol
    
    def distribute(self) -> List[List[int]]:
        class Centroid:
            def __init__(self,centroid,points)->None:
                self.centroid = centroid
                self.points = points

        
        epochs = 500
        index = []
        centroids = []
        for i in range(self.no_riders):
            while True:
                a = rd.randint(0,len(self.item_lat_long)-1)
                if a not in index:
                    centroid = self.item_lat_long[a]
                    points = []
                    centroids.append(Centroid(centroid,points))
                    break
        
        # for i in centroids:
        #     print(i.centroid)
        #     print(i.points)
        for i in range(50):
            for centroid in range(len(centroids)):
                centroids[centroid].points = []
            
            for point in range(len(self.item_lat_long)):
                min_distance  = float('inf')
                centroid_index = 0
                for j in range(len(centroids)):
                    centroid = centroids[j].centroid
                    lat1 = self.item_lat_long[point][0]
                    lat2 = centroid[0]
                    lon1 = self.item_lat_long[point][1]
                    lon2 = centroid[1]
                    d = distance((lat1,lon1),(lat2,lon2))
                    # d = (lat1-lat2)**2+(lon1-lon2)**2
                    if d < min_distance:
                        centroid_index = j
                        min_distance = d
                centroids[centroid_index].points.append((point,self.item_lat_long[point]))
            
            for centroid in range(len(centroids)):
                lat = 0
                long = 0
                for point in centroids[centroid].points:
                    lat += point[1][0]
                    long += point[1][1]
                size = len(centroids[centroid].points)
                if size != 0:
                    lat = lat/size
                    long = long/size
                    centroids[centroid].centroid = (lat,long)
        
        # for k in centroids:
        #     print(k.centroid)
        #     print(k.points)

        # class Riders_deleveries:
        #     def __init__(self,total_volume,points_with_volume) -> None:
        #         self.total_volume = total_volume
        #         self.points_with_volume = points_with_volume
        
        riders_deleveries = []
        for i in range(len(centroids)):
            points_with_volume = []
            total_volume = 0 
            for point in centroids[i].points:
                l = self.item_dims[point[0]][0]
                b = self.item_dims[point[0]][1]
                h = self.item_dims[point[0]][2]
                volume = l*b*h
                total_volume += volume
                points_with_volume.append((volume,point[0]))
            points_with_volume.sort()
            riders_deleveries.append([total_volume,points_with_volume])
        
        riders_deleveries.sort(reverse=True)

        # print(riders_deleveries)

        riders_with_bag_volume = []
        for i in range(len(self.rider_vol)):
            riders_with_bag_volume.append((self.rider_vol[i],i))
        riders_with_bag_volume.sort(reverse=True)

        dictionary_for_riders = {}
        for i in range(len(riders_with_bag_volume)):
            while riders_with_bag_volume[i][0]<=riders_deleveries[i][0]:
                riders_deleveries[i][0] = riders_deleveries[i][0] - riders_deleveries[i][1][0][0]
                riders_deleveries[i][1].pop(0)
            delevery_points = []
            for j in riders_deleveries[i][1]:
                delevery_points.append(j[1])
            dictionary_for_riders[i] = delevery_points
        
        # final output
        riders_with_final_deliveries = []
        for i in range(self.no_riders):
            riders_with_final_deliveries.append([])

        for i in range(self.no_riders):
            riders_with_final_deliveries[i] = dictionary_for_riders[i]
        
        return riders_with_final_deliveries
