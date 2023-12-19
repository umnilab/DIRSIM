#!/usr/bin/env python
# coding: utf-8

# # specify POI features

# In[1]:


import os
import csv
import json
import time
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


# In[2]:


# 1. read POI data
# 2. read POI features  
# 3. save results  
# 4. check results → "poi_feature.json" under /data/


# # 0. Folder

# In[3]:


#simulation 
folder = "/home/umni2/a/umnilab/users/xue120/umni4/"
sim_folder = folder + "2023_abm/PostDisasterSim/"

#POI node
POI_node = sim_folder + "data/poi/poi.json"

#POI data
poi = "2022_abm/2-check-poi-data/"
poi_aug, poi_sept, poi_oct = poi+"08/", poi+"09/", poi+"10/"


# # 1. read POI data

# In[4]:


with open(POI_node, "r") as f:
    df_poi = json.load(f)
poi_list = list(df_poi["id"])
n_poi = len(poi_list)
print (n_poi)
poi_county_dict = {df_poi["id"][i]:df_poi["county"][i] for i in range(len(poi_list))}


# # 2. read POI features 

# In[5]:


#2.1 specify paths
poi_path_8 = folder + poi_aug
df_8 = os.listdir(poi_path_8)
df_8.sort()
df_8 = df_8[1:]  #["0801", "0802", ..., "0831"]

poi_path_9 = folder + poi_sept    
df_9 = os.listdir(poi_path_9) 
df_9.sort()
df_9 = df_9[1:]  

poi_path_10 = folder + poi_oct    
df_10 = os.listdir(poi_path_10) 
df_10.sort()
df_10 = df_10[1:]  
print (len(df_8), len(df_9), len(df_10))


# In[6]:


#2.2 read visit day
#df = df_8, df_9, df_10
#poi_month = poi_aug, poi_sept, poi_oct
#idx = 0, 1, 2
#ndays = 31, 30, 31
def read_visit(df, poi_month, idx, ndays, rlevel_dict):
    sum_visit = 0
    count_array = np.array([0 for i in range(ndays)])
    for i in range(len(df)):
        df_poi = pd.read_csv(folder + poi_month + df[i])
        id_list = list(df_poi["safegraph_place_id"])
        visit_list = list(df_poi["visits_by_day"])
        
        for j in range(len(visit_list)):
            poi_id = id_list[j]
            if poi_id in rlevel_dict: 
                visit_split = visit_list[j][1:-1].split(",") 
                visit = [int(visit_split[k]) for k in range(len(visit_split))]
                rlevel_dict[poi_id][idx] = visit
                sum_visit += np.sum(visit)
    return rlevel_dict, sum_visit


# In[7]:


#2.3 read POI features
rlevel_dict = dict()
for poi in df_poi["id"]:
    rlevel_dict[poi] = [[0 for i in range(31)], [0 for i in range(30)], [0 for i in range(31)]]
print (len(rlevel_dict))

rlevel_dict, sum_visit_8 = read_visit(df_8, poi_aug, 0, 31, rlevel_dict)
print (round(sum_visit_8/31, 2))
rlevel_dict, sum_visit_9 = read_visit(df_9, poi_sept, 1, 30, rlevel_dict)
print (round(sum_visit_9/30, 2))
rlevel_dict, sum_visit_10 = read_visit(df_10, poi_oct, 2, 31, rlevel_dict)
print (round(sum_visit_10/31, 2))


# # 3. save results

# In[8]:


poi_edge = sim_folder + "data/poi/poi_feature.json"
with open(poi_edge, "w") as outfile:
    json.dump(rlevel_dict, outfile)


# # 4. check results

# In[9]:


with open(poi_edge, "r") as f:
    rlevel = json.load(f)


# # All five counties

# In[10]:


county_list = ["Harris County", "Fort Bend County", "Galveston County", "Brazoria County", "Jefferson County"]
aug_feature = np.array([0 for i in range(31)])
sept_feature = np.array([0 for i in range(30)])
oct_feature = np.array([0 for i in range(31)])
for poi in rlevel:
    if poi_county_dict[poi] in county_list:
        aug_feature += np.array(rlevel[poi][0])
        sept_feature += np.array(rlevel[poi][1])
        oct_feature += np.array(rlevel[poi][2])
plt.figure(figsize=(8,2),dpi=300)
x = [i+1 for i in range(31+30+31)]
plt.plot(x, list(aug_feature)+list(sept_feature)+list(oct_feature),"s-", color="black", linewidth=1.0, markersize=2.0)
plt.xlabel("Days since August 1, 2017")
plt.title("Number of visits in the five counties")
plt.ylabel("Number of visits")


# # Harris County

# In[11]:


county_list = ["Harris County"]
aug_feature = np.array([0 for i in range(31)])
sept_feature = np.array([0 for i in range(30)])
oct_feature = np.array([0 for i in range(31)])
for poi in rlevel:
    if poi_county_dict[poi] in county_list:
        aug_feature += np.array(rlevel[poi][0])
        sept_feature += np.array(rlevel[poi][1])
        oct_feature += np.array(rlevel[poi][2])
plt.figure(figsize=(8,2),dpi=300)
x = [i+1 for i in range(31+30+31)]
plt.plot(x, list(aug_feature)+list(sept_feature)+list(oct_feature),"s-", color="r", linewidth=1.0, markersize=2.0)
plt.xlabel("Days since August 1, 2017")
plt.title("Number of visits in Harris County")
plt.ylabel("Number of visits")


# # Other four counties

# In[12]:


county_list = ["Fort Bend County", "Galveston County", "Brazoria County", "Jefferson County"]
aug_feature = np.array([0 for i in range(31)])
sept_feature = np.array([0 for i in range(30)])
oct_feature = np.array([0 for i in range(31)])
for poi in rlevel:
    if poi_county_dict[poi] in county_list:
        aug_feature += np.array(rlevel[poi][0])
        sept_feature += np.array(rlevel[poi][1])
        oct_feature += np.array(rlevel[poi][2])
plt.figure(figsize=(8,2),dpi=300)
x = [i+1 for i in range(31+30+31)]
plt.plot(x, list(aug_feature)+list(sept_feature)+list(oct_feature),"s-", color="blue", linewidth=1.0, markersize=2.0)
plt.xlabel("Days since August 1, 2017")
plt.title("Number of visits in the other four counties")
plt.ylabel("Number of visits")


# # Fort Bend

# In[13]:


county_list = ["Fort Bend County"]
aug_feature = np.array([0 for i in range(31)])
sept_feature = np.array([0 for i in range(30)])
oct_feature = np.array([0 for i in range(31)])
for poi in rlevel:
    if poi_county_dict[poi] in county_list:
        aug_feature += np.array(rlevel[poi][0])
        sept_feature += np.array(rlevel[poi][1])
        oct_feature += np.array(rlevel[poi][2])
plt.figure(figsize=(8,2),dpi=300)
x = [i+1 for i in range(31+30+31)]
plt.plot(x, list(aug_feature)+list(sept_feature)+list(oct_feature),"s-", color="blue", linewidth=1.0, markersize=2.0)
plt.xlabel("Days since August 1, 2017")
plt.title("Number of visits in Fort Bend County")
plt.ylabel("Number of visits")


# # Brazoria County

# In[14]:


county_list = ["Brazoria County"]
aug_feature = np.array([0 for i in range(31)])
sept_feature = np.array([0 for i in range(30)])
oct_feature = np.array([0 for i in range(31)])
for poi in rlevel:
    if poi_county_dict[poi] in county_list:
        aug_feature += np.array(rlevel[poi][0])
        sept_feature += np.array(rlevel[poi][1])
        oct_feature += np.array(rlevel[poi][2])
plt.figure(figsize=(8,2),dpi=300)
x = [i+1 for i in range(31+30+31)]
plt.plot(x, list(aug_feature)+list(sept_feature)+list(oct_feature),"s-", color="blue", linewidth=1.0, markersize=2.0)
plt.xlabel("Days since August 1, 2017")
plt.title("Number of visits in Brazoria County")
plt.ylabel("Number of visits")


# # Galveston County

# In[15]:


county_list = ["Galveston County"]
aug_feature = np.array([0 for i in range(31)])
sept_feature = np.array([0 for i in range(30)])
oct_feature = np.array([0 for i in range(31)])
for poi in rlevel:
    if poi_county_dict[poi] in county_list:
        aug_feature += np.array(rlevel[poi][0])
        sept_feature += np.array(rlevel[poi][1])
        oct_feature += np.array(rlevel[poi][2])
plt.figure(figsize=(8,2),dpi=300)
x = [i+1 for i in range(31+30+31)]
plt.plot(x, list(aug_feature)+list(sept_feature)+list(oct_feature),"s-", color="blue", linewidth=1.0, markersize=2.0)
plt.xlabel("Days since August 1, 2017")
plt.title("Number of visits in Galveston County")
plt.ylabel("Number of visits")


# # Jefferson County

# In[16]:


county_list = ["Jefferson County"]
aug_feature = np.array([0 for i in range(31)])
sept_feature = np.array([0 for i in range(30)])
oct_feature = np.array([0 for i in range(31)])
for poi in rlevel:
    if poi_county_dict[poi] in county_list:
        aug_feature += np.array(rlevel[poi][0])
        sept_feature += np.array(rlevel[poi][1])
        oct_feature += np.array(rlevel[poi][2])
plt.figure(figsize=(8,2),dpi=300)
x = [i+1 for i in range(31+30+31)]
plt.plot(x, list(aug_feature)+list(sept_feature)+list(oct_feature),"s-", color="blue", linewidth=1.0, markersize=2.0)
plt.xlabel("Days since August 1, 2017")
plt.title("Number of visits in Jefferson County")
plt.ylabel("Number of visits")


# In[ ]:




