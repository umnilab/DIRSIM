#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os 
import time
import json
import pyarrow
import numpy as np
import pandas as pd
import geopandas as gpd
import pyarrow.parquet as pq
from shapely.geometry import Point
import warnings
warnings.filterwarnings('ignore')


# In[2]:


#input: /home/umni2/a/umnilab/data/quadrant/Texas/2017/07/
#output: /home/umni2/a/umnilab/users/xue120/umni4/2023_abm/PostDisasterSim/mob_data/


# In[3]:


#raw mobility data
#Index(['uid', 'lon', 'lat', 'ts', 'error']
#uid        -9222942879714521987
#lon      [-95.36419, -95.35717]
#lat      [29.470078, 29.465984]
#ts           [28996.0, 29253.0]
#error                [nan, nan]

#1. read the shapefile of the five counties
#2. conduct spatial join and generate new json files
#id, lon, lat, ts.


# # 0. folder

# In[4]:


folder = "/home/umni2/a/umnilab/"
folder_mob = folder + "data/quadrant/Texas/2017/" 
df_aug = os.listdir(folder_mob + "08/")
print (df_aug)
print (len(df_aug))

folder_census = folder + "users/xue120/umni4/2022_abm/0-TX-shapefile-2/"
file_census = "Tx_Census_CntyBndry_Detail_TIGER500k.shp"
path_census = os.path.join(folder_census, file_census) 

folder_sim =  folder + "users/xue120/umni4/2023_abm/PostDisasterSim/mob_data/"


# # 1. read the shapefile of the five counties

# In[5]:


tx = gpd.read_file(path_census) 
df_shp = tx.loc[tx['NAME'].isin(["Harris County", "Fort Bend County", "Brazoria County",\
"Galveston County", "Jefferson County"]), :]
selected_columns = ['NAME', "geometry"]
df_shp = df_shp[selected_columns]


# In[6]:


df_shp.plot()


# In[7]:


df_shp


# # 2. conduct spatial join and generate new json files

# In[8]:


#month: "08"
#(start_day, num_day) = (1, 15); (16, 16); (1, 15); (16, 15)
def extract_gps_in_area(month, df_shp, start_day, num_day):
    if month == "08":
        df_folder, df_day = folder_mob+"08/", df_aug 
        
    for idx in range(num_day):
        print ("day: ", start_day+idx)
        
        time0 = time.time()
        #1. read the mobility data
        table = pq.read_table(df_folder + df_day[start_day-1+idx])
        df = table.to_pandas()
        n_user = len(df)
        print ("n_user: ", n_user)
        time1 = time.time()
        print ("time 1, read mob, ", round(time1-time0, 3))
        
        #2. read the mob data
        lon_all, lat_all, ts_all, id_all = list(), list(), list(), list()
        
        df_lon_list = [list(df["lon"][i]) for i in range(n_user)]
        df_lat_list = [list(df["lat"][i]) for i in range(n_user)]
        df_ts_list = [list(df["ts"][i]) for i in range(n_user)]
        
        lon_all = [lon for item in df_lon_list for lon in item]
        lat_all = [lat for item in df_lat_list for lat in item]
        ts_all = [ts for item in df_ts_list for ts in item]
        
        df_uid_list = list(df["uid"])
        n_df_list = [len(df["lon"][i]) for i in range(n_user)]
        id_all = [df_uid_list[i] for i in range(n_user) for j in range(n_df_list[i])]   
        n_point = len(id_all)
        print ("n_point: ", n_point)
        time2 = time.time()
        print ("time 2, extract list, ", round(time2-time0, 3))
        
        #3. build the mob shapefile
        data = {"lon": lon_all, "lat": lat_all, "ts": ts_all, "uid": id_all}
        home_df = pd.DataFrame(data)
        home_geo = [Point(xy) for xy in zip(lon_all, lat_all)]
        home_gpd = gpd.GeoDataFrame(home_df, geometry=home_geo, crs='EPSG:4326')
        time3 = time.time()
        print ("time 3, generate geodataframe, ", round(time3-time0,3))
            
        #4. conduct the spatial join
        point_in_area = gpd.sjoin(home_gpd, df_shp, how='inner', op='within')
        time4 = time.time()
        print ("time 4, spatial join, ", round(time4-time0,3))

        #5. output the point
        n = len(point_in_area)
        id_set = set(list(point_in_area["uid"]))
        uid_list, lon_list, lat_list, ts_list =\
            list(point_in_area["uid"]), list(point_in_area["lon"]), \
            list(point_in_area["lat"]), list(point_in_area["ts"])
        
        id_lon_lat_ts = {user:[[], [], []] for user in id_set}
        #lon, lat, ts
        for i in range(n):
            user, lon, lat, ts = uid_list[i], lon_list[i], lat_list[i], ts_list[i]
            id_lon_lat_ts[user][0].append(lon)
            id_lon_lat_ts[user][1].append(lat)
            id_lon_lat_ts[user][2].append(ts)
        print ("n_in_point, ", n)
        time5 = time.time()
        print ("time 5, extract list, ", round(time5-time0,3))
        
        output_path = folder_sim + month + "/"
        with open(output_path + str(start_day+idx) + ".json", "w") as outfile:
            json.dump(id_lon_lat_ts, outfile)
        time6 = time.time()
        print ("time 6, generate json, ", round(time6-time0,3))
        print ("-------------have processed one day's data------------")


# In[9]:


extract_gps_in_area("08", df_shp, 15, 7)


# # Test

# In[3]:


import random
import json
import matplotlib.pyplot as plt


# In[4]:


folder = "/home/umni2/a/umnilab/users/xue120/umni4/"
gps = "2023_abm/PostDisasterSim/mob_data/"
ts_all = list()
for idx in ["15", "16", "17", "18", "19", "20", "21"]:
    path = folder + gps + "08" + "/" + idx + ".json"
    with open(path, "r") as f:
        df = json.load(f)                    
        f.close()
    ts_list = [df[user][2] for user in df]
    ts_list_all = [i for item in ts_list for i in item]
    ts_all = ts_all + ts_list_all


# In[5]:


sampled_elements = random.sample(ts_list_all, 1000000)


# In[6]:


plt.hist(sampled_elements, bins=96)
plt.show()


# In[ ]:




