import requests


def get_coordinates(addresses, api_key):
    req = []
    for address in addresses:
        req.append({"query": address})
        
    data = {"batch": req}
    print(data)
    base_url = f"http://api.positionstack.com/v1/forward?access_key={api_key}"
    response = requests.post(base_url, json=data)
    data = response.json()
    print(data)

addresses = [
    "1260, SY 35/4, SJR Tower's, 7th Phase, 24th Main Puttanhalli, JP Nagar, Bangalore",
    "82/3, Third Floor, Khata 866, Panathur Main Road, Bhoganahalli Cross, Marathahalli, Bangalore",
    "Embassy Tech Square Food Court, Cessna Tech Park, Outer Ring Road, Kadubeesanahalli, Marathahalli, Bangalore",
    "2617, 27th Main, Sector 1, Opposite CPWD Complex, HSR, Bangalore"
]

api_key = "908b968e7d607628359014ebc12ae1f2"

coordinates = get_coordinates(addresses, api_key)
# if coordinates:
#     for address, coord in zip(addresses, coordinates):
#         print(f"{address}: {coord}")
