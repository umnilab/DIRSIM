#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.
#Simulator: PostDisasterSim.
#Authors: Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, and Satish V. Ukkusuri. 


# # code_4: estimate home locations

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


# # 1. read the mobility data

# In[3]:


#input: path
#output: date_file_8
mobility_file_path_8 = "/data/xue120/2022_abm/6-simulation/Code1_2/code_1_output_five_counties_time/08"
date_file_8 = os.listdir(mobility_file_path_8)    #["0801", "0802", ...,"0831"]
date_file_8.sort()
date_file_8 = date_file_8[1:]
print (date_file_8)  #["0801", "0802", ..., "0831"]


# # 2. estimate the home

# In[4]:


############################2.1-2.2: load poi points############################
#2.1 extract poi points
#input: month, day
#output: user_id_list, lon_list, lat_list, time_list
#month = ["08", "09"]
#day = ["0801", "0802",..., "0831"], or ["0901", "0902",..., "0930"]
def get_poi_point(month, day):
    time1 = time.time()
    user_id_list, lon_list, lat_list, time_list = list(), list(), list(), list()
    
    file_path = "/data/xue120/2022_abm/6-simulation/Code1_2/code_1_output_five_counties_time/" + str(month) +    "/" + str(day)
    all_json = os.listdir(file_path)    #["0.json", "1.json", ...]
    all_json_file = list()
    for item in all_json:
        if len(item) < 10:
            all_json_file.append(item)
    for k in range(len(all_json_file)):
        with open(file_path + "/" + all_json_file[k], "r") as f:
            df_file = json.load(f)                       #read each file
            f.close()
        user_id_list += df_file["name_select"]
        lon_list += df_file["lon_select"]
        lat_list += df_file["lat_select"]
        time_list += df_file["time_select"]
    print ("# mobility points of this day is: ", len(user_id_list))
    print ("# users of this day is: ", len(set(user_id_list)))
    time2 = time.time()
    print ("the total running time", time2 - time1)
    return user_id_list, lon_list, lat_list, time_list

#2.2 extract poi points
#input: date_file_8
#output: user_id_list_all, lon_list_all, lat_list_all, time_list_all
user_id_list_all, lon_list_all, lat_list_all, time_list_all = list(), list(), list(), list()
for day in range(16):
    print ("day:", day+1)
    user_id_list, lon_list, lat_list, time_list = get_poi_point("08", date_file_8[day])
    user_id_list_all += user_id_list
    lon_list_all += lon_list
    lat_list_all += lat_list
    time_list_all += time_list

#get foundamental statistics
print ("the size of file: ")
print (sys.getsizeof(user_id_list_all)/1024/1024/8)
print ("# all gps points: ")
print (len(user_id_list_all))
print ("# unique gps points: ")
set_user_id_list_all = set(user_id_list_all)
print (len(set_user_id_list_all))


# In[5]:


############################2.3-2.4: extract night-hour points############################
#2.3 find the hour of time unix
#input: time_unix
#output: hour
def get_hour(time_unix):
    #time_unix = 1501564948                                      
    time_normal = time.gmtime(time_unix)   
    dt = time.strftime("%Y-%m-%d %H:%M:%S",time_normal)    
    hour = int(dt.split("_")[0].split(" ")[1].split(":")[0])
    return hour

#2.4 extract night hour record
#input: user_id_list_all, lon_list_all, lat_list_all, time_list_all
#output: user_id_list_all_night, lon_list_all_night, lat_list_all_night, time_list_all_night
user_id_list_all_night = list()
lon_list_all_night = list()
lat_list_all_night = list()
time_list_all_night = list()
#night_hour = [21-5, 22-5, 23-5, 0, 1, 2, 3, 4, 5, 24+6-5]
night_hour = [16, 17, 18, 19, 20, 21, 22, 23, 0, 1]     #London time to Texas time

night_id = list()   #[0,2,4,...]
print ("# rows", len(time_list_all))
for i in range(len(time_list_all)):
    if i%10000000 == 0:
        print (i)
    unix_hour = time_list_all[i]
    if get_hour(int(unix_hour/1000)) in night_hour:
        night_id.append(i)
print (len(night_id))

user_id_list_all_night = [user_id_list_all[i] for i in night_id]
lon_list_all_night = [lon_list_all[i] for i in night_id]
lat_list_all_night = [lat_list_all[i] for i in night_id]
time_list_all_night = [time_list_all[i] for i in night_id]
print (len(user_id_list_all_night))


# In[6]:


############2.5. extract users with sufficient number of counts in the night hours##########
#2.5
#input: user_id_list_all_night
#output: count_frequency, lon_frequency, lat_frequency
#output: valid_user_id_list
count_frequency = dict()  #count_frequency = {"123": 4, "456": 6, ...}
lon_frequency = dict()  #count_frequency = {"123": [1.1, 1.2], "456": 6, ...}
lat_frequency = dict()  #count_frequency = {"123": [1.1, 1.2], "456": 6, ...}
idx  = 0 
for i in range(len(user_id_list_all_night)):
    user_id = user_id_list_all_night[i]
    idx += 1
    if user_id not in count_frequency:
        count_frequency[user_id] = 1
        lon_frequency[user_id] = [lon_list_all_night[i]]
        lat_frequency[user_id] = [lat_list_all_night[i]]
    else:
        count_frequency[user_id] += 1
        lon_frequency[user_id].append(lon_list_all_night[i])
        lat_frequency[user_id].append(lat_list_all_night[i])
    if idx %1000000 ==0:
        print ("idx = ", idx)
count_frequency_list = list(count_frequency.values())  #[4, 6, ...]
print ("ave # count", np.mean(count_frequency_list))
print ("# user", len(count_frequency_list))

print (np.max(list(count_frequency.values())))
print (count_frequency_list.count(1))
print (count_frequency_list.count(2))
print (count_frequency_list.count(3))
print (count_frequency_list.count(4))
print (count_frequency_list.count(5))

#find the id with >160 data points
valid_user_id_list = list()
num_idx = 0
threshold = 160
for item in count_frequency:
    if count_frequency[item] > threshold:
        num_idx += 1
        valid_user_id_list.append(item)
print (num_idx)
print (len(valid_user_id_list))


# In[7]:


########## 2.6 estimate their homes ##########
#input: lon_frequency, lat_frequency, valid_user_id_list
#output: estimate_lon_list, lat_list
lon_valid_id_gps_sequence = dict() 
lat_valid_id_gps_sequence = dict() 
for valid_id in valid_user_id_list:
    lon_valid_id_gps_sequence[valid_id] = lon_frequency[valid_id]
    lat_valid_id_gps_sequence[valid_id] = lat_frequency[valid_id]
print (len(lon_valid_id_gps_sequence))
print (len(lat_valid_id_gps_sequence))

estimate_lon_list = list()
estimate_lat_list = list()
for i in range(len(valid_user_id_list)):
    valid_id = valid_user_id_list[i]
    lon_list = lon_valid_id_gps_sequence[valid_id]
    lat_list = lat_valid_id_gps_sequence[valid_id]
    estimate_lon = np.mean(lon_list)
    estimate_lat = np.mean(lat_list)
    estimate_lon_list.append(estimate_lon)
    estimate_lat_list.append(estimate_lat)


# # 3. Add another column of county

# In[10]:


#3.1. read the shapefile
#input: path
#output: df_shapefile
folder_census = "/data/xue120/2022_abm/"+"0-TX-shapefile/"
file_census = "Tx_Census_CntyJurisdictional_TIGER.shp"
path_census = os.path.join(folder_census,file_census) 
tx = gpd.read_file(path_census) 
df_shapefile = tx.loc[tx['NAME'].isin(["Harris County", "Fort Bend County", "Brazoria County","Galveston County", "Jefferson County"]), :]

#3.2. generate the shapefile consisting of points
#input: user_home
#output: point_gpd
data = {"lon": user_home['lon'], "lat": user_home['lat'], "id": user_home["id"],        "geometry":[0 for i in range(len(user_home['lon']))]}
print ("1/4")
point_df = pd.DataFrame(data, index=[i for i in range(len(user_home['lon']))])
print ("2/4")
point_crs = {'init':'epsg:4326'} # define coordinate reference system
point_geometry = [Point(xy) for xy in zip(user_home['lon'], user_home['lat'])]
print ("3/4")
point_gpd = gpd.GeoDataFrame(point_df, crs = point_crs, geometry = point_geometry)
print ("4/4")
print ("number of poi point: ", len(point_gpd)) 
print ("number of census tract: ",len(df_shapefile))

#3.3. implement the spatial join 
#input: point_gpd, df_shapefile
#output: poi_within_tract_result
start_time = time.time()
poi_within_tract_result = gpd.sjoin(point_gpd, df_shapefile, how='inner', op='within')
end_time = time.time()
print ("total running time: ", end_time - start_time)
print ("number of poi point in one of census tract: ", len(poi_within_tract_result))

#3.4. extract the column in poi_within_tract_result
#input: poi_within_tract_result
#output: id_list, lon_list, lat_list, county_list
id_list = list(poi_within_tract_result["id"])
lon_list = list(poi_within_tract_result["lon"])
lat_list = list(poi_within_tract_result["lat"])
county_list = list(poi_within_tract_result["NAME"])
print (len(id_list))

#3.5. 
human_five_county = {"id": id_list , "lon": lon_list ,                   "lat": lat_list, "county":county_list}


# # 4. save as the json

# In[15]:


with open("code_4_output_house.json", "w") as outfile:
    json.dump(human_five_county, outfile)


# In[16]:


#input: path
with open("code_4_output_house.json", "r") as f:
    read_file = json.load(f)
print (read_file.keys())
print (len(read_file["id"]))


# In[17]:


county_name_set = set(county_list)
print (len(county_name_set))
print ("----------------------------------------")
for i in county_name_set:
    print (i)
    print (county_list.count(i))


# In[ ]:





# In[ ]:




