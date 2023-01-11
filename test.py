import numpy as np
from typing import List
from services.TSP import TSP

def generate_metric_graph(N: int) -> List[List[float]]:
    points = np.random.uniform(0, 20, (N, 2))
    graph = [[0 for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for j in range(N):
            graph[i][j] = np.linalg.norm(points[i]-points[j])
    return graph

N = 10
graph = generate_metric_graph(N)
node_weights = [1 for _ in range(N)]

tsp = TSP(graph, node_weights)
tsp.shortest_distance_first()
tsp.shortest_distance_first_combination()
tsp.perfect()
