from services.TSP import TSP


def tsp_calculation(cluster, hub_location, item_lat_long, return_dict, return_list):
    temp_lat_long = [hub_location]
    for id in cluster:
        temp_lat_long.append(item_lat_long[id-1])
    tsp = TSP(temp_lat_long)
    no_of_nodes = len(temp_lat_long)
    temp_path, temp_path_cost = [], 0
    if no_of_nodes > 12:
        temp_path, temp_path_cost, _ = tsp.approximation_1_5()
        for i in range(4):
            temp_path, temp_path_cost, _ = tsp.two_edge_switch(1, temp_path)
            temp_path, temp_path_cost, _ = tsp.three_edge_switch(1, temp_path)
            temp_path, temp_path_cost, _ = tsp.node_edge_insert(1, temp_path)
    else:
        temp_path, temp_path_cost, _ = tsp.perfect()

    path = []
    for node in temp_path:
        if node == 0:
            path.append(-1)
        else:
            path.append(cluster[node-1]-1)
    index_of_hub = path.index(-1)
    path = path[index_of_hub:]+path[:index_of_hub]
    return_dict['total_cost'] += temp_path_cost
    return_list.append(path[:])
