from typing import List,Tuple
import statistics as st


def anomaly_detect(data: List[List[float]])-> List[List[float]]:
    z = 1.7
    data1 = [i[0] for i in data]
    data2 = [i[1] for i in data]
    data3 = [i[2] for i in data]
    data4 = [i[3] for i in data]
    mean1 = st.mean(data1)
    mean2 = st.mean(data2)
    mean3 = st.mean(data3)
    mean4 = st.mean(data4)
    # print(mean1,mean2,mean3,mean4)
    std1 = st.stdev(data1)
    std2 = st.stdev(data2)
    std3 = st.stdev(data3)
    std4 = st.stdev(data4)
    # print(std1,std2,std3,std4)
    anamoly_list = []
    for i in data:
        if i[0] > mean1 + z * std1 or i[0] < mean1 - z * std1:
            anamoly_list.append(i)
        elif i[1] > mean2 + z * std2 or i[1] < mean2 - z * std2:
            anamoly_list.append(i)
        elif i[2] > mean3 + z * std3 or i[2] < mean3 - z * std3:
            anamoly_list.append(i)
        elif i[3] > mean4 + z * std4 or i[3] < mean4 - z * std4:
            anamoly_list.append(i)
    return anamoly_list