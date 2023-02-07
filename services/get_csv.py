import csv

def write_to_csv(coordinates: list, filename: str, id: list):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)

        # Write the header for the nodes
        writer.writerow(["AWB", "latitude", "longitude"])

        # Write the nodes to the file
        for i, coord in enumerate(coordinates):
            writer.writerow([id[i], coord[0], coord[1]])

        # Write the header for the edges
        writer.writerow(["edge_id", "start_AWB", "end_AWB", "geometry"])

        # Write the edges to the file
        for i, coord in enumerate(coordinates[:-1]):
            start = id[i]
            end = id[i] + 1
            writer.writerow([i, start, end, "LINESTRING({} {})".format(coord[0], coord[1])])

# Example usage
write_to_csv(coordinates=[(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)], filename="test.csv", id=[45,3,43,4,54])