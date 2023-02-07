import requests
import json
# route_data = [[15.638070, 74.916183],[15.399739, 75.001707], [15.452276, 75.302718], [15.575888, 75.366442],[15.857958, 75.108613],[15.813357, 74.487377],[15.638070, 74.916183]]
def get_geojson(route_data: list, file_name: str):
    api_key = "AtD6KKbxZbMGumtiusZaHBClfullYMvlqCbIacNNkQQu-ONLx-95xel_a6y45wTH"
    route_length = len(route_data)
    coordinates = []
    for i in range(route_length-1):
        start = f"{route_data[i][0]}, {route_data[i][1]}"
        end = f"{route_data[i+1][0]}, {route_data[i+1][1]}"
        url = f"https://dev.virtualearth.net/REST/v1/Routes/Driving?wp.0={start}&wp.1={end}&key={api_key}"

        response = requests.get(url)
        data = response.json()
        routes = data['resourceSets'][0]['resources'][0]['routeLegs'][0]['itineraryItems']
        for route in routes:
            coordinates.append(route['maneuverPoint']['coordinates'])

    # ! Building geoson out of coordinates
    geojson = {}
    geojson['type'] = 'FeatureCollection'
    geojson['features'] = [{
        'type': 'Feature',
        "properties": {},
        'geometry': {
            'type': 'polygon',
            'coordinates': coordinates
        }
    }]
    print(geojson)
    with open(file_name, "w+") as file:
    # Write the dictionary to the file as a JSON string
        json.dump(geojson, file)
    return geojson


# print(get_geojson(route_data=route_data))

