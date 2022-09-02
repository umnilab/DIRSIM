#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.
#Simulator: PostDisasterSim.
#Authors: Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, and Satish V. Ukkusuri. 


# # code_5: define edges between homes

# In[8]:


import os
import csv
import sys
import random
import json
import time
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
from glob import glob
import matplotlib.pyplot as plt
from shapely.geometry import Point
from math import sin, cos, sqrt, atan2,radians


# # 1. read the home location data

# In[5]:


#1.1. read the home location data 
#input: path.
#output: read_file, id_list, lon_list, lat_list, county_list
with open("code_4_output_house.json", "r") as f:
    read_file = json.load(f)

id_list = list(read_file["id"])
lon_list = list(read_file["lon"])
lat_list = list(read_file["lat"])
county_list = list(read_file["county"])


# # 2. define edges

# In[9]:


#2.1 #map the lon_list and lat_list to {(xxx 0.02,yyy 0.02):[0,1,2,100]}
#input: id_list, lon_list, lat_list
#output: mapping
time1 = time.time()
mapping = dict()
for i in range(len(id_list)):
    #if i %10000 == 0:
    #    print (i)
    lon, lat = abs(lon_list[i]), abs(lat_list[i])
    lon_round, lat_round = int(lon*50.0)/50, int(lat*50.0)/50
    key = (lon_round, lat_round)
    key_1 = (lon_round + 0.02, lat_round)
    key_2 = (lon_round + 0.02, lat_round + 0.02)
    key_3 = (lon_round, lat_round + 0.02)
    key_4 = (lon_round - 0.02, lat_round + 0.02)
    key_5 = (lon_round - 0.02, lat_round)
    key_6 = (lon_round - 0.02, lat_round - 0.02)
    key_7 = (lon_round, lat_round - 0.02)
    key_8 = (lon_round + 0.02, lat_round - 0.02)
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


# In[11]:


#2.2 compute the distance between loc1 and loc2
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


# In[12]:


#2.3. 
#input: mapping
#output: pair_within_one_mile
time1 = time.time()  #second search every set
pair_within_one_mile = list()
edge_idx = 0
key_idx = 0
for key in mapping:
    key_idx += 1
    idx_list = mapping[key]  
    for idx1 in idx_list:
        for idx2 in idx_list:
            if idx1 < idx2:
                loc1 = [lon_list[idx1], lat_list[idx1]]
                loc2 = [lon_list[idx2], lat_list[idx2]]
                if distancePair(loc1, loc2) < 1.609:
                    pair = str(idx1)+"_"+str(idx2)
                    pair_within_one_mile.append(pair)
                    edge_idx += 1
    if key_idx %10 == 0:
        print ("key_idx:", key_idx, "total_idx:", len(mapping))
        print ("size of set:", len(idx_list))
        print ("total edge:", edge_idx)
        time2 = time.time()
        print ("the total running time until now", time2 - time1)
        print ("---------------------------------------------")


# In[13]:


#2.4
#input: pair_within_one_mile
#output: output_dict, pair_within_one_mile_list
print (len(pair_within_one_mile))
pair_within_one_mile_list = list(set(pair_within_one_mile))
print (len(pair_within_one_mile_list))

output_dict = dict()
for i in range(len(pair_within_one_mile_list)):
    output_dict[i] = pair_within_one_mile_list[i]
print (len(pair_within_one_mile_list))


# # 3. save as the json

# In[15]:


with open("code_5_output_house_edge.json", "w") as outfile:
    json.dump(output_dict, outfile)


# In[ ]:




