import random as rd
from anomaly_detect import anomaly_detect
import json


l = []
for i in range(100):
    a = []
    a.append(rd.uniform(1,100))
    a.append(rd.uniform(1,100))
    a.append(rd.uniform(1,100))
    a.append(rd.uniform(1,100))
    l.append(a)

print(json.dumps(anomaly_detect(l),indent=4))
print(len(anomaly_detect(l)))