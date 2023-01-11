from typing import List, Tuple

class TSP:
    
    N: int
    graph: List[List[float]]
    node_weight: List[float]

    def __init__(self, graph: List[List[float]], node_weight: List[float]) -> None:
        self.graph = graph
        self.node_weight = node_weight
        self.N = len(graph)
        if(self.N==0): raise ValueError("Graph Must Have Atleast One Node")
    
    def get_path_cost(self, path: List[int]) -> float:
        cost = 0
        for i in range(self.N-1):
            cost += self.graph[path[i]][path[i+1]]
        cost += self.graph[path[-1]][path[0]]
        return cost
    
    def shortest_distance_first(self) -> List[int]:
        
        def argmin_except_self(neighbours: List[float], index: int) -> Tuple[List[int], float]:
            n = len(neighbours)
            min_value, min_index = float('inf'), -1
            for i in range(n):
                if i==index: continue
                if neighbours[i]<min_value:
                    min_value, min_index = neighbours[i], i
            return min_index

        path = [0]
        for i in range(self.N-1):
            next_path = argmin_except_self(self.graph[i], i)
            path.append(next_path)
            
        path_cost = self.get_path_cost(path)
        print("Shortest distance first:", path_cost)
        return path, path_cost
    
    def shortest_distance_first_combination(self) -> List[int]:
        
        def argmin_except_self(neighbours: List[float], index: int) -> Tuple[List[int], float]:
            n = len(neighbours)
            min_value, min_index = float('inf'), -1
            for i in range(n):
                if i==index: continue
                if neighbours[i]<min_value:
                    min_value, min_index = neighbours[i], i
            return min_index

        path = [0]
        for i in range(self.N-1):
            next_path = argmin_except_self(self.graph[i], i)
            path.append(next_path)
            
        path_cost = self.get_path_cost(path)
        print("Shortest distance first:", path_cost)
        return path, path_cost
    