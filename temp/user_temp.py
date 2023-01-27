import random
import json
from tqdm import tqdm

roles = ["ADMIN", "RIDER"]

list_dict = []

for i in tqdm(range(100)):
    data = {
        "name": {
            "first": f"John {i+1}",
            "last": f"Doe {i+1}"
        },
        "phone_no": str(random.randint(7000000000, 9999999999)),
        "password": "mypassword",
        "role": random.choices(roles, weights=[0.1, 0.9])[0]
    }
    list_dict.append(data)

with open("user.json", "w") as f:
    json.dump(list_dict, f, indent=4)