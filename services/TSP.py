import os
import sys
import math
from random import randint
import copy
import subprocess
from time import time
from typing import List, Tuple, Set
from services.Clustering import distance

def road_distance(origin, destination)->float:
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

class TSP:
    
    N: int
    graph: List[List[float]]
    node_weight: List[float]

    def __init__(self, item_lat_long: List[Tuple[float]]) -> None:
        self.graph = self.generate_graph(item_lat_long)
        # self.node_weight = node_weight
        self.N = len(self.graph)
        if(self.N==0): raise ValueError("Graph Must Have Atleast One Node")
    
    def generate_graph(self, item_lat_long: List[Tuple[float]]) -> List[List[float]]:
        n = len(item_lat_long)
        graph = [[0 for _ in range(n)] for _ in range(n)]
        for i in range(n-1):
            for j in range(i+1, n):
                graph[i][j] = road_distance(item_lat_long[i], item_lat_long[j])
                graph[j][i] = graph[i][j]
        return graph
    
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
    
    def two_edge_switch(self, iterations: int,  path: List[int], verbose: bool = False) -> List[int]:
        
        time_start = time()
        min_path, min_path_cost = [], float('inf')
        cost = self.get_path_cost(path)
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
    
    def three_edge_switch(self, iterations: int, path: List[int], verbose: bool = False) -> List[int]:
        time_start = time()
        min_path, min_path_cost = [], float('inf')
        cost = self.get_path_cost(path)
        for _ in range(iterations):
            for i in range(self.N):
                for j in range(i, self.N):
                    for k in range(j, self.N):
                        new_path = path[:i] + list(reversed(path[j:k])) + path[i:j] + path[k:]
                        new_path_cost = self.get_path_cost(new_path)
                        if min_path_cost>new_path_cost:
                            min_path = new_path.copy()
                            min_path_cost = new_path_cost
        
        delta = time()-time_start
        if verbose: print("3 edge shift optimization:", min_path_cost, f"({delta} sec)")
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
    
    def approximation_1_5(self, verbose: bool = False) -> List[float]:
        time_start = time()
        
        
        def minimum_spanning_tree():
            INF, N, no_edge = float('inf'), self.N, 0
            N = self.N
            G = self.graph
            tree_dict = {}
            for i in range(N): tree_dict[i] = []
            selected_node = [0 for i in range(N)]
            selected_node[0] = True
            while (no_edge < N - 1):
                minimum = INF
                a, b = 0, 0
                for m in range(N):
                    if selected_node[m]:
                        for n in range(N):
                            if ((not selected_node[n]) and G[m][n]):  
                                if minimum > G[m][n]:
                                    minimum = G[m][n]
                                    a = m
                                    b = n
                tree_dict[a].append(b)
                tree_dict[b].append(a)
                selected_node[b] = True
                no_edge += 1
            return tree_dict
        
        def findpath(graph): 
            n = len(graph) 
            numofadj = list() 
            for i in range(n): 
                numofadj.append(sum(graph[i])) 
            startpoint = 0
            numofodd = 0
            for i in range(n-1, -1, -1): 
                if (numofadj[i] % 2 == 1): 
                    numofodd += 1
                    startpoint = i 
            if (numofodd > 2): 
                print("No Solution") 
                return 
            stack = list() 
            path = list() 
            cur = startpoint 
            while(stack != [] or sum(graph[cur]) != 0): 
                if (sum(graph[cur]) == 0): 
                    path.append(cur + 1) 
                    cur = stack.pop(-1) 
                else: 
                    for i in range(n): 
                        if graph[cur][i] == 1: 
                            stack.append(cur) 
                            graph[cur][i] = 0
                            graph[i][cur] = 0
                            cur = i 
                            break
            tsp_path = []
            for ele in path: 
                if ele-1 not in tsp_path: tsp_path.append(ele-1)
            if cur not in tsp_path: tsp_path.append(cur)
            return tsp_path
        
        mst_dict = minimum_spanning_tree()
        odd_edged_nodes = []
        for k, v in mst_dict.items():
            if len(v)%2: odd_edged_nodes.append(k)
        
        node_translation_dict = {}
        rev_node_translation_dict = {}
        for index, node in enumerate(odd_edged_nodes):
            node_translation_dict[index] = node
            rev_node_translation_dict[node] = index
        
        file_name = str(randint(1, 1000000))
        if not os.path.exists("./services/temp_files"):
            os.makedirs("./services/temp_files")

        with open(f"./services/temp_files/{file_name}.txt", "w+") as file:
            odd_length = len(odd_edged_nodes)
            file.write(f'{odd_length}\n')
            file.write(f'{odd_length*(odd_length-1)//2}\n')
            for i in range(odd_length):
                for j in range(i+1, odd_length):
                    if odd_edged_nodes[j] in mst_dict[odd_edged_nodes[i]]: continue
                    one = rev_node_translation_dict[odd_edged_nodes[i]]
                    two = rev_node_translation_dict[odd_edged_nodes[j]]
                    three = self.graph[odd_edged_nodes[i]][odd_edged_nodes[j]]
                    write_str = f'{one} {two} {three}\n'
                    file.write(write_str)
        
        MCPM = subprocess.run(["./services/MCPM", "-f", f"./services/temp_files/{file_name}.txt", "--minweight"], capture_output=True)
        os.remove(f"./services/temp_files/{file_name}.txt")
        
        string_edge = [x.strip() for x in MCPM.stdout.decode('utf-8').split('\n')[2:-1]]
        for edges in string_edge:
            i, j = [int(x) for x in edges.split(' ')]
            mst_dict[node_translation_dict[i]].append(node_translation_dict[j])
            mst_dict[node_translation_dict[j]].append(node_translation_dict[i])
        
        eulerian_path = [[0 for _ in range(self.N)] for _ in range(self.N)]
        for i in mst_dict:
            for j in mst_dict[i]:
                eulerian_path[i][j] = 1
                eulerian_path[j][i] = 1
                
        # print()
        path = findpath(eulerian_path)
        path_cost = self.get_path_cost(path)
        delta = time()-time_start
        if verbose: print("1.5 Approximation:", path_cost, f"({delta} sec)")
        return path, path_cost, delta
    
    def node_edge_insert(self, iterations: int, path: List[int], verbose: bool = False) -> List[float]:
        time_start = time()
        for _ in range(iterations):
            for i in range(len(path)):
                temp_path = path[:]
                node = path[i]
                del temp_path[i]
                for j in range(len(temp_path)):
                    temp_path = temp_path[:]
                    temp_path.insert(j, node)
                    if self.get_path_cost(temp_path) < self.get_path_cost(path):
                        path = temp_path[:]
                    del temp_path[j]
                    
        path_cost = self.get_path_cost(path)
        delta = time()-time_start
        return path, path_cost, delta