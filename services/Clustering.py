from typing import List,Tuple
import random as rd
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
    
    
    
    def distribute(self):
        class Centroid:
            def __init__(self,centroid,points):
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
        for i in range(5):
            for centroid in range(len(centroids)):
                centroids[centroid].points = []
            
            for point in range(len(self.item_lat_long)):
                min_distance  = float('inf')
                centroid_index = 0
                for j in range(len(centroids)):
                    centroid = centroids[j].centroid
                    distance = (self.item_lat_long[point][0]-centroid[0])**2+(self.item_lat_long[point][1]-centroid[1])**2
                    if distance < min_distance:
                        centroid_index = j
                        min_distance = distance
                centroids[centroid_index].points.append((point,self.item_lat_long[point]))

            # for k in centroids:
            #     print(k.centroid)
            #     print(k.points)
            
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

        for i in centroids:
            print(i.centroid)
            print(i.points)    

                