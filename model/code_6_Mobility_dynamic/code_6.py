#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.
#Simulator: PostDisasterSim.
#Authors: Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, and Satish V. Ukkusuri. 


# # code_6: get user activities

# In[2]:


import os
import csv
import sys
import json
import time
import random
import numpy as np
import pandas as pd
import geopandas as gpd
from glob import glob
import matplotlib.pyplot as plt
from shapely.geometry import Point
from math import sin, cos, sqrt, atan2,radians


# # 1. read user home, user trajectory

# In[4]:


#1.1. read user homes
with open("code_4_output_house.json", "r") as f:
    human_location = json.load(f)
print(len(human_location))
print(len(human_location["id"]))
print(human_location["id"][0])
print(human_location["lon"][0])
print(human_location["lat"][0])
print(human_location["county"][0])

#{"123": [-100, 25]}
human_lon_lat_dict = {human_location["id"][i]:                      [human_location["lon"][i], human_location["lat"][i]]                      for i in range(len(human_location["lat"]))}


# In[5]:


#1.2. read user trajectory
mobility_file_path_8 = "/data/xue120/2022_abm/6-simulation/Code1_2/code_1_output_five_counties_time/08"
date_file_8 = os.listdir(mobility_file_path_8)    #["0801", "0802", ...,"0831"]
date_file_8.sort()
date_file_8 = date_file_8[1:]
print (date_file_8)  #["0801", "0802", ..., "0831"]

mobility_file_path_9 = "/data/xue120/2022_abm/6-simulation/Code1_2/code_1_output_five_counties_time/09"
date_file_9 = os.listdir(mobility_file_path_9)    #["0801", "0802", ...,"0831"]
date_file_9.sort()
date_file_9 = date_file_9[1:]
print (date_file_9)  #["0901", "0902", ..., "0930"]


# # 2. compute activity levels

# In[6]:


#2.1. load the mobility data
#input: month, day
#output: user_id_list, lon_list, lat_list, time_list
#############################
#month = ["08", "09"]
#day = ["0801", "0802",..., "0831"], or ["0901", "0902",..., "0930"]
def get_poi_point(month, day):
    time1 = time.time()
    user_id_list, lon_list, lat_list, time_list = list(), list(), list(), list()
    
    file_path = "/data/xue120/2022_abm/6-simulation/Code1_2/code_1_output_five_counties_time/" + str(month) +    "/" + str(day)
    all_json = os.listdir(file_path) #["0.json", "1.json", ...]
    all_json_file = list()
    for item in all_json:
        if len(item) < 10:
            all_json_file.append(item)
    for k in range(len(all_json_file)):
        #print ("k = ", k)
        with open(file_path + "/" + all_json_file[k], "r") as f:
            df_file = json.load(f)                       #read each file
            
        user_id_list_one_day = df_file["name_select"]
        lon_list_one_day = df_file["lon_select"]
        lat_list_one_day = df_file["lat_select"]
        time_list_one_day = df_file["time_select"]
        
        user_id_list += user_id_list_one_day
        lon_list += lon_list_one_day
        lat_list += lat_list_one_day
        time_list += time_list_one_day
    print ("# mobility points of this day is: ", len(user_id_list))
    print ("# users of this day is: ", len(set(user_id_list)))
    time2 = time.time()
    print ("the total running time", time2 - time1)
    return user_id_list, lon_list, lat_list, time_list


# In[7]:


#2.2. initilize the activity_level
#input: human_location
#output: activity level
activity_level = dict()
for user in human_location["id"]:
    activity_level[user] = [[0 for i in range(31)], [0 for i in range(30)]]
print (activity_level[human_location["id"][0]])
print (len(activity_level))


# In[12]:


#2.3
def get_hour(time_unix):
    #time_unix = 1501564948                                      
    time_normal = time.gmtime(time_unix)   
    dt = time.strftime("%Y-%m-%d %H:%M:%S",time_normal)    
    hour = int(dt.split("_")[0].split(" ")[1].split(":")[0])
    return hour

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


# In[13]:


#2.4 read the preprocess the data in August
#input: human_location
#output: user_id_list, lon_list, lat_list, time_list)
#output: valid_user_dict, activity_level

night_hour = [16, 17, 18, 19, 20, 21, 22, 23, 0, 1]
valid_user_id_list = list(human_location["id"])
threshold = 10 # a criterion to check whether the human has gone home

for day in range(31):
    time1 = time.time()
    print ("day:", day + 1)
    
    total_count = 0
    user_id_list, lon_list, lat_list, time_list = get_poi_point("08", date_file_8[day])
    valid_user_dict = {user:0 for user in user_id_list}
    for user in valid_user_id_list:
        valid_user_dict[user] = 1
    time2 = time.time()
    print ("the total running time for geting gps points on one day", time2 - time1)
    
    print (len(time_list))
    for i in range(len(time_list)):
        #if i%1000000 == 0:
        #    print (i)
        user_id = user_id_list[i]
        unix_hour = time_list[i]
        
        if valid_user_dict[user_id] == 1:
            if activity_level[user_id][0][day] == 0:
                if get_hour(int(unix_hour/1000)) in night_hour:
                    if distancePair(human_lon_lat_dict[user_id], [lon_list[i], lat_list[i]]) < threshold:
                        activity_level[user_id][0][day] = 1
                        total_count += 1
                        
    print ("total count for one day:", total_count)
    time2 = time.time()
    print ("the total running time for one day", time2 - time1)
    print ("---------------------------------------------------------")


# In[14]:


#2.5 read the preprocess the data in Sept
#input: human_location
#output: user_id_list, lon_list, lat_list, time_list)
#output: valid_user_dict, activity_level

night_hour = [16, 17, 18, 19, 20, 21, 22, 23, 0, 1]
valid_user_id_list = list(human_location["id"])
threshold = 10 # a criterion to check whether the human has gone home

for day in range(30):
    time1 = time.time()
    print ("day:", day + 1)
    
    total_count = 0
    user_id_list, lon_list, lat_list, time_list = get_poi_point("09", date_file_9[day])
    valid_user_dict = {user:0 for user in user_id_list}
    for user in valid_user_id_list:
        valid_user_dict[user] = 1
    #print (np.sum(valid_user_dict.values()))
    time2 = time.time()
    print ("the total running time for geting gps points on one day", time2 - time1)
    
    print (len(time_list))
    for i in range(len(time_list)):
        #if i%1000000 == 0:
        #    print (i)
        user_id = user_id_list[i]
        unix_hour = time_list[i]
        
        if valid_user_dict[user_id] == 1:
            if activity_level[user_id][1][day] == 0:
                if get_hour(int(unix_hour/1000)) in night_hour:
                    if distancePair(human_lon_lat_dict[user_id], [lon_list[i], lat_list[i]]) < threshold:
                        activity_level[user_id][1][day] = 1
                        total_count += 1
                        
    print ("total count for one day:", total_count)
    time2 = time.time()
    print ("the total running time for one day", time2 - time1)
    print ("---------------------------------------------------------")


# # 4. save as the json

# In[15]:


with open("code_6_human_activity.json", "w") as outfile:
    json.dump(activity_level, outfile)


# In[16]:


with open("code_6_human_activity.json", "r") as f:
    ac_human = json.load(f)


# In[17]:


august_ac = [[ac_human[idx][0][i] for i in range(31)] for idx in list(ac_human.keys())]
sept_ac = [[ac_human[idx][1][i] for i in range(30)] for idx in list(ac_human.keys())]


# In[18]:


august_aver = np.average(august_ac, axis=0)
sept_aver = np.average(sept_ac, axis=0)


# In[19]:


all_aver = list(august_aver) + list(sept_aver)

x = [i for i in range(61)]
y = all_aver

plt.figure(figsize=(10,3),dpi=300)
plt.scatter(x, y, s=16, c='orangered',edgecolors ='black',            marker='o', linewidths=0.8,zorder=30)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.show()


# In[ ]:




