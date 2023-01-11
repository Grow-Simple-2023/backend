import sys
import copy
from time import time
from typing import List, Tuple, Set

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
    
    def shortest_distance_first(self, start: int, verbose: bool = False) -> List[int]:
        
        time_start = time()
        def argmin_except(neighbours: List[float], path: List[int]) -> Tuple[List[int], float]:
            n = len(neighbours)
            min_value, min_index = float('inf'), -1
            for i in range(n):
                if i in path: continue
                if neighbours[i]<min_value:
                    min_value, min_index = neighbours[i], i
            return min_index

        path = [start]
        i = start
        while len(path)<self.N:
            next_path = argmin_except(self.graph[i], path)
            path.append(next_path)
            i = next_path
        
        path_cost = self.get_path_cost(path)
        delta = time()-time_start
        if verbose: print("Shortest distance first:", path_cost, f"({delta} sec)")
        return path, path_cost, delta
    
    def shortest_distance_first_combination(self, verbose: bool = False) -> List[int]:
        
        time_start = time()
        def argmin_except(neighbours: List[float], path: List[int]) -> Tuple[List[int], float]:
            n = len(neighbours)
            min_value, min_index = float('inf'), -1
            for i in range(n):
                if i in path: continue
                if neighbours[i]<min_value:
                    min_value, min_index = neighbours[i], i
            return min_index

        min_path_cost, min_path = float('inf'), {}
        for i in range(self.N):
            path, path_cost, _ = self.shortest_distance_first(i)
            if path_cost<min_path_cost:
                min_path_cost, min_path = path_cost, path.copy()
        
        delta = time()-time_start
        if verbose: print("Shortest distance first combination:", min_path_cost, f"({delta} sec)")
        return min_path, min_path_cost, delta
    
    def two_edge_switch(self, iterations: int, verbose: bool = False) -> List[int]:
        
        time_start = time()
        min_path, min_path_cost = [], float('inf')
        path, cost, _ = self.shortest_distance_first_combination()
        for _ in range(iterations):
            for i in range(self.N):
                for j in range(i, self.N):
                    new_path = path[:i] + list(reversed(path[i:j])) + path[j:]
                    new_path_cost = self.get_path_cost(new_path)
                    if min_path_cost>new_path_cost:
                        min_path = new_path.copy()
                        min_path_cost = new_path_cost
        
        delta = time()-time_start
        if verbose: print("2 edge shift optimization:", min_path_cost, f"({delta} sec)")
        return min_path, min_path_cost, delta
    
    def perfect(self, verbose: bool = False) -> List[float]:
        time_start = time()
        
        matrix = self.graph
        data = list(range(1, self.N+1))
        n = len(data)
        all_sets, g, p, path = [], {}, [], []
        
        def get_minimum(k, a):
            if (k, a) in g:
                return g[k, a]

            values = []
            all_min = []
            for j in a:
                set_a = copy.deepcopy(list(a))
                set_a.remove(j)
                all_min.append([j, tuple(set_a)])
                result = get_minimum(j, tuple(set_a))
                values.append(matrix[k-1][j-1] + result)

            g[k, a] = min(values)
            p.append(((k, a), all_min[values.index(g[k, a])]))

            return g[k, a]
        
        
        for x in range(1, n):
            g[x + 1, ()] = matrix[x][0]

        get_minimum(1, tuple(data[1:]))

        path.append(0)
        solution = p.pop()
        path.append(solution[1][0]-1)
        for x in range(n - 2):
            for new_solution in p:
                if tuple(solution[1]) == new_solution[0]:
                    solution = new_solution
                    path.append(solution[1][0]-1)
                    break

        path_cost = self.get_path_cost(path)
        delta = time()-time_start
        if verbose: print("Shortest distance perfect:", path_cost, f"({delta} sec)")
        return path, path_cost, delta
    