#!/usr/bin/env python
# coding: utf-8

# # specify home features

# In[1]:


import os
import json
import time
import numpy as np
import pyarrow.parquet as pq
from math import sin, cos, sqrt, atan2, radians


# In[2]:


# 0. folder
# 1. read user homes and GPS trajectories
# 2. specify features as recovery levels  → "valid_user_feature.json" under /data/


# # 0. Folder

# In[3]:


#simulation 
folder = "/home/umni2/a/umnilab/users/xue120/umni4/"
sim_folder = folder + "2023_abm/PostDisasterSim/"

#mobility_data
folder_mob = "/home/umni2/a/umnilab/data/quadrant/Texas/2017/" 
mob_aug = os.listdir(folder_mob + "08/")
mob_sept = os.listdir(folder_mob + "09/")
print (mob_aug, mob_sept)
print (len(mob_aug), len(mob_sept))

#valid user
home_node = sim_folder + "data/home/valid_user_rms.json"

#hour and threshold to determine whether the user has returned home
night_hour_1, night_hour_2 = [22, 23], [0, 1, 2, 3, 4, 5]
night_hour = [night_hour_1, night_hour_2]
threshold = 8.0


# # 1. read user homes and GPS trajectories

# In[4]:


#read user homes
with open(home_node, "r") as f:
    df = json.load(f)

user_list = list(df["id"])  #v: valid
user_int_list = [int(user) for user in user_list]
n_user = len(user_int_list) 
print(n_user)

user_dict = {user:0 for user in user_int_list}
user_home = {user_int_list[i]: [round(df["lon"][i],5), round(df["lat"][i], 5)] for i in range(n_user)}
user_county = {user_int_list[i]: df["county"][i] for i in range(n_user)}


# # 2. specify features as recovery levels

# In[5]:


#2.1 extract GPS points
#input: month, day #month = ["08", "09"] 
#(start_day, num_day) 
#output: user_id_list, lon_list, lat_list, ts_list
def read_gps(month, start_day, num_day):
    id_all, lon_all, lat_all, ts_all = list(), list(), list(), list()
    if month == "08":
        df_folder, df_day = folder_mob+"08/", mob_aug 
    elif month == "09":
        df_folder, df_day = folder_mob+"09/", mob_sept     
    
    for idx in range(num_day):    
        #1. read the mobility data
        table = pq.read_table(df_folder + df_day[start_day-1+idx])
        df = table.to_pandas()
        df_valid = df[df["uid"].isin(user_int_list)]
        n_user, n_valid = len(df), len(df_valid)
        print ("n_user: ", n_user,  "     n_valid: ", n_valid)
        
        #2. read the mob data
        lon_all, lat_all, ts_all, id_all = list(), list(), list(), list()
        df_lon, df_lat, df_ts, df_uid =\
            list(df_valid["lon"]), list(df_valid["lat"]), list(df_valid["ts"]), list(df_valid["uid"])
        
        df_lon_list = [df_lon[i] for i in range(n_valid)]
        df_lat_list = [df_lat[i] for i in range(n_valid)]
        df_ts_list = [df_ts[i] for i in range(n_valid)]
        
        lon_all = [lon for item in df_lon_list for lon in item]
        lat_all = [lat for item in df_lat_list for lat in item]
        ts_all = [ts for item in df_ts_list for ts in item]
        
        n_df_list = [len(df_lon[i]) for i in range(n_valid)]
        id_all = [df_uid[i] for i in range(n_valid) for j in range(n_df_list[i])]   
        n_point = len(id_all)
        print ("n_valid_point: ", n_point)
        
    return id_all, lon_all, lat_all, ts_all, n_point


# In[6]:


#2.2
def get_hour(ts): #ts: from 0 to 86400 
    hour = int(ts/3600.0)
    half_hour = int(2*hour + int((ts-hour*3600.0)/1800.0))
    return hour, half_hour


# In[7]:


#2.3
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


#2.4 combine the point within the same half hour
#input: lon_lat_hhour = [...,[-50.123, 30.123, 12],...]  #hhour: half hour
#output: combine_lon_lat = [...,[-50.123, 30.123],...]
def combine_point_by_half_hour(lon_lat_hhour):
    combine_lon_lat = list()
    for idx in range(len(lon_lat_hhour)):
        combine_lon_lat.append([lon_lat_hhour[idx][0], lon_lat_hhour[idx][1]])
    return combine_lon_lat


# In[9]:


#2.5
#input: user, night_record
#output: lon, lat
def estimate_lon_lat(user, night_record):
    if len(night_record[user])==0:
        return 0
    else:
        X = np.array(combine_point_by_half_hour(night_record[user]))
        center_x_ms, center_y_ms = np.mean(X, axis=0)
        return [center_x_ms, center_y_ms] 


# In[10]:


#2.6 extract the centroid of nighttime points
#input1: month = "08", "09"  
#input2: user_int_dict = {int(user):0, ..} 
#input3: night_hour = [[22, 23], [0, 1, 2, 3, 4, 5]] 
#input4: day = 1, 2, 3, ...., 31
def compute_centroid_night_point(month, user_dict, night_hour, day):
    night_record = {user: [] for user in user_dict}  
    aver_night_record = {user: [] for user in user_dict}
    
    night_hour_1, night_hour_2 = night_hour[0], night_hour[1] 
    #[22, 23]; [0, 1, 2, 3, 4, 5]
    user_id_list, lon_list, lat_list, ts_list, n_point = read_gps(month, day, 1)
    for i in range(n_point):
        hour, half_hour = get_hour(ts_list[i])
        if hour in night_hour_1:
            night_record[user_id_list[i]].append([lon_list[i], lat_list[i], half_hour])
    
    print ("------------------------------")
    next_day_month, next_day = month, day+1
    if month == "08" and day == 31:
        next_day_month, next_day = "09", 1 
        
    user_id_list, lon_list, lat_list, ts_list, n_point = read_gps(next_day_month, next_day, 1)
    for i in range(n_point):
        hour, half_hour = get_hour(ts_list[i])
        if hour in night_hour_2:
            night_record[user_id_list[i]].append([lon_list[i], lat_list[i], half_hour])    
    
    for user in user_dict:        
        lon_lat = estimate_lon_lat(user, night_record)
        if lon_lat !=0:
            aver_night_record[user] = lon_lat    
    return aver_night_record


# In[11]:


#2.7 read gps data within one month
#input1: month = "08", "09"  
#input2: user_dict = {int(user):0, ...}
#input3: night_hour = [[22, 23], [0, 1, 2, 3, 4, 5]]
#input4: rlevel = {"xxx": [[0,0,...,0], [0,0,...,0]]}
#input5: threshold
#output: rlevel_output, n_zero_list, n_out_list, n_in_list
def read_gps_within_month(month, user_dict, night_hour, rlevel, threshold):
    n_in_list, n_out_list, n_zero_list = list(), list(), list()
    n_user = len(user_dict)
    
    if month == "08":
        n_day = 31-14
    else:
        n_day = 30    
    
    rlevel_output = rlevel
    for day in range(n_day):
        time1 = time.time()
        start_day = day + 1               #1, 2, ...., 31
        if month == "08":
            start_day = start_day + 14
        print ("start_day: ", start_day)
        aver_night_record = compute_centroid_night_point(month, user_dict, night_hour, start_day)
        
        n_in, n_out, n_zero = 0, 0, 0
        for user in user_dict:
            if len(aver_night_record[user]) == 0:
                 n_zero += 1
            else: 
                if rlevel[user][day] == 1:
                    distance = compute_distance(aver_night_record[user], user_home[user])
                    if distance > threshold:
                        rlevel_output[user][day] = 0.0
                        n_out += 1        
        n_in = n_user-n_zero-n_out
        print ("n_in, n_out, n_zero", n_in, n_out, n_zero)
        n_in_list.append(n_in)
        n_out_list.append(n_out)
        n_zero_list.append(n_zero)
        time2 = time.time()
        print ("time: ", time2-time1) 
        print ("---------------------------------------------------------------")
    return rlevel_output, n_in_list, n_out_list, n_zero_list 


# In[12]:


#2.8 initialize the feature level
rlevel = dict()  #r: recovery
for user in user_dict:
    rlevel[user] = [1.0 for i in range(31-14)]
print (len(rlevel))
print (df["id"][0])


# In[13]:


rlevel, n_in_list_8, n_out_list_8, n_zero_list_8 = read_gps_within_month("08", user_dict, night_hour, rlevel, threshold)


# In[14]:


out = {"rlevel":rlevel, "in": n_in_list_8, "out": n_out_list_8, "zero": n_zero_list_8}


# In[15]:


output_path = sim_folder + "/data/home/"
with open(output_path + "feature_8_mean.json", "w") as outfile:
    json.dump(out, outfile)


# In[ ]:





# In[ ]:




