#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.
#Simulator: PostDisasterSim.
#Authors: Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia,\
#Tong Yao, and Satish V. Ukkusuri.


# In[2]:


import time
import json
import mesa
import numpy as np
import random as random 
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import pyplot as plt


# In[3]:


#1. functions.
#2. read home, read poi, read electricity.
#3. home agent, POI agent, electricity agent, and threelayernetwork.
#4. main.


# In[4]:


#user: 0. Harris County.
#user: 1. Fort Bend County.
#user: 2. Brazoria County.
#user: 3. Galveston County.
#user: 4. Jefferson County.


# # 1. functions.

# In[5]:


#function 1.
def interpolate(sample_data):
    output_data = [0.0 for i in range(31)]
    output_data[0] = (2.0*sample_data[1]+sample_data[0])/3.0                             
    output_data[1] = sample_data[1]               #Sept 2 
    output_data[5] = sample_data[2]               #Sept 6
    output_data[29] = sample_data[3] 
    #Sept 30   
    list1 = [2,3,4]
    list2 = [6+i for i in range(25)]
    for term in list1:
        output_data[term] = output_data[1] + (output_data[5] - output_data[1])*(term - 1)/(5-1)
    for term in list2:
        if term !=29:
            output_data[term] = output_data[5] + (output_data[29] - output_data[5])*(term - 5)/(29-5)
    return output_data


# In[6]:


#function 2.
def v_return(q_race, q_house, q_human, q_social, q_physical):
    f = -3.800 + 0.971*q_race + 1.303*q_house + 2.876*q_human - 2.781*q_social + 2.276*q_physical
    return_value = 1.0/(1.0 + np.exp(-1.0 * f))
    return return_value


# In[7]:


#function 3.
def calculate_new_human_value(day, df_user_race, df_user_house, df_user_value,                              df_user_neighbor, df_poi_value, df_user_county, electricity_sequence):
    new_value = {key: 0.0 for key in df_user_value}
    for county_idx in new_value:
        human_value = df_user_value[county_idx]
        poi_value = df_poi_value[county_idx]
        county_value = electricity_sequence[df_user_county[county_idx]][day]
        regression_result = v_return(df_user_race[county_idx], df_user_house[county_idx],                                     human_value, poi_value, county_value)
        term = max([np.min([df_user_value[county_idx]+regression_result*0.01,1.0]),0.0])
        if term >= 0.0:
            new_value[county_idx] = term
    return new_value


# In[8]:


#function 4.
def calculate_new_POI_value(day, df_poi_value, df_poi_neighbor, df_poi_county,electricity_sequence):
    beta_s_all = {"Harris County": 1.076, "Fort Bend County": 0.481, "Brazoria County": 0.486, "Galveston County": 0.486, "Jefferson County": 0.486}
    beta_s_s_all = {"Harris County": -0.214, "Fort Bend County": -0.156, "Brazoria County": 1.065, "Galveston County": 1.065, "Jefferson County": 1.065}
    beta_p_s_all = {"Harris County": -0.823, "Fort Bend County": -0.771, "Brazoria County": -0.165, "Galveston County": -0.165, "Jefferson County": -0.165}
    Ks = 0.85
    Ksother = 0.85
    
    new_value = {key:0.0 for key in df_poi_value}
    idx = 0
    #print ("df_poi_value", df_poi_value)
    for key in new_value:
        #print (df_poi_value[key])
        beta_s, beta_s_s, beta_p_s =            beta_s_all[df_poi_county[key]], beta_s_s_all[df_poi_county[key]],            beta_p_s_all[df_poi_county[key]]
        term_1 = beta_s * df_poi_value[key] * (1.0 - df_poi_value[key]*1.0/Ks)/12.0
        
        term_2 = beta_s_s * 1.0 * df_poi_value[key]*(1.0 - df_poi_value[key]/Ksother)/12.0
        
        county_value = electricity_sequence[df_poi_county[key]][day]
        term_3 = beta_p_s*county_value * (1.0-county_value*1.0)/1.0
        new_value[key] = max(min(df_poi_value[key]-term_1-term_2-term_3, 1.0), 0)
    return new_value  


# # 2. read home, POI, and electricity.

# In[9]:


def read_home_data(user_path_1, user_path_2, user_path_3):
    #1. read data
    with open(user_path_1, "r") as f1:
        df_user_node= json.load(f1)   
        #node. #43,147 nodes. #['id', 'lon', 'lat', 'county']
        
    with open(user_path_2, "r") as f2: 
        df_user_edge = json.load(f2)   
        #edge. #2,308,629 edges.  #['29378_30839', '26745_27557', ..., '24584_28503',]
        
    with open(user_path_3, "r") as f3:
        df_user_value = json.load(f3)
        #[[1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1], \
        #[1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1]]
    
    #2. extract information
    county_list = ["Harris County", "Fort Bend County", "Brazoria County",                   "Galveston County", "Jefferson County"]
    county_idx_dict = {county_list[i]: i for i in range(5)}
    idx_county_dict = {i: county_list[i] for i in range(5)}
    county_user_value = {i: list() for i in range(5)}
    
    for i in range(len(df_user_node["id"])):
        idx = df_user_node["id"][i]
        ac_value = df_user_value[idx]
        county = df_user_node["county"][i]
        
        county_idx = county_idx_dict[county]                  #0,1,2,3,4,5
        county_user_value[county_idx].append(ac_value[1][0])
      
    df_user_value_order_start = dict()
    for idx in county_user_value:
        df_user_value_order_start[idx] = [float(np.mean(county_user_value[idx]))]
        
    #3. set the race and housing for each user
    ratio_race, ratio_house = 0.485, 0.569
    for idx in df_user_value_order_start:
        df_user_value_order_start[idx].append(ratio_race)
        df_user_value_order_start[idx].append(ratio_house)
    
    #4. extract county, value, race, house for users
    #input: df_user_value_order_start
    #output: df_user_county, df_user_value, df_user_race, df_user_house
    df_user_county = idx_county_dict 
    df_user_value = {key: df_user_value_order_start[key][0] for key in df_user_value_order_start}
    df_user_race = {key: df_user_value_order_start[key][1] for key in df_user_value_order_start}
    df_user_house = {key: df_user_value_order_start[key][2] for key in df_user_value_order_start}
    
    df_user_neighbor = {0: 123, 1: 36, 2: 17, 3: 32, 4: 37}
        
    return df_user_county, df_user_value, df_user_race, df_user_house, df_user_neighbor


# In[10]:


def read_poi_data(poi_path_1, poi_path_2, poi_path_3):
    #1. read poi data
    with open(poi_path_1, "r") as f1:  #90513 nodes  #['id', 'lon', 'lat', 'county']
        df_poi_node= json.load(f1)

    with open(poi_path_2, "r") as f2:
        df_poi_edge = json.load(f2)

    with open(poi_path_3, "r") as f3:
        df_poi_value = json.load(f3)
    
    #2. extract information
    county_list = ["Harris County", "Fort Bend County", "Brazoria County",                   "Galveston County", "Jefferson County"]
    county_idx_dict = {county_list[i]: i for i in range(5)}
    idx_county_dict = {i: county_list[i] for i in range(5)}
    county_poi_value = {i: list() for i in range(5)}
    
    for i in range(len(df_poi_node["id"])):
        idx = df_poi_node["id"][i]
        ac_value = df_poi_value[idx]
        county = df_poi_node["county"][i]

        county_idx = county_idx_dict[county]                  #0,1,2,3,4,5
        county_poi_value[county_idx].append(min(ac_value[0][-1]/(0.01+ac_value[1][0]),1.0))
 
    df_poi_value_order_start = dict()
    for idx in county_poi_value:
        df_poi_value_order_start[idx] = float(np.mean(county_poi_value[idx]))
    
    df_poi_county = idx_county_dict 
    df_poi_value = {key: df_poi_value_order_start[key] for key in df_poi_value_order_start}
    
    #3. obtain the neighborhood    
    df_poi_neighbor = {0: 139, 1: 108, 2: 80, 3: 79, 4: 70}
    
    return df_poi_county, df_poi_value, df_poi_neighbor


# In[11]:


def read_electricity_data():
    electricity_curve = {"Harris County": [0.779, 0.835, 0.874, 0.884],                    "Fort Bend County": [0.872, 0.873, 0.886, 0.906],                    "Brazoria County": [0.841, 0.931, 0.947, 1.000],                    "Galveston County": [0.753, 0.792, 0.813, 0.844],                    "Jefferson County": [0.883, 0.600, 0.670, 0.679]}
    
    electricity_sequence = {"Harris County": interpolate(electricity_curve["Harris County"]),                       "Fort Bend County": interpolate(electricity_curve["Fort Bend County"]),                       "Brazoria County": interpolate(electricity_curve["Brazoria County"]),                       "Galveston County": interpolate(electricity_curve["Galveston County"]),                       "Jefferson County": interpolate(electricity_curve["Jefferson County"])}
    return electricity_sequence


# # 3. home agent, POI agent, electricity agent.

# In[12]:


#Class 1: home agent layer
class HomeAgentLayer(mesa.Agent):
    """An agent with fixed initial activity value."""
    def __init__(self, df_user_county, df_user_value,                 df_user_race, df_user_house,                  df_user_neighbor, electricity_sequence):
        self.user_county = df_user_county
        self.user_value = df_user_value
        self.user_race = df_user_race
        self.user_house = df_user_house
        self.user_neighbor = df_user_neighbor
        self.home_day = 1
        self.electricity_sequence = electricity_sequence
        
    def step(self, poi_value):
        new_value = calculate_new_human_value(self.home_day, self.user_race, self.user_house,                                   self.user_value, self.user_neighbor,                                     poi_value, self.user_county, self.electricity_sequence)
        self.user_value = new_value    
        self.home_day += 1
    def print_activity_value(self):
        return (np.mean(list(self.user_value.values())))


# In[13]:


#Class 2: POI agent layer
class POIAgent(mesa.Agent):
    def __init__(self, df_poi_county, df_poi_value, df_poi_neighbor, electricity_sequence):
        self.poi_county = df_poi_county
        self.poi_value = df_poi_value
        self.poi_neighbor = df_poi_neighbor
        self.poi_day = 1
        self.electricity_sequence = electricity_sequence
        
    def step(self):
        new_value = calculate_new_POI_value(self.poi_day, self.poi_value,                                            self.poi_neighbor, self.poi_county, self.electricity_sequence)
        self.poi_value = new_value 
        self.poi_day += 1
        
    def print_activity_value(self):
        return (np.mean(list(self.poi_value.values())))


# # 4. three-layer network.

# In[14]:


#Class: three layer network agent
class ThreeLayerNetworkAgent(mesa.Model):
    def __init__(self, df_user_county, df_user_value, df_user_race,                 df_user_house,  df_user_neighbor, 
                 df_poi_county, df_poi_value, df_poi_neighbor, electricity_sequence):
        self.humanLayer = HomeAgentLayer(df_user_county, df_user_value,                                         df_user_race, df_user_house,df_user_neighbor, electricity_sequence)
        self.socialLayer = POIAgent(df_poi_county, df_poi_value,df_poi_neighbor, electricity_sequence)
        self.day = 1
        self.electricity_sequence = electricity_sequence

    def step(self):
        self.socialLayer.step()
        self.humanLayer.step(self.socialLayer.poi_value)
        self.day += 1
  
    def show_current_value(self):
        human_value = self.humanLayer.print_activity_value()
        poi_value = self.socialLayer.print_activity_value()*1.0
        electricity_value = np.sum([self.electricity_sequence[key][self.day]*1.0/5.0                                    for key in self.electricity_sequence])
        human_value_collection = self.humanLayer.user_value
        poi_value_collection = self.socialLayer.poi_value
        
        print("Day is " +str(self.day) + ".")
        print("My average electricity value is " + str(electricity_value) + ".")
        print("My average home value is " + str(human_value) + ".")
        print("My average poi value is " + str(poi_value) + ".")
        return human_value, poi_value, electricity_value, human_value_collection, poi_value_collection


# # 5. main.

# In[15]:


def main(user_path_1, user_path_2, user_path_3, poi_path_1, poi_path_2, poi_path_3):
    time1 = time.time()
    human_value, poi_value, electricity_value = [0.0 for i in range(30)], [0.0 for i in range(30)], [0.0 for i in range(30)]
    
    #1. read the data
    df_user_county, df_user_value, df_user_race, df_user_house, df_user_neighbor =        read_home_data(user_path_1, user_path_2, user_path_3)
    print ("finish loading home data")
    
    df_poi_county, df_poi_value, df_poi_neighbor =        read_poi_data(poi_path_1, poi_path_2, poi_path_3)
    print ("finish loading POI data")
    
    electricity_sequence = read_electricity_data()
    print ("finish loading electricity data")
    
    #2. build the network
    model = ThreeLayerNetworkAgent(df_user_county, df_user_value, df_user_race,                 df_user_house,  df_user_neighbor, 
                 df_poi_county, df_poi_value, df_poi_neighbor,electricity_sequence )
    print ("finish building the three-layer network")
    time2 = time.time()
    print ("time until now: ", time2- time1)
    
    #3. simulate the Septmber.
    print ("start simulating the recovery from Sept. 1 to Sept. 30, 2017")
    for i in range(30):
        print ("--------------------------------")
        print ("--------------------------------")
        print ("day: ", i+1)
        human_value[i], poi_value[i], electricity_value[i],human_value_collection, poi_value_collection            = model.show_current_value()

        print ("--------------------------------")
        model.step()
        time2 = time.time()
        print ("time until now: ", time2- time1)
    return human_value, poi_value, electricity_value 


# In[16]:


if __name__ == '__main__':
    loc = "/data/xue120/2022_abm/6-simulation/"
    home_node = loc + "code_4_5_6/code_4_output_house.json"
    home_edge = loc + "code_4_5_6/code_5_output_house_edge.json"
    home_activity = loc + "code_4_5_6/code_6_human_activity.json"
    
    poi_node = loc + "code_1_2_3/code_1_output_poi.json"
    poi_edge = loc + "code_1_2_3/code_2_output_poi_adj.json"
    poi_activity = loc + "code_1_2_3/code_3_output_poi_activity.json"

    main(home_node, home_edge, home_activity, poi_node, poi_edge, poi_activity)


# In[ ]:





# In[ ]:




