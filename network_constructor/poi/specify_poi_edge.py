#!/usr/bin/env python
# coding: utf-8

# # specify POI edges

# In[1]:


import os
import json
import time
import numpy as np
from math import sin, cos, sqrt, atan2, radians


# In[2]:


# 1. read POI data
# 2. specify edges between two POIs → "poi_edge.json" under /data/


# # 0. Folder

# In[3]:


#simulation 
folder = "/home/umni2/a/umnilab/users/xue120/umni4/"
sim_folder = folder + "2023_abm/PostDisasterSim/"


# # 1. read POI data

# In[4]:


#read POI data 
#input: path.
#output: read_file, id_list, lon_list, lat_list, county_list
poi_node = sim_folder + "data/poi/poi.json"
with open(poi_node, "r") as f:
    df = json.load(f)

id_list, lon_list, lat_list, county_list =\
list(df["id"]), list(df["lon"]), list(df["lat"]), list(df["county"])


# # 2. specify egdes between two POIs

# In[5]:


#We define the existence of an edge between two nodes 
#if and only if their spatial distance
#is less than a predefined threshold.

#For N nodes, specifying all edges requires O(N^{2}) time.
#To reduce the computation time, we now devise a Two-Step method with O(N) complexity.


# In[6]:


#compute the distance between loc1 and loc2
def compute_distance(loc1,loc2):    #loc1: [lon1,lat1]; loc2: [lon2,lat2]
    R = 6373.0
    lon1, lat1 = radians(loc1[0]), radians(loc1[1])
    lon2, lat2 = radians(loc2[0]), radians(loc2[1])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2*atan2(sqrt(a), sqrt(1-a))
    distance = R*c
    return distance


# In[7]:


#Step 1: We build grids whose coordinates are multiples of 0.02 (around 2 km), 
#and map each home location to 9=3*3 surrounding grids.

#input: id_list, lon_list, lat_list
#output: mapping
gs = 0.02                  #grid size
num_grid = round(1/gs)  
mapping = dict()
for i in range(len(id_list)):
    lon, lat = abs(lon_list[i]), abs(lat_list[i])
    r_lon, r_lat = int(lon*num_grid)/num_grid, int(lat*num_grid)/num_grid      #0.12
    key = (r_lon, r_lat)
    
    key_1, key_2, key_3 = (r_lon+gs, r_lat), (r_lon+gs, r_lat+gs), (r_lon, r_lat+gs)
    key_4, key_5, key_6 = (r_lon-gs, r_lat+gs), (r_lon-gs, r_lat), (r_lon-gs, r_lat-gs)
    key_7, key_8 = (r_lon, r_lat-gs), (r_lon+gs, r_lat-gs)
    key_list = [key, key_1, key_2, key_3, key_4, key_5, key_6, key_7, key_8]
    for entry in key_list:
        if entry not in mapping:
            mapping[entry] = [i]          #{(90.02, 30.02): 90512, ...}
        else: 
            mapping[entry].append(i)
            
print (len(mapping))  #3K-5K
print (np.sum([len(mapping[key]) for key in mapping]))  #90513*9=814,617


# In[8]:


#Step 2: We compute all pair-wise distances within under the same key in mapping
time1 = time.time()  
threshold = 1.0    
pair_within_threshold = list()
grid_idx, edge_idx = 0, 0
for key in mapping:
    grid_idx += 1
    poi_list = mapping[key]  
    for poi_1 in poi_list:
        for poi_2 in poi_list:
            if poi_1 < poi_2:
                loc1, loc2 = [lon_list[poi_1], lat_list[poi_1]], [lon_list[poi_2], lat_list[poi_2]]
                if compute_distance(loc1, loc2) < threshold:
                    pair_within_threshold.append(str(poi_1)+"_"+str(poi_2))
                    edge_idx += 1
    if grid_idx % 200 == 0:
        print ("grid_idx:", grid_idx)
        print ("# edge:", edge_idx)
        time2 = time.time()
        print ("the total running time until now", time2 - time1)
        print ("---------------------------------------------")


# In[9]:


print ("#edges with repeating: ", len(pair_within_threshold))
pair_list = list(set(pair_within_threshold))
print ("#edges without repeating: ", len(pair_list))

output_dict = dict()
for i in range(len(pair_list)):
    output_dict[i] = pair_list[i]
print ("#edge/poi", round(len(output_dict)/len(id_list),4))


# In[10]:


poi_edge = sim_folder + "data/poi/poi_edge.json"
with open(poi_edge, "w") as outfile:
    json.dump(output_dict, outfile)


# In[ ]:




