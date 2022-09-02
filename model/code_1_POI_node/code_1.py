#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.
#Simulator: PostDisasterSim.
#Authors: Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, and Satish V. Ukkusuri. 


# # code_1: get the simplied POI file.

# In[2]:


import os
import time
import json
import shapely.wkt
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


# # 1. set file locations

# In[3]:


#1. Parameter setting
#1.1 shapefile
folder_census = "/data/xue120/2022_abm/"+"0-TX-shapefile/"
file_census = "Tx_Census_CntyJurisdictional_TIGER.shp" 
path_census = os.path.join(folder_census, file_census) 
df_shapefile = gpd.read_file(path_census) 

#1.2 POI
poi_file_path = "/data/xue120/2022_abm/"+"1-poi-data/geometry.csv"
df_poi = pd.read_csv(poi_file_path)


# # 2. spatial join

# In[4]:


############################2.1-2.3: get point_gpd"############################
#2.1. get the centroid of all POI polygons
#input: df_poi
#output: centroid_list, safegraph_id_list
centroid_list, safegraph_id_list = list(), list()    
safegraph_place_id_list = list(df_poi["safegraph_place_id"])
df_poi_polygon_wkt = df_poi['polygon_wkt']
print ("# row", len(safegraph_place_id_list))
for j in range(len(safegraph_place_id_list)):
    if j % 100000 == 0 :
        print (j)
    point = shapely.wkt.loads(df_poi_polygon_wkt[j]).centroid
    centroid_list.append([point.x, point.y])
    safegraph_id_list.append(safegraph_place_id_list[j])
    
#2.2. get the lon, lat lists of the centroids
#input: centroid_list, safegraph_id_list
#output: lon_sample_list, lat_sample_list, safegraph_id_sample_list
lon_list = [centroid_list[j][0] for j in range(len(centroid_list))]
lat_list = [centroid_list[j][1] for j in range(len(centroid_list))]
lon_sample_list, lat_sample_list, safegraph_id_sample_list  = list(), list(), list()
for i in range(len(lon_list)):
    if lon_list[i] < -93.4 and lon_list[i] > -110:
        if lat_list[i] > 25.0 and lat_list[i] < 36.7:
            lon_sample_list.append(lon_list[i])
            lat_sample_list.append(lat_list[i])
            safegraph_id_sample_list.append(safegraph_id_list[i])
            
#2.3. generate the shapefile consisting of points
#input: lon_sample_list, lat_sample_list, safegraph_id_sample_list
#output: point_gpd 
data = {"lon": lon_sample_list, "lat": lat_sample_list,         "geometry":[0 for i in range(len(lon_sample_list))],        "safegraph_id": safegraph_id_sample_list}
point_df = pd.DataFrame(data, index=[i for i in range(len(lon_sample_list))])
point_crs = {'init':'epsg:4326'} # define coordinate reference system
point_geometry = [Point(xy) for xy in zip(lon_sample_list, lat_sample_list)]
point_gpd = gpd.GeoDataFrame(point_df, crs = point_crs, geometry = point_geometry)

############################2.4: get df_shapefile"############################
#2.4. extract the shapefile of five counties
#output: df_shapefile.
tx = gpd.read_file(path_census) 
df_shapefile = tx.loc[tx['NAME'].isin(["Harris County", "Fort Bend County", "Brazoria County","Galveston County", "Jefferson County"]), :]

######################2.5: append point_gpd to df_shapefile"####################
#2.5. spatial join
#input: point_gpd, df_shapefile
#output: poi_within_tract_result
print ("# poi point: ", len(point_gpd)) 
print ("# shapefile: ", len(df_shapefile))
start_time = time.time()
poi_within_tract_result = gpd.sjoin(point_gpd, df_shapefile, how='inner', op='within')
end_time = time.time()
print ("time: ", end_time - start_time)
print ("# poi point in these zones: ", len(poi_within_tract_result))


# # 3. show statistics, and get final shapefiles

# In[5]:


######################3.1-3.2: show statistics, and get final shapefiles"####################
#3.1. county distribution
#input: poi_within_tract_result
#output1: lon_sample_list_select, lat_sample_list_select 
#output2: county_name
lon_sample_list_select = poi_within_tract_result["geometry"].x 
lat_sample_list_select = poi_within_tract_result["geometry"].y 
county_name =list(poi_within_tract_result["NAME"])
county_name_set = set(county_name)
print (len(county_name))
print ("----------------------------------------")
for i in county_name_set:
    print (i)
    print (county_name.count(i))
    
#3.2. get final shapefiles
#input: poi_within_tract_result
#output: poi_five_county 
column_list = list(poi_within_tract_result.columns)
column_list.remove("lon")
column_list.remove("lat")
column_list.remove("geometry")
column_list.remove("safegraph_id")
column_list.remove("NAME")
poi_within_tract_result.drop(columns=column_list)
poi_five_county_safegraph_id = list(poi_within_tract_result["safegraph_id"])
poi_five_county_lon = list(poi_within_tract_result["lon"])
poi_five_county_lat = list(poi_within_tract_result["lat"])
poi_five_county_county = list(poi_within_tract_result["NAME"])
poi_five_county = {"id": poi_five_county_safegraph_id, "lon": poi_five_county_lon,                   "lat":poi_five_county_lat, "county":poi_five_county_county}


# # 4. save as the json

# In[6]:


with open("code_1_output_poi.json", "w") as outfile:
    json.dump(poi_five_county, outfile)
with open("/data/xue120/2022_abm/"+"6-simulation/Code1_1/code_1_output_poi.json", "r") as f:
    df_poi_data = json.load(f)


# In[ ]:




