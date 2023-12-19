#!/usr/bin/env python
# coding: utf-8

# # specify home nodes

# In[1]:


import os
import json
import time
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.cluster import MeanShift
from math import sin, cos, sqrt, atan2, radians


# In[2]:


# 0. path
# 1. read mobility data
# 2. estimate home locations for users
# 3. run the RMeanShift algorithm → "valid_user_rms.json" under /data/


# # 0. path

# In[3]:


#GPS data from Quadrant
folder = "/home/umni2/a/umnilab/users/xue120/umni4/"
gps = "2023_abm/PostDisasterSim/mob_data/"
gps_aug = gps+"08"
used_day_list = ["15", "16", "17", "18", "19", "20", "21", "22"]

#shapefile
folder_census = folder + "2022_abm/0-TX-shapefile-2/"
file_census = "Tx_Census_CntyBndry_Detail_TIGER500k.shp"

#simulation 
sim_folder = folder + "2023_abm/PostDisasterSim/"

#the number of days that is used to sample users
threshold = 6


# # 1. read mobility data

# In[4]:


mobility_path_8 = folder + gps_aug
df_8 = os.listdir(mobility_path_8)    #["0801", "0802", ...,"0831"]
df_8.sort()
df_8 = df_8[1:]  #["0801", "0802", ..., "0831"]
print (df_8)


# # 2. estimate home locations for users

# In[5]:


############################2.1-2.2: load GPS points############################
#2.1 extract GPS points
#input: month, day #month = ["08"]  #day = ["15", "16",..., "21"]
#output: user_id_list, lon_list, lat_list, time_list
def read_gps(day):
    time1 = time.time()
    id_all, lon_all, lat_all, time_all = list(), list(), list(), list()
    path = folder + gps + "08" + "/" + day + ".json"
    with open(path, "r") as f:
        df = json.load(f)                    
        f.close()
    
    user_list = list(df.keys())
    n_user = len(user_list)
    print ("#users per day is: ", n_user)
    
    lon_list = [df[user_list[i]][0] for i in range(n_user)]
    lat_list = [df[user_list[i]][1] for i in range(n_user)]
    ts_list = [df[user_list[i]][2] for i in range(n_user)]
    lon_all = [lon for item in lon_list for lon in item]
    lat_all = [lat for item in lat_list for lat in item]
    ts_all = [ts for item in ts_list for ts in item]

    user_count = [len(df[user_list[i]][0]) for i in range(n_user)]
    id_all = [user_list[i] for i in range(n_user) for j in range(user_count[i])] 
    n_all = len(id_all)
    print ("#GPS points per day is: ", n_all)

    time2 = time.time()
    print ("running time is ", round(time2 - time1, 3))
    return id_all, lon_all, lat_all, ts_all, n_all

#2.2 extract GPS points
#input: used_day_list
#output: user_id_all, lon_all, lat_all, time_all
user_id_all, lon_all, lat_all, ts_all, day_all = list(), list(), list(), list(), list()
for idx in range(len(used_day_list)):
    print ("day:", used_day_list[idx])  #"15"
    user_id_list, lon_list, lat_list, ts_list, n_all = read_gps(used_day_list[idx])
    day = int(used_day_list[idx])
    user_id_all += user_id_list
    lon_all += lon_list
    lat_all += lat_list
    ts_all += ts_list
    day_all += [day for i in range(n_all)]

#get foundamental statistics
print ("#gps points: ", len(user_id_all))
set_user = set(user_id_all)
print ("#users: ", len(set_user))


# In[6]:


#2.3 find the hour of ts
#input: ts
#output: hour, half_hour
def get_hour(ts): #ts: from 0 to 86400 
    hour = int(ts/3600.0)
    half_hour = int(2*hour + int((ts-hour*3600.0)/1800.0))
    return hour, half_hour

#2.4 extract night hour record
#input: user_id_all, lon_all, lat_all, time_all
#output: user_id_all_night, lon_all_night, lat_all_night, day_all_night, half_hour_all_night
user_id_all_night, lon_all_night, lat_all_night, day_all_night, half_hour_all_night =\
list(), list(), list(), list(), list()
night_hour = [22, 23, 0, 1, 2, 3, 4, 5] 

night_id = list()   #[0,2,4,...]
print ("# rows: ", len(ts_all))
time1 = time.time()
for i in range(len(ts_all)):
    ts = ts_all[i]
    if i %3000000==0:
        print ("i", i)
        time2 = time.time()
        print ("running time is ", round(time2 - time1, 3))
    hour, half_hour = get_hour(ts)
    if hour in night_hour:
        user_id_all_night.append(user_id_all[i])
        lon_all_night.append(lon_all[i])
        lat_all_night.append(lat_all[i])
        half_hour_all_night.append(half_hour)
        if hour not in [22, 23]:
            day_all_night.append(day_all[i]-1)
        else:
            day_all_night.append(day_all[i])
        
print (len(user_id_all_night))
print (len(set(user_id_all_night)))


# In[7]:


#2.5 extract users with sufficient number of counts during the night hours
#input: user_id_all_night
#output: count_freq_day, lon_record, lat_record, day_record, half_hour_record
#output: valid_user_id_list
count_freq_day = dict()  #count_freq_day = {"123": {"15":0,"16":0,...,"21":0}, "456": 6, ...}
lon_record = dict()      #lon_record = {"123": [-80.0, -80.1], "456": ...}
lat_record = dict()      #lat_record = {"123": [35.0, 35.1], "456": ...}
day_record = dict()      #day_record = {"123": [15,16,17,18,19,20,21]}
half_hour_record = dict()  #half_day_record = {"123": [0,1,2,...,47]}
print (len(user_id_all_night))
time1 = time.time()
for i in range(len(user_id_all_night)):
    user_id = user_id_all_night[i]
    day = day_all_night[i]
    if day not in [14, 22]:
        if user_id not in count_freq_day:
            count_freq_day[user_id] = {str(day_all_night[i]):0}
            lon_record[user_id], lat_record[user_id] = [lon_all_night[i]], [lat_all_night[i]]
            day_record[user_id], half_hour_record[user_id] = [day_all_night[i]], [half_hour_all_night[i]]
        else:
            count_freq_day[user_id][str(day_all_night[i])] = 0
            lon_record[user_id].append(lon_all_night[i])
            lat_record[user_id].append(lat_all_night[i])
            day_record[user_id].append(day_all_night[i])
            half_hour_record[user_id].append(half_hour_all_night[i])
    if i %1000000 ==0:
        print ("i = ", i)
        time2 = time.time()
        print ("running time is ", round(time2 - time1, 3))


# In[8]:


#2.6 count the length of days with gps data for each user
count_freq = {user: len(count_freq_day[user]) for user in count_freq_day}  #count_freq = {"123": 12, "456": 6, ...}
count_freq_list = list(count_freq.values())  #[4, 6, ...]
print ("ave night count per user: ", np.mean(count_freq_list))
print ("#user", len(count_freq_list))
print ("max count", np.max(list(count_freq.values())))
for i in range(8):
    print ("#" + str(i) + " point", count_freq_list.count(i))


# In[9]:


#2.7 sample users based on the number of days when the gps data exists.
valid_user_id_list = list()
num_idx = 0
for item in count_freq:
    if count_freq[item] >= threshold:
        num_idx += 1
        valid_user_id_list.append(item)
print (num_idx)
print (len(valid_user_id_list))
n_user = len(valid_user_id_list)
#output night points for all valid users.
valid_night_record = {user : [lon_record[user], lat_record[user], day_record[user], half_hour_record[user]]\
                      for user in valid_user_id_list}


# In[10]:


#2.8 extract data for sampled users.
#input: lon_freq, lat_record, valid_user_id_list
#output: valid_id_lon_seq, valid_id_lat_seq
valid_id_lon_seq, valid_id_lat_seq = dict(), dict() 
for valid_id in valid_user_id_list:
    valid_id_lon_seq[valid_id] = lon_record[valid_id]
    valid_id_lat_seq[valid_id] = lat_record[valid_id]
print (len(valid_id_lon_seq))
print (len(valid_id_lat_seq))
print (np.mean([len(valid_id_lon_seq[user_idx]) for user_idx in valid_id_lon_seq]))


# # 3. run the RMeanShift Algorithm

# In[11]:


# 3.1 combine the point within each half hour
#input: valid_night_record.  {user : [lon_record[user], lat_record[user], day_record[user], half_hour_record[user]]}
#output_1: agg_valid_id_lon_seq, {user: [lon1, lon2,...]}
#output_2: agg_valid_id_lat_seq, {user: [lat1, lat2,...]}
agg_valid_id_lon_seq, agg_valid_id_lat_seq = dict(), dict()
for user in valid_night_record:
    lon_record, lat_record, day_record, half_hour_record =\
        valid_night_record[user][0], valid_night_record[user][1], valid_night_record[user][2], valid_night_record[user][3]
    
    lon_dict, lat_dict = dict(), dict()
    for i in range(len(lon_record)):
        day_half_hour = str(day_record[i]) +"_" + str(half_hour_record[i])
        if day_half_hour not in lon_dict:
            lon_dict[day_half_hour] = [lon_record[i]]
            lat_dict[day_half_hour] = [lat_record[i]]
        else:
            lon_dict[day_half_hour].append(lon_record[i])
            lat_dict[day_half_hour].append(lat_record[i])

    agg_valid_id_lon_seq[user] = [np.mean(lon_dict[day_half_hour]) for day_half_hour in lon_dict]  
    agg_valid_id_lat_seq[user] = [np.mean(lat_dict[day_half_hour]) for day_half_hour in lat_dict]
print (np.mean([len(agg_valid_id_lon_seq[user_idx]) for user_idx in valid_id_lon_seq]))


# In[12]:


# 3.2 RMeanShift algorithm
estimate_lon_list_ms, estimate_lat_list_ms = list(), list()
user_home_ms = dict()
time1 = time.time()
n_iter = n_user
for i in range(n_iter):
    valid_id = valid_user_id_list[i]
    lon_list, lat_list = agg_valid_id_lon_seq[valid_id], agg_valid_id_lat_seq[valid_id]
    
    X = np.array([[lon_list[idx], lat_list[idx]] for idx in range(len(lon_list))])
    clustering = MeanShift(bandwidth=0.0025).fit(X)
    center_x_ms = clustering.cluster_centers_[0][0]
    center_y_ms = clustering.cluster_centers_[0][1]
    
    estimate_lon_list_ms.append(center_x_ms)
    estimate_lat_list_ms.append(center_y_ms)
    time2 = time.time()
    if i%100 == 0:
        print ("i = ", i,"   time = ", round(time2-time1, 3))

user_home_ms = {"lon": estimate_lon_list_ms,\
                "lat": estimate_lat_list_ms,\
                "id": valid_user_id_list}


# In[13]:


#input: path
#output: df_shapefile
path_census = os.path.join(folder_census,file_census) 
tx = gpd.read_file(path_census) 
df_shp = tx.loc[tx['NAME'].isin(["Harris County", "Fort Bend County", "Brazoria County",\
"Galveston County", "Jefferson County"]), :]


# In[14]:


def extract_point_within_county(user_home, df_shp, n_iter):
    zero_list = [0 for i in range(n_iter)]
    
    #generate the shapefile consisting of points
    data = {"lon": user_home['lon'], "lat": user_home['lat'], "id": user_home["id"],\
            "geometry":zero_list}
    point_df = pd.DataFrame(data, index=zero_list)
    point_crs = {'init':'epsg:4326'} # define coordinate reference system
    point_geometry = [Point(xy) for xy in zip(user_home['lon'], user_home['lat'])]
    point_gpd = gpd.GeoDataFrame(point_df, crs=point_crs, geometry = point_geometry)
    print ("#user: ", len(point_gpd), "#county: ", len(df_shp))
    
    #implement the spatial join 
    #input: point_gpd, df_shp
    #output: user_within_county
    point_gpd_project = point_gpd.to_crs("EPSG:4326")
    user_within_county = gpd.sjoin(point_gpd_project, df_shp, how='inner', op='within')
    print ("#user in the counties: ", len(user_within_county))

    #get valid users
    #input: user_within_county
    #output: user_in_five_counties
    id_list = list(user_within_county["id"])
    lon_list = list(user_within_county["lon"])
    lat_list = list(user_within_county["lat"])
    county_list = list(user_within_county["NAME"])
    print (len(id_list))
    user_in_five_counties = {"id": id_list , "lon": lon_list , "lat": lat_list, "county": county_list}
    return user_in_five_counties


# In[15]:


user_in_five_counties_rms = extract_point_within_county(user_home_ms, df_shp, n_iter)
user_rms_file = sim_folder+"data/home/valid_user_rms.json"
with open(user_rms_file , "w") as outfile:
    json.dump(user_in_five_counties_rms, outfile)
print ("done")


# In[16]:


county_name = set(user_in_five_counties_rms["county"])
county_list = list(user_in_five_counties_rms["county"])
for county in county_name:
    print (county)
    print (county_list.count(county))


# # Pearson correlation

# In[3]:


import scipy.stats


# In[4]:


x = [30418, 2712, 1573, 1701, 1539]
y = [4713, 812, 374, 342, 252]


# In[5]:


# Compute Pearson correlation coefficient and p-value
correlation_coefficient, p_value = scipy.stats.pearsonr(x, y)

# Print the results
print("Pearson correlation coefficient:", correlation_coefficient)
print("P-value:", p_value)


# In[ ]:




