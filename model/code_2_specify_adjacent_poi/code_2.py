#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.
#Simulator: PostDisasterSim.
#Authors: Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, and Satish V. Ukkusuri. 


# # code_2: compute the adjacency

# In[2]:


import os
import time
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from math import sin, cos, sqrt, atan2, radians


# # 1. read POI files

# In[3]:


#1.1 read the poi files
#input: path
#output: df_poi_data
with open("/data/xue120/2022_abm/"+"6-simulation/Code1_1/code_1_output_poi.json", "r") as f:
    df_poi_data = json.load(f)
print (len(df_poi_data))
print (df_poi_data.keys())
print (list(df_poi_data["id"])[0:5])
print (len(df_poi_data["lon"]))


# # 2. compute the adjacency

# In[4]:


############################2.1-2.4: compute the adjaceny############################
#2.1 build the location-user mapping
#input: df_poi_data
#output: mapping
time1 = time.time()
id_list, lon_list, lat_list = list(df_poi_data["id"]), list(df_poi_data["lon"]), list(df_poi_data["lat"])
#build the mapping from fixed locations to user id
#{(xxx 0.02,yyy 0.02):[0,1,2,100]}
mapping = dict()
print ("# row", len(id_list))
for i in range(len(id_list)):
    if i % 10000 == 0:
        print (i)
    lon, lat = abs(lon_list[i]), abs(lat_list[i])
    lon_round, lat_round = int(lon*100.0)/100, int(lat*100.0)/100
    key = (lon_round, lat_round)
    key_1 = (lon_round + 0.01, lat_round)
    key_2 = (lon_round + 0.01, lat_round + 0.01)
    key_3 = (lon_round, lat_round + 0.01)
    key_4 = (lon_round - 0.01, lat_round + 0.01)
    key_5 = (lon_round - 0.01, lat_round)
    key_6 = (lon_round - 0.01, lat_round - 0.01)
    key_7 = (lon_round, lat_round - 0.01)
    key_8 = (lon_round + 0.01, lat_round - 0.01)
    key_list = [key, key_1, key_2, key_3, key_4, key_5, key_6, key_7, key_8]
    for one_key in key_list:
        if one_key not in mapping:
            mapping[one_key] = [i]
        else:
            mapping[one_key].append(i)
print (len(mapping))
print (np.sum([len(mapping[key]) for key in mapping]))
time2 = time.time()
print ("the total running time", time2-time1)

#2.2 compute the spatial distance (unit: km) between locations 1 and 2.
#input: loc1, loc2
#output: distance
def distancePair(loc1,loc2):    #loc1:[lon1,lat1]; loc2:[lon2,lat2]
    R = 6373.0
    lon1 = radians(loc1[0])
    lat1 = radians(loc1[1])
    lon2 = radians(loc2[0])
    lat2 = radians(loc2[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance

#2.3 compute the spatial distance (unit: km) between locations 1 and 2.
#input: mapping
#output: pair_within_one_mile
time1 = time.time()
#second search every set
pair_within_one_mile = list()
edge_idx, key_idx = 0, 0
print ("# index: ", len(mapping))
for key in mapping:
    key_idx += 1
    idx_list = mapping[key]  
    for idx1 in idx_list:
        for idx2 in idx_list:
            if idx1 < idx2:
                loc1, loc2 = [lon_list[idx1], lat_list[idx1]], [lon_list[idx2], lat_list[idx2]]
                if distancePair(loc1, loc2) < 1.000:            # 1 km
                    pair = str(idx1) + "_" + str(idx2)
                    pair_within_one_mile.append(pair)
                    edge_idx += 1
    if key_idx % 100 == 0:
        print ("key_idx: ", key_idx)
        time2 = time.time()
        print ("the total running time until now", time2 - time1)
        print ("---------------------------------------------")
        
#2.4 statistics of pair_within_one_mile.        
print ("# pair before considering repeating", len(pair_within_one_mile))
pair_within_one_mile_list = list(set(pair_within_one_mile))
print ("# pair after deleting repeating", len(pair_within_one_mile_list))
output_dict = dict()
for i in range(len(pair_within_one_mile_list)):
    output_dict[i] = pair_within_one_mile_list[i]


# # 3. save as the json

# In[5]:


#store it as json
with open("code_2_output_poi_adj.json", "w") as outfile:
    json.dump(output_dict, outfile)
#open it 
with open("code_2_output_poi_adj.json", "r") as f:
    read_file = json.load(f)
#count the number of edges   
print("# edges: ", len(read_file))
#show one edge
print (list(read_file.values())[100])


# In[ ]:





# In[ ]:




