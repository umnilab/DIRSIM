#!/usr/bin/env python
# coding: utf-8

# # specify POI nodes

# In[1]:


import os
import json
import shapely.wkt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


# In[2]:


# 1. map POIs to the five counties
# 2. get the POI shapefile
# 3. extract POIs with daily visitor traffic data
# 4. save the POI file                       → "poi.json" under /data/


# # 0. folder

# In[3]:


#shapefile
folder = "/home/umni2/a/umnilab/users/xue120/umni4/"
folder_census = folder + "2022_abm/0-TX-shapefile/"
file_census = "Tx_Census_CntyJurisdictional_TIGER.shp" 
path_census = os.path.join(folder_census, file_census) 

#simulation 
sim_folder = folder + "2023_abm/PostDisasterSim/"

#POI
poi_path = folder +"2022_abm/1-poi-data/geometry.csv"
df_poi = pd.read_csv(poi_path)
print (len(df_poi))

#poi dynamic data
poi = "2022_abm/2-check-poi-data/"
poi_aug, poi_sept, poi_oct = poi+"08/", poi+"09/", poi+"10/"


# # 1. map POIs to the five counties

# In[4]:


#1.1. get the centroid of all POI polygons
#input: df_poi
#output: centroid_list, safegraph_id_list
id_list, centroid_list = list(), list()    
place_id_list = list(df_poi["safegraph_place_id"])
polygon_wkt = df_poi['polygon_wkt']

print ("# row", len(place_id_list))
for i in range(len(place_id_list)):
    if i % 100000 == 0 :
        print (i)
    id_list.append(place_id_list[i])
    point = shapely.wkt.loads(polygon_wkt[i]).centroid
    centroid_list.append([point.x, point.y])
    
#1.2. get the lon, lat lists of the centroids with the five counties
#input: centroid_list, id_list
#output: lon_sample_list, lat_sample_list, safegraph_id_sample_list
lon_list = [centroid_list[i][0] for i in range(len(centroid_list))]
lat_list = [centroid_list[i][1] for i in range(len(centroid_list))]
lon_sample_list, lat_sample_list, id_sample_list  = list(), list(), list()
for i in range(len(lon_list)):
    if lon_list[i] < -93.4 and lon_list[i] > -100.0:
        if lat_list[i] > 25.0 and lat_list[i] < 30.3:
            lon_sample_list.append(lon_list[i])
            lat_sample_list.append(lat_list[i])
            id_sample_list.append(id_list[i])
print(len(lon_list))

#1.3. generate the shapefile consisting of points
#input: lon_sample_list, lat_sample_list, id_sample_list
#output: point_gpd 
n_sample = len(lon_sample_list)
data = {"lon": lon_sample_list, "lat": lat_sample_list, \
        "geometry":[0 for i in range(n_sample)],\
        "safegraph_id": id_sample_list}
point_df = pd.DataFrame(data, index=[i for i in range(n_sample)])
point_crs = {'init':'epsg:4326'} # define coordinate reference system
point_geometry = [Point(xy) for xy in zip(lon_sample_list, lat_sample_list)]
point_gpd = gpd.GeoDataFrame(point_df, crs = point_crs, geometry = point_geometry)

#1.4. extract the shapefile of five counties
#output: df_shapefile.
tx = gpd.read_file(path_census) 
df_shp = tx.loc[tx['NAME'].isin(["Harris County", "Fort Bend County", "Brazoria County",\
"Galveston County", "Jefferson County"]), :]

#1.5. spatial join
#input: point_gpd, df_shapefile
#output: poi_within_tract_result
point_gpd_project = point_gpd.to_crs("EPSG:4326")

print ("#poi: ", len(point_gpd)) 
print ("#shapefile: ", len(df_shp))
poi_within_county = gpd.sjoin(point_gpd_project, df_shp, how='inner', op='within')
print ("#poi: ", len(poi_within_county))


# # 2. get the POI shapefile

# In[5]:


#2.1. county distribution
#input: poi_within_county
#output1: lon_sample_list_select, lat_sample_list_select 
#output2: county_name
lon_sample_list_select = poi_within_county["geometry"].x 
lat_sample_list_select = poi_within_county["geometry"].y 
county_name =list(poi_within_county["NAME"])
county_name_set = set(county_name)
print (len(county_name))
print ("----------------------------------------")
for i in county_name_set:
    print (i)
    print (county_name.count(i))
    
#2.2. get final shapefiles
#input: poi_within_county
#output: poi_five_county 
column_list = list(poi_within_county.columns)
maintain_label = ["lon", "lat", "geometry", "safegraph_id", "NAME"]
for label in maintain_label:
    column_list.remove(label)
poi_within_county.drop(columns=column_list)

poi_safegraph_id = list(poi_within_county["safegraph_id"])
poi_lon = list(poi_within_county["lon"])
poi_lat = list(poi_within_county["lat"])
poi_county = list(poi_within_county["NAME"])
poi = {"id": poi_safegraph_id, "lon": poi_lon, "lat":poi_lat, "county":poi_county}


# # 3. extract POIs with daily visitor traffic data

# In[6]:


#3.1 specify paths
poi_path_8 = folder + poi_aug
df_8 = os.listdir(poi_path_8)
df_8.sort()
df_8 = df_8[1:]    #["core_poi-patterns-part1.csv", ...]

poi_path_9 = folder + poi_sept    
df_9 = os.listdir(poi_path_9) 
df_9.sort()
df_9 = df_9[1:] 

poi_path_10 = folder + poi_oct    
df_10 = os.listdir(poi_path_10) 
df_10.sort()
df_10 = df_10[1:] 
print (len(df_8), len(df_9), len(df_10))


# In[7]:


#3.2 id county
id_county_dict = {poi["id"][i]:poi["county"][i] for i in range(len(poi["id"]))}  
print (len(id_county_dict))


# In[8]:


#3.3 extract poi with visit
#df = df_8, df_9, df_10
#poi_month = poi_aug, poi_sept, poi_oct
#ndays = 31, 30, 31
#county_list = ["Harris County", "Fort Bend County", "Galveston County", "Brazoria County", "Jefferson County"]
def extract_poi_with_visit(df, poi_month, ndays, id_county_dict, county_list):
    poi_with_visit = dict()
    for i in range(len(df)):
        df_poi = pd.read_csv(folder + poi_month + df[i])
        visit_by_day_list = list(df_poi["visits_by_day"])
        id_list = list(df_poi["safegraph_place_id"])
        for k in range(len(visit_by_day_list)):
            visit = visit_by_day_list[k]
            poi_id = id_list[k]
            if poi_id in id_county_dict:                          #valid
                if id_county_dict[poi_id] in county_list:         #five counties
                    if visit == visit:                            #with visits
                        if poi_id not in poi_with_visit:
                            poi_with_visit[poi_id] = 0
    return poi_with_visit


# In[9]:


#3.4
county_list = ["Harris County", "Fort Bend County", "Brazoria County", "Galveston County", "Jefferson County"]
poi_with_visit_8 = extract_poi_with_visit(df_8, poi_aug, 31, id_county_dict, county_list)
poi_with_visit_9 = extract_poi_with_visit(df_9, poi_sept, 30, id_county_dict, county_list)
poi_with_visit_10 = extract_poi_with_visit(df_10, poi_oct, 31, id_county_dict, county_list)

set_1 = set(list(poi_with_visit_8.keys()))
set_2 = set(list(poi_with_visit_9.keys()))
set_3 = set(list(poi_with_visit_10.keys()))
set_common = set_1.intersection(set_2)
set_common = set_common.intersection(set_3)
print (len(set_common))


# In[10]:


#3.5 
poi_safegraph_id_new, poi_lon_new, poi_lat_new, poi_county_new = list(), list(), list(), list()
for i in range(len(poi_safegraph_id)):
    if poi_safegraph_id[i] in set_common:
        poi_safegraph_id_new.append(poi_safegraph_id[i])
        poi_lon_new.append(poi_lon[i])
        poi_lat_new.append(poi_lat[i])
        poi_county_new.append(poi_county[i])
poi_new = {"id": poi_safegraph_id_new, "lon": poi_lon_new, "lat":poi_lat_new, "county":poi_county_new}


# # 4. save the POI file

# In[11]:


poi_loc = sim_folder + "data/poi/poi.json"
with open(poi_loc, "w") as outfile:
    json.dump(poi_new, outfile)
with open(poi_loc, "r") as f:
    df_poi = json.load(f)


# In[12]:


county_name =list(df_poi["county"])
county_name_set = set(county_name)
print (len(county_name))
print ("----------------------------------------")
for i in county_name_set:
    print (i)
    print (county_name.count(i))


# In[ ]:





# In[ ]:




