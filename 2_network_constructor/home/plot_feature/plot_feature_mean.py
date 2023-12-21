#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import json
import time
import numpy as np
from math import sin, cos, sqrt, atan2, radians
import matplotlib.pyplot as plt


# In[2]:


# 0. folder
# 1. read dara
# 2. check recovery curves
# 3. check recovery curves for different counties


# # 0. folder

# In[3]:


#valid user
folder = "/home/umni2/a/umnilab/users/xue120/umni4/"
sim_folder = folder + "2023_abm/PostDisasterSim/"
home_node = sim_folder + "data/home/valid_user_rms.json"
rlevel_8 = sim_folder + "data/home/feature_8_mean.json"
rlevel_9 = sim_folder + "data/home/feature_9_mean.json"


# # 1. read data

# In[4]:


#read user homes
with open(home_node, "r") as f:
    df = json.load(f)

user_list = list(df["id"])  #v: valid
user_int_list = [int(user) for user in user_list]
n_user = len(user_int_list) 
print(n_user)

user_dict = {user:0 for user in user_int_list}
user_county = {user_int_list[i]: df["county"][i] for i in range(n_user)}


# In[5]:


with open(rlevel_8, "r") as f:
    df_8 = json.load(f)
with open(rlevel_9, "r") as f:
    df_9 = json.load(f)


# In[6]:


rlevel = dict()  #r: recovery
for user in user_dict:
    rlevel[user] = [[1.0 for i in range(31-14)], [1.0 for i in range(29)]]
print (len(rlevel))
print (df["id"][0])


# In[7]:


for user in user_dict:
    if str(user) in df_8["rlevel"]:
        rlevel[user][0] = df_8["rlevel"][str(user)]
    if str(user) in df_9["rlevel"]:
        rlevel[user][1] = df_9["rlevel"][str(user)]


# In[8]:


n_in_list_8, n_out_list_8, n_zero_list_8 = df_8["in"], df_8["out"], df_8["zero"]
n_in_list_9, n_out_list_9, n_zero_list_9 = df_9["in"], df_9["out"], df_9["zero"]


# In[9]:


n_in_all = n_in_list_8 + n_in_list_9
n_out_all = n_out_list_8 + n_out_list_9
n_zero_all = n_zero_list_8 + n_zero_list_9


# # 2. check recovery curves

# In[10]:


august_r = [[rlevel[idx][0][i] for i in range(31-14)] for idx in rlevel]
sept_r = [[rlevel[idx][1][i] for i in range(29)] for idx in rlevel]
august_aver = np.sum(august_r, axis=0)
sept_aver = np.sum(sept_r, axis=0)


# In[11]:


all_aver = list(august_aver) + list(sept_aver)
n_all = len(all_aver)

x = [i for i in range(n_all)]
y = all_aver

plt.figure(figsize=(10,3),dpi=75)
plt.scatter(x, y, s=16, c='orangered',edgecolors ='black', marker='o', linewidths=0.8, zorder=30)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.show()


# In[12]:


def compute_k_days_average(ylist, k):
    a = int((k-1)/2)
    b = a+1
    n = len(ylist)
    ylist_new = list()
    for i in range(len(ylist)):
        entries = ylist[max(0, i-a): min(n, i+b)]
        ylist_new.append(np.mean(entries))
    return ylist_new


# In[13]:


x = [i for i in range(n_all)]
y = [y[i]/n_user for i in range(n_all)]
y_new = compute_k_days_average(y, 7)

plt.figure(figsize=(10,4),dpi=75)
plt.scatter(x, y, s=16,  c='orangered',edgecolors ='black', marker='o', linewidths=0.8, zorder=30)
plt.plot(x, y_new, "s-", color= "red", linewidth=1, markersize=4)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.show()


# In[14]:


# In all
plt.figure(figsize=(10,3),dpi=75)
x = [i for i in range(n_all)]
plt.scatter(x, n_in_all, s=16, c='orangered',edgecolors ='black', marker='o', linewidths=0.8, zorder=30)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.show()


# In[15]:


# Out all
plt.figure(figsize=(10,3),dpi=75)
x = [i for i in range(n_all)]
plt.scatter(x, n_out_all, s=16, c='orangered',edgecolors ='black', marker='o', linewidths=0.8, zorder=30)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.show()


# In[16]:


# Zero
plt.figure(figsize=(10,3),dpi=75)
x = [i for i in range(n_all)]
plt.scatter(x, n_zero_all, s=16, c='orangered',edgecolors ='black', marker='o', linewidths=0.8, zorder=30)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.show()


# # 3. check recovery curves for different counties

# In[17]:


# extract the rlevel for the subset of counties.

# user_county = {user:county}
# county_name: 'Brazoria County', 'Fort Bend County', 'Galveston County', 'Harris County', 'Jefferson County'
# rlevel: 46460; month_idx: 0 and 1; day: 0-16; 0-30; rlevel[user][month_idx][day]
def extract_value_for_county(user_county, county_name, rlevel):
    sub_rlevel = dict()
    for user in rlevel:
        if user_county[user] == county_name:
            sub_rlevel[user] = rlevel[user]
    
    august_r = [[sub_rlevel[idx][0][i] for i in range(31-14)] for idx in sub_rlevel]
    sept_r = [[sub_rlevel[idx][1][i] for i in range(29)] for idx in sub_rlevel]
    august_aver = np.mean(august_r, axis=0)
    sept_aver = np.mean(sept_r, axis=0)
    all_aver = list(august_aver) + list(sept_aver)
    return all_aver


# In[18]:


def plot_recovery_for_each_county(county_name):
    all_aver = extract_value_for_county(user_county, county_name, rlevel)
    x = [i for i in range(n_all)]
    y = [all_aver[i] for i in range(n_all)]
    y_new = compute_k_days_average(y, 7)
    print (round(np.mean(y), 4))
    plt.figure(figsize=(10,4),dpi=75)
    plt.scatter(x, y, s=16,  c='orangered',edgecolors ='black', marker='o', linewidths=0.8, zorder=30)
    plt.plot(x, y_new, "s-", color= "red", linewidth=1, markersize=4)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.title(county_name, fontsize=18)
    plt.show()


# In[19]:


plot_recovery_for_each_county("Harris County")


# In[20]:


plot_recovery_for_each_county("Fort Bend County")


# In[21]:


plot_recovery_for_each_county("Brazoria County")


# In[22]:


plot_recovery_for_each_county("Galveston County")


# In[23]:


plot_recovery_for_each_county("Jefferson County")


# In[ ]:





# In[ ]:




