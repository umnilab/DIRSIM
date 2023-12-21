#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Validate simulation results and real-world recovery


# In[2]:


import os
import json
import time
import numpy as np
import matplotlib.pyplot as plt


# In[3]:


#0. folder
#1. read the real-world recovery
#2. read simulation results
#3. draw figures


# # 0. folder

# In[4]:


#home
folder = "/home/umni2/a/umnilab/users/xue120/umni4/"
sim_folder = folder + "2023_abm/PostDisasterSim/"
home_node = sim_folder + "data/home/valid_user_rms.json"
home_8 = sim_folder + "data/home/feature_8_mean.json"
home_9 = sim_folder + "data/home/feature_9_mean.json"

#POI
poi = sim_folder + "data/poi/poi_feature.json"

#water
water = sim_folder + "data/water/physical_60.json"

#Simulated results
sim_home = sim_folder + "results/base/output_home.json"
sim_home_value = sim_folder + "results/base/output_home_value.json"

sim_poi = sim_folder + "results/base/output_poi.json"
sim_poi_value = sim_folder + "results/base/output_poi_value.json"


# # 1. read the real-world recovery

# In[5]:


#read home
with open(home_8, "r") as f:
    df_home_8 = json.load(f)  
with open(home_9, "r") as f:
    df_home_9 = json.load(f)
n_user = len(df_home_8["rlevel"])
#{'-8477737084538322842': [1, 2, 3, ..., 31]}
print (n_user)
    
#read POI
with open(poi, "r") as f:
    df_poi = json.load(f)
    #{"sg:1daa7da8d5064fcbba3ed8afb2bd1a02": [[1,2,...,31],[1,2,...,30],[1,2,...,31]]}
n_poi = len(df_poi)    
print (n_poi)

#read water
water_data = json.load(open(water))
water_seq = {"Harris County": water_data["ha"], "Fort Bend County": water_data["fb"],\
            "Brazoria County": water_data["br"], "Galveston County": water_data["ga"],\
            "Jefferson County": water_data["jf"]}
print (len(water_seq["Harris County"]))


# # 2. read generated values

# In[6]:


#read simulated home
with open(sim_home, "r") as f:
    df_sim_home = json.load(f) 
user_county = df_sim_home["county"]
print (len(user_county))
#{'-8477737084538322842': 'Harris County',
# '-180844057206980504': 'Harris County'

with open(sim_home_value, "r") as f:
    df_sim_home_value = json.load(f) 
print (len(df_sim_home_value))
#{"0":{'-8477737084538322842': 1.0,'-180844057206980504': 0.0, ...}}


# In[7]:


#read simulated poi
with open(sim_poi, "r") as f:
    df_sim_poi = json.load(f) 
poi_county = df_sim_poi["county"]
print (len(poi_county))
#{'sg:1daa7da8d5064fcbba3ed8afb2bd1a02': 'Harris County',
# 'sg:22a5c6aeb2594a5590101738f2aab61e': 'Harris County',

with open(sim_poi_value, "r") as f:
    df_sim_poi_value = json.load(f) 
print (len(df_sim_poi_value))
#{"0":{'sg:1daa7da8d5064fcbba3ed8afb2bd1a02': 1.0,
#      'sg:22a5c6aeb2594a5590101738f2aab61e': 0.0,


# # 3. draw the figure

# In[8]:


def compute_k_days_average(ylist, k):
    a = int((k-1)/2)
    b = a+1
    n = len(ylist)
    ylist_new = list()
    for i in range(len(ylist)):
        entries = ylist[max(0, i-a): min(n, i+b)]
        ylist_new.append(np.mean(entries))
    return ylist_new


# # 3.1 Home

# # Real

# In[9]:


home_8_average = np.mean([np.array(df_home_8["rlevel"][user]) for user in df_home_8["rlevel"]], axis=0)
home_9_average = np.mean([np.array(df_home_9["rlevel"][user]) for user in df_home_9["rlevel"]], axis=0)
home_8_9 = list(home_8_average) + list(home_9_average)


# In[10]:


y_home = compute_k_days_average(home_8_9, 7)
#y_home = home_8_9


# In[11]:


y_home_select = y_home[15:]
n_home_select = len(y_home_select)
x_home_select = [i for i in range(n_home_select)]


# # Simulated

# In[12]:


y_home_sim = list()
for i in range(31):
    home_value_dict = df_sim_home_value[str(i)]
    average_home_value = np.mean(np.array(list(home_value_dict.values())))
    y_home_sim.append(average_home_value)
x_home_sim =  [i for i in range(len(y_home_sim))]


# # Figure

# In[13]:


plt.figure(figsize=(2.5,2),dpi=300)
l1 = plt.scatter(x_home_select, y_home_select, c="black", s=12, marker="x", label='Real')
l2 = plt.plot(x_home_sim, y_home_sim, color="red", linestyle='-',\
              marker="o", linewidth=1, markersize=2.0, label='Simulated')
my_x_ticks = [0, 10, 20, 30]
plt.xticks(my_x_ticks)
plt.xticks(fontsize = 11)
plt.xlabel('Days since Aug. 30, 2017', fontsize = 11)

my_y_ticks = np.arange(0.90, 0.95, 0.01)
plt.yticks(my_y_ticks)
plt.yticks(fontsize = 11)
plt.ylabel("Recovery level", fontsize = 11)

plt.title("Human layer", fontsize = 11)
plt.legend(loc=4, fontsize=11)
#plt.grid()
#plt.savefig('real_1_1.pdf',bbox_inches = 'tight')
plt.savefig('vai_human.pdf',bbox_inches = 'tight')
plt.show()


# # 3.2 POI

# # Real

# In[14]:


poi_8 = np.mean([np.array(df_poi[poi][0]) for poi in df_poi], axis=0)
poi_9 = np.mean([np.array(df_poi[poi][1]) for poi in df_poi], axis=0)
poi_10 = np.mean([np.array(df_poi[poi][2]) for poi in df_poi], axis=0)
poi_8_9_10 = list(poi_8) + list(poi_9) + list(poi_10)


# In[15]:


poi_pre_average = np.mean(poi_8_9_10[14:14+7])
print (poi_pre_average)


# In[16]:


y_poi = compute_k_days_average(np.array(poi_8_9_10[0:-3])/poi_pre_average, 7)
#y_poi = np.array(poi_8_9_10)/poi_pre_average


# In[17]:


y_poi_select = y_poi[29:]
n_poi_select = len(y_poi_select)
x_poi_select = [i for i in range(n_poi_select)]


# # Simulated

# In[18]:


y_poi_sim = list()
for i in range(60):
    poi_value_dict = df_sim_poi_value[str(i)]
    average_poi_value = np.mean(np.array(list(poi_value_dict.values())))
    y_poi_sim.append(average_poi_value)
x_poi_sim =  [i for i in range(len(y_poi_sim))]


# # Figure

# In[19]:


plt.figure(figsize=(4,2),dpi=300)
l1 = plt.scatter(x_poi_select, y_poi_select, c="black", marker="x", s=12, label='Real')
l2 = plt.plot(x_poi_sim, y_poi_sim, color="dodgerblue", linestyle='-',\
              marker="o", linewidth=1, markersize=2.0, label='Simulated')
my_x_ticks = [0, 10, 20, 30, 40, 50, 60]
plt.xticks(my_x_ticks)
plt.xticks(fontsize = 11)
plt.xlabel('Days since Aug. 30, 2017', fontsize = 11)

my_y_ticks = np.arange(0.60, 1.21, 0.20)
plt.yticks(my_y_ticks)
plt.yticks(fontsize = 11)
plt.ylabel("Recovery level", fontsize = 11)

plt.title("Social infrastructure layer", fontsize = 11)
plt.legend(loc=4, fontsize=11)
#plt.grid()
#plt.savefig('real_1_1.pdf',bbox_inches = 'tight')
plt.savefig('vali_social.pdf',bbox_inches = 'tight')
plt.show()


# # 3.3 Water

# In[20]:


water_average = np.mean([np.array(water_seq[county]) for county in water_seq], axis=0)
n_water = len(water_average)
x_water = [i for i in range(n_water)]


# In[21]:


plt.figure(figsize=(4,2),dpi=300)
l1 = plt.scatter(x_water, water_average, color="gold", marker="*", s=12, label='Physical infrastructures')

my_x_ticks = [0, 10, 20, 30, 40, 50, 60]
plt.xticks(my_x_ticks)
plt.xticks(fontsize = 10)
plt.xlabel('Days since Aug. 30, 2017', fontsize = 10)

my_y_ticks = np.arange(0.50, 1.21, 0.20)
plt.yticks(my_y_ticks)
plt.yticks(fontsize = 10)
plt.ylabel("Recovery level", fontsize = 10)

#plt.title("Recovery curves of Physical infra", fontsize = 10)
plt.legend(loc=4, fontsize=10)
#plt.grid()
#plt.savefig('real_1_1.pdf',bbox_inches = 'tight')
#plt.savefig('sg_peak4_21_21_1feature_0005.pdf',bbox_inches = 'tight')
plt.show()


# In[ ]:





# In[ ]:




