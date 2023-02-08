from typing import List, Tuple
import statistics as st
import numpy as np

#used for checking anomaly in length, width, height and weight
def anomaly_detect(data: List[List[float]]) -> List[int]:
    #here z is 1.7 for 90% confidence interval
    z = 1.7
    data = np.array(data)
    data1 = [i[0] for i in data] # length
    data2 = [i[1] for i in data] # width
    data3 = [i[2] for i in data] # height
    data4 = [i[3] for i in data] # weight
    mean1 = st.mean(data1) # mean of length
    mean2 = st.mean(data2) # mean of width
    mean3 = st.mean(data3) # mean of height
    mean4 = st.mean(data4) # mean of weight
    std1 = st.stdev(data1) # standard deviation of length
    std2 = st.stdev(data2) # standard deviation of width
    std3 = st.stdev(data3) # standard deviation of height
    std4 = st.stdev(data4) # standard deviation of weight

    anamoly_list = [] # list of index of anamolies

    for index, i in enumerate(data):
        # if any of the dimension is out of 90% confidence interval then it is anamoly
        if i[0] > mean1 + z * std1 or i[0] < mean1 - z * std1:
            anamoly_list.append(index)
        elif i[1] > mean2 + z * std2 or i[1] < mean2 - z * std2:
            anamoly_list.append(index)
        elif i[2] > mean3 + z * std3 or i[2] < mean3 - z * std3:
            anamoly_list.append(index)
        elif i[3] > mean4 + z * std4 or i[3] < mean4 - z * std4:
            anamoly_list.append(index)
    
    # returns list of index of anamolies
    return anamoly_list
