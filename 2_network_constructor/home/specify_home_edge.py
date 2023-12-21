#!/usr/bin/env python
# coding: utf-8

# # specify home edges

# In[1]:


import os
import json
import time
import numpy as np
from math import sin, cos, sqrt, atan2, radians


# In[2]:


# 1. read home location data
# 2. specify edges between two home nodes → "valid_user_edge.json" under /data/
# 3. specify edges from POI nodes to home nodes  → "valid_poi_user_edge.json" under /data/


# # 0. Folder

# In[3]:


#simulation 
folder = "/home/umni2/a/umnilab/users/xue120/umni4/"
sim_folder = folder + "2023_abm/PostDisasterSim/"


# # 1. read home location data

# In[4]:


#read the home location data 
#input: path.
#output: read_file, id_list, lon_list, lat_list, county_list
home_node = sim_folder + "data/home/valid_user_rms.json"
with open(home_node, "r") as f:
    df = json.load(f)

id_list, lon_list, lat_list, county_list = list(df["id"]), list(df["lon"]), list(df["lat"]), list(df["county"])


# In[5]:


print (len(id_list))


# # 2. specify home edges

# In[6]:


#We define the existence of an edge between two nodes 
#if and only if their spatial distance
#is less than a predefined threshold.

#For N nodes, specifying all edges requires O(N^{2}) time.
#To reduce the computation time, we now devise a Two-Step method with O(N) complexity.


# In[7]:


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


# In[8]:


#Step 1: We build grids whose coordinates are multiples of 0.02 (around 2 km), 
#and map each home location to 9=3*3 surrounding grids.

#input: id_list, lon_list, lat_list
#output: mapping
gs = 0.02                  #grid size
num_grid = round(1/gs)  
mapping = dict()
for i in range(len(id_list)):
    lon, lat = abs(lon_list[i]), abs(lat_list[i])
    lon, lat = round(int(lon*num_grid)/num_grid,2), round(int(lat*num_grid)/num_grid,2)  #0.12
    key = (lon, lat)
    
    lon_plus_gs, lon_minus_gs = round(lon+gs, 2), round(lon-gs, 2)
    lat_plus_gs, lat_minus_gs = round(lat+gs, 2), round(lat-gs, 2)
    
    key_1, key_2, key_3 = (lon_plus_gs, lat), (lon_plus_gs, lat_plus_gs), (lon, lat_plus_gs)
    key_4, key_5, key_6 = (lon_minus_gs, lat_plus_gs), (lon_minus_gs, lat), (lon_minus_gs, lat_minus_gs)
    key_7, key_8 = (lon, lat_minus_gs), (lon_plus_gs, lat_minus_gs)
    key_list = [key, key_1, key_2, key_3, key_4, key_5, key_6, key_7, key_8]
    for entry in key_list:
        if entry not in mapping:
            mapping[entry] = [i]          #{(90.02, 30.02): 35611, ...}
        else: 
            mapping[entry].append(i)
            
print (len(mapping))  #3K-5K
print (np.sum([len(mapping[key]) for key in mapping]))  #35683*9


# In[9]:


#Step 2: We compute all pair-wise distances within under the same key in mapping
time1 = time.time()  
threshold = 1.0     
pair_within_threshold = list()
grid_idx, edge_idx = 0, 0
for key in mapping:
    grid_idx += 1
    user_list = mapping[key]  
    for user_1 in user_list:
        for user_2 in user_list:
            if user_1 < user_2:
                loc1, loc2 = [lon_list[user_1], lat_list[user_1]], [lon_list[user_2], lat_list[user_2]]
                if compute_distance(loc1, loc2) < threshold:
                    pair_within_threshold.append(str(user_1)+"_"+str(user_2))
                    edge_idx += 1
    if grid_idx % 1000 == 0:
        print ("grid_idx:", grid_idx)
        print ("# edge:", edge_idx)
        time2 = time.time()
        print ("the total running time until now", time2 - time1)
        print ("---------------------------------------------")


# In[10]:


print ("#edges with repeating: ", len(pair_within_threshold))
pair_list = list(set(pair_within_threshold))
print ("#edges without repeating: ", len(pair_list))

output_dict = dict()
for i in range(len(pair_list)):
    output_dict[i] = pair_list[i]
print ("#edge/user", round(len(output_dict)/len(id_list),4))


# In[11]:


user_edge = sim_folder + "data/home/valid_user_edge.json"
with open(user_edge, "w") as outfile:
    json.dump(output_dict, outfile)


# # 3. specify edges from POIs to homes

# In[12]:


home_node = sim_folder + "data/poi/poi.json"
with open(home_node, "r") as f:
    df_poi = json.load(f)

poi_id_list, poi_lon_list, poi_lat_list, poi_county_list =\
list(df_poi["id"]), list(df_poi["lon"]), list(df_poi["lat"]), list(df_poi["county"])


# In[13]:


len(df_poi["id"])


# In[14]:


mapping_poi = dict()
for i in range(len(poi_id_list)):
    lon, lat = abs(poi_lon_list[i]), abs(poi_lat_list[i])
    lon, lat = round(int(lon*num_grid)/num_grid,2), round(int(lat*num_grid)/num_grid, 2)     #0.12
    key = (lon, lat)

    lon_plus_gs, lon_minus_gs = round(lon+gs, 2), round(lon-gs, 2)
    lat_plus_gs, lat_minus_gs = round(lat+gs, 2), round(lat-gs, 2)
    
    key_1, key_2, key_3 = (lon_plus_gs, lat), (lon_plus_gs, lat_plus_gs), (lon, lat_plus_gs)
    key_4, key_5, key_6 = (lon_minus_gs, lat_plus_gs), (lon_minus_gs, lat), (lon_minus_gs, lat_minus_gs)
    key_7, key_8 = (lon, lat_minus_gs), (lon_plus_gs, lat_minus_gs)
    
    key_list = [key, key_1, key_2, key_3, key_4, key_5, key_6, key_7, key_8]
    for entry in key_list:
        if entry not in mapping_poi:
            mapping_poi[entry] = [i]          #{(90.02, 30.02): 35611, ...}
        else: 
            mapping_poi[entry].append(i)
            
print (len(mapping_poi))  #3K-5K
print (np.sum([len(mapping_poi[key]) for key in mapping_poi]))  #57647*9


# In[15]:


set_user = set(mapping.keys())
set_poi = set(mapping_poi.keys())
print (len(set_user))
print (len(set_poi))
set_common = set_user.intersection(set_poi)
print (len(set_common))


# In[16]:


#Step 2: We compute all pair-wise distances within under the same key in mapping
time1 = time.time()  
threshold = 1.0     
pair_within_threshold = list()
user_poi_check_pair = dict()
grid_idx, edge_idx = 0, 0
for key in set_common:
    user_list = mapping[key]
    poi_list = mapping_poi[key]
    for user in user_list:
        loc1 = [lon_list[user], lat_list[user]]
        
        for poi in poi_list:
            user_poi = str(user)+"_"+str(poi)
            if user_poi not in user_poi_check_pair:
                loc2 = [poi_lon_list[poi], poi_lat_list[poi]]
                if compute_distance(loc1, loc2) < threshold:
                    pair_within_threshold.append(user_poi)
                    edge_idx += 1 
                user_poi_check_pair[user_poi]=0
            
    if grid_idx % 100 == 0:
        print ("grid_idx:", grid_idx)
        print ("# edge:", edge_idx)
        time2 = time.time()
        print ("the total running time until now", time2 - time1)
        print ("---------------------------------------------")
    grid_idx += 1


# In[17]:


print ("#edges with repeating: ", len(pair_within_threshold))
pair_list = list(set(pair_within_threshold))
print ("#edges without repeating: ", len(pair_list))

output_dict = dict()
for i in range(len(pair_list)):
    output_dict[i] = pair_list[i]
print ("#edge/user", round(len(output_dict)/len(id_list),4))
print ("#edge/poi", round(len(output_dict)/len(poi_id_list),4))


# In[18]:


home_poi_edge = sim_folder + "data/home/valid_poi_user_edge.json"
with open(home_poi_edge, "w") as outfile:
    json.dump(output_dict, outfile)


# In[ ]:




