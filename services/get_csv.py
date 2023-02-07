import csv
# List of latitude and longitude coordinates
def get_csv (lat_lon: list, file_name: str):
    # lat_lon = [[51.5074, 0.1278], [51.5194, 0.1322], [51.5275, 0.1213]]

    # Line string representation of edges connecting the nodes
    edges = ["LINESTRING({} {} , {} {})".format(lat_lon[0][1], lat_lon[0][0], lat_lon[1][1], lat_lon[1][0]),
            "LINESTRING({} {} , {} {})".format(lat_lon[1][1], lat_lon[1][0], lat_lon[2][1], lat_lon[2][0])]

    # Save the list of latitude and longitude and edges to a CSV file
    with open(file_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Node", "Edge"])
        for i, coord in enumerate(lat_lon):
            writer.writerow([f"{coord[1]}, {coord[0]}", edges[i]])
    