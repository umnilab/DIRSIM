#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.
#Simulator: PostDisasterSim.
#Authors: Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, and Satish V. Ukkusuri. 


# # code_3: get poi dynamic

# In[2]:


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


# # 1. read POI information data: name, lon, lat, county

# In[5]:


#1.1 read the POI information
#input: path
#output: df_poi
with open("code_1_output_poi.json", "r") as f:
    df_poi = json.load(f)
print(len(df_poi))
print(len(df_poi["id"]))
print(df_poi["id"][0])
print(df_poi["lon"][0])
print(df_poi["lat"][0])
print(df_poi["county"][0])


# In[6]:


#1.2 read POI activity
#input: path
#output: poi_file_name_8, poi_file_name_9, id_list
poi_activity_file_8 = "/data/xue120/2022_abm/2-check-poi-data/08/"
poi_activity_file_9 = "/data/xue120/2022_abm/2-check-poi-data/09/"
poi_file_name_8 = os.listdir(poi_activity_file_8)    #["xxx.csv", ]
poi_file_name_9 = os.listdir(poi_activity_file_9)    #["xxx.csv", ]
poi_file_name_8.sort()
poi_file_name_9.sort()
poi_file_name_8 = poi_file_name_8[1:]
poi_file_name_9 = poi_file_name_9[1:]
print (len(poi_file_name_8))
print (len(poi_file_name_9))


for i in range(1):
    poi_file = pd.read_csv(poi_activity_file_8 + poi_file_name_8[i])
    print (poi_file.head(2))
    id_list = list(poi_file["safegraph_place_id"])
    print (len(id_list))
    print (len(set(id_list).intersection(set(df_poi["id"]))))
    print("------------------------------------")


# # 2. record the activitity level

# In[8]:


#2.1
#input: df_poi
#output: activity_level_dict
activity_level_dict = dict()
for poi in df_poi["id"]:
    activity_level_dict[poi] = [[0 for i in range(31)], [0 for i in range(30)]]
print (activity_level_dict[poi][0])
print (len(activity_level_dict))


# In[9]:


#2.2 read the POI files
#input:month, file_name
#output: id_list, activity_list, final_id_list, final_activity_list 
#month = ["08", "core_poi-patterns"]
id_list = list()
activity_list = list()
def read_poi(month, file_name):
    if month == "08":
        poi_activity_file = "/data/xue120/2022_abm/2-check-poi-data/08/"
    if month == "09":
        poi_activity_file = "/data/xue120/2022_abm/2-check-poi-data/09/"
    full_file_name = poi_activity_file + file_name
    df_poi_file = pd.read_csv(full_file_name)
    
    id_list = df_poi_file["safegraph_place_id"]
    activity_list = df_poi_file["popularity_by_hour"]
    final_id_list = list()
    final_activity_list = list()
    #print("the size of initial id list")
    #print(len(activity_list))
    
    for j in range(len(activity_list)):
        #print (type(activity_list[j]))
        if type(activity_list[j]) == str:
            final_id_list.append(id_list[j])
            activity_split = activity_list[j][1:-1].split(",")
            #print ("!!!!")
            activity_sum = np.sum([int(activity_split[i]) for i in range(len(activity_split))])
            final_activity_list.append(activity_sum)
    #print("-----------------------")
    #print("the size of final id list")
    print(len(final_id_list))
    print(len(final_activity_list)) 
    return final_id_list, final_activity_list


# In[10]:


#2.3
#input: df_poi, poi_file_name_8
#output: activity_level_dict
r1, r2 = read_poi("08", "core_poi-patterns-part1.csv")

#read the preprocess the data in August
valid_poi_list = list(df_poi["id"])
for file_idx in range(len(poi_file_name_8)):
    time1 = time.time()
    print ("file_idx:", file_idx + 1)
    final_id_list, final_activity_list = read_poi("08", poi_file_name_8[file_idx])
    
    valid_poi_dict = {poi:0 for poi in final_id_list}
    for poi in valid_poi_list:
        valid_poi_dict[poi] = 1
    
    for i in range(len(final_activity_list)):
        poi_id = final_id_list[i]
        if valid_poi_dict[poi_id] == 1:
            activity_level = final_activity_list[i]  
            for day in range(31):
                activity_level_dict[poi_id][0][day] += int(activity_level)/31.0
    time2 = time.time()
    print ("the total running time for one day", time2 - time1)
    print ("---------------------------------------------------------")

for file_idx in range(len(poi_file_name_9)):
    time1 = time.time()
    print ("file_idx:", file_idx + 1)
    final_id_list, final_activity_list = read_poi("09", poi_file_name_9[file_idx])
    
    valid_poi_dict = {poi:0 for poi in final_id_list}
    for poi in valid_poi_list:
        valid_poi_dict[poi] = 1
    
    for i in range(len(final_activity_list)):
        poi_id = final_id_list[i]
        if valid_poi_dict[poi_id] == 1:
            activity_level = final_activity_list[i]    
            for day in range(30):
                activity_level_dict[poi_id][1][day] += int(activity_level)/30.0
    time2 = time.time()
    print ("the total running time for one day", time2 - time1)
    print ("---------------------------------------------------------")


# # 3. save json

# In[11]:


with open("code_3_output_poi_activity.json", "w") as outfile:
    json.dump(activity_level_dict, outfile)


# In[12]:


with open("code_3_output_poi_activity.json", "r") as f:
    ac_poi = json.load(f)


# In[13]:


august_ac = [[ac_poi[idx][0][i] for i in range(31)] for idx in list(ac_poi.keys())]
sept_ac = [[ac_poi[idx][1][i] for i in range(30)] for idx in list(ac_poi.keys())]


# In[14]:


august_aver = np.average(august_ac, axis=0)
sept_aver = np.average(sept_ac, axis=0)


# In[15]:


all_aver = list(august_aver) + list(sept_aver)

x = [i for i in range(61)]
y = all_aver

plt.figure(figsize=(10,3),dpi=300)
plt.scatter(x, y, s=16, c='orangered',edgecolors ='black', marker='o', linewidths=0.8,zorder=30)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.show()


# In[ ]:




