#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.
#Simulator: PostDisasterSim.
#Authors: Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, and Satish V. Ukkusuri.


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


#function 1. get the neighborhood of human  #["0":["123","456"]]
#input: df_value_order_start, df_edge
#output: df_neighbor
def get_current_neighbor(df_value_order_start, df_edge):
    df_neighbor = {key: list() for key in df_value_order_start}
    for i in range(len(df_edge)):
        edge = df_edge[str(i)]
        edge_split = edge.split("_")
        node_1, node_2 = int(edge_split[0]), int(edge_split[1])
        if node_1 in df_value_order_start and node_2 in df_value_order_start:
            df_neighbor[node_1].append(node_2)
            df_neighbor[node_2].append(node_1)
    return df_neighbor

#function 2.
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

#function 3.
def v_return(q_race, q_house, q_human, q_social, q_physical):
    f = -3.800 + 0.971*q_race + 1.303*q_house + 2.876*q_human - 2.781*q_social + 2.276*q_physical
    return_value = 1.0/(1.0 + np.exp(-1.0 * f))
    return return_value

#function 4.
#{1:1}
def calculate_new_human_value(day, df_user_race, df_user_house, df_user_value,                              df_user_neighbor, df_poi_value, df_user_county, electricity_sequence):
    new_value = {key:0.0 for key in df_user_value}
    poi_value =  np.mean([df_poi_value[key] for key in df_poi_value])
    idx = 0 
    for key in new_value:  
        if idx % 10000 ==0:
            print ("Human: ", idx)
        human_value_list = list()
        if key in df_user_neighbor:
            if len(df_user_neighbor[key]) >0:
                for neighbor in df_user_neighbor[key]:
                    if neighbor in df_user_value:
                        human_value_list.append(df_user_value[neighbor])
            human_value = np.mean(human_value_list)
        else: 
            human_value = 0.5
        if key in df_user_county:
            county_value = electricity_sequence[df_user_county[key]][day]
        else:
            county_value = 0.5
        regression_result = v_return(df_user_race[key], df_user_house[key],                                     human_value, poi_value, county_value)
        term = max([np.min([df_user_value[key]+regression_result*0.05,1.0]),0.0])
        if term >= 0.0:
            new_value[key] = term
        idx += 1
    return new_value

#function 5.
def calculate_new_POI_value(day, df_poi_value, df_poi_neighbor, df_poi_county,electricity_sequence):
    beta_s_all = {"Harris County": 1.076, "Fort Bend County": 0.481, "Brazoria County": 0.486, "Galveston County": 0.486, "Jefferson County": 0.486}
    beta_s_s_all = {"Harris County": -0.214, "Fort Bend County": -0.156, "Brazoria County": 1.065, "Galveston County": 1.065, "Jefferson County": 1.065}
    beta_p_s_all = {"Harris County": -0.823, "Fort Bend County": -0.771, "Brazoria County": -0.165, "Galveston County": -0.165, "Jefferson County": -0.165}
    Ks = 0.85
    Ksother = 0.85
    
    new_value = {key:0.0 for key in df_poi_value}
    idx = 0 
    for key in new_value:
        idx+=1
        if idx %10000 == 0:
            print ("POI: ", idx)
        #print (df_poi_value[key])
        beta_s, beta_s_s, beta_p_s =            beta_s_all[df_poi_county[key]], beta_s_s_all[df_poi_county[key]],            beta_p_s_all[df_poi_county[key]]
        term_1 = beta_s * df_poi_value[key]*(1.0 - df_poi_value[key]*1.0/Ks)
        
        n_neigh = len(df_poi_neighbor[key])
        term_2 = np.sum([beta_s_s*1.0*df_poi_value[nei]*(1-df_poi_value[nei]/Ksother)/n_neigh for nei in df_poi_neighbor[key]])
        
        county_value = electricity_sequence[df_poi_county[key]][day]
        term_3 = beta_p_s*county_value*(1.0-county_value*1.0)
        new_value[key] = max(min(df_poi_value[key]-term_1-term_2-term_3, 1.4), 0)
    return new_value  

#function 6.
#self.user_county = {0: "Harris", ...}
#self.user_value = {"0": 123, ...}
#self.county_value = {"Harris":123, ...}
def extract_zone_value(user_poi_county_dict, user_poi_value_dict):
    counties = set(list(user_poi_county_dict.values()))
    county_value_dict = {key:list() for key in counties}
    county_value = {key:0.0 for key in counties}
    for user_id in user_poi_value_dict:
        county = user_poi_county_dict[user_id]
        value = user_poi_value_dict[user_id]
        county_value_dict[county].append(value)
    for county in county_value_dict:
        county_value[county] = np.mean(county_value_dict[county])
    return county_value


# In[4]:


def read_home_data(user_path_1, user_path_2, user_path_3):
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
    df_user_value_order, df_user_value_order_start = dict(), dict()
    for i in range(len(df_user_node["id"])):
        idx = df_user_node["id"][i]
        ac_value = df_user_value[idx]
        df_user_value_order[i] = ac_value
        df_user_value_order_start[i] = [df_user_node["county"][i], ac_value[1][0]] 
     
    #3. set the race and housing for each user
    #input: df_user_value_order_start
    #output: df_user_value_order_start
    r = random.random
    random.seed(5)
    ratio_race, ratio_house = 0.485, 0.569
    for key in df_user_value_order_start:
        random_race = random.random()
        if random_race < ratio_race:
            df_user_value_order_start[key].append(1)
        else:
            df_user_value_order_start[key].append(0)  
        random_house = random.random()
        if random_house < ratio_house:
            df_user_value_order_start[key].append(1)
        else:
            df_user_value_order_start[key].append(0)
    
    #4. extract county, value, race, house for users
    #input: df_user_value_order_start
    #output: df_user_county, df_user_value, df_user_race, df_user_house
    df_user_county = {key: df_user_value_order_start[key][0] for key in df_user_value_order_start}
    df_user_value = {key: df_user_value_order_start[key][1] for key in df_user_value_order_start}
    df_user_race = {key: df_user_value_order_start[key][2] for key in df_user_value_order_start}
    df_user_house = {key: df_user_value_order_start[key][3] for key in df_user_value_order_start}
    
    df_user_neighbor = get_current_neighbor(df_user_value_order_start, df_user_edge)
        
    return df_user_county, df_user_value, df_user_race, df_user_house, df_user_neighbor


# In[5]:


def read_poi_data(poi_path_1, poi_path_2, poi_path_3):
    #1. read poi data
    with open(poi_path_1, "r") as f1:  #90513 nodes  #['id', 'lon', 'lat', 'county']
        df_poi_node= json.load(f1)

    with open(poi_path_2, "r") as f2:
        df_poi_edge = json.load(f2)

    with open(poi_path_3, "r") as f3:
        df_poi_value = json.load(f3)
    
    #2. extract information
    #input: df_poi_node
    #output: df_poi_value_order, df_poi_value_order_start
    #output: df_poi_county, df_poi_value
    df_poi_value_order = dict()
    df_poi_value_order_start = dict()
    for i in range(len(df_poi_node["id"])):
        idx = df_poi_node["id"][i]
        ac_value = df_poi_value[idx]
        df_poi_value_order[i] = ac_value
        df_poi_value_order_start[i] = [df_poi_node["county"][i], min(ac_value[0][-1]/(0.01+ac_value[1][0]),1.0)]
    df_poi_county = {key: df_poi_value_order_start[key][0] for key in df_poi_value_order_start}
    df_poi_value = {key: df_poi_value_order_start[key][1] for key in df_poi_value_order_start}
    
    #3. obtain the neighborhood
    df_poi_neighbor = get_current_neighbor(df_poi_value_order_start, df_poi_edge)
    
    return df_poi_county, df_poi_value, df_poi_neighbor


# In[6]:


def read_electricity_data():
    electricity_curve = {"Harris County": [0.779, 0.835, 0.874, 0.884],                    "Fort Bend County": [0.872, 0.873, 0.886, 0.906],                    "Brazoria County": [0.841, 0.931, 0.947, 1.000],                    "Galveston County": [0.753, 0.792, 0.813, 0.844],                    "Jefferson County": [0.883, 0.600, 0.670, 0.679]}
    
    electricity_sequence = {"Harris County": interpolate(electricity_curve["Harris County"]),                       "Fort Bend County": interpolate(electricity_curve["Fort Bend County"]),                       "Brazoria County": interpolate(electricity_curve["Brazoria County"]),                       "Galveston County": interpolate(electricity_curve["Galveston County"]),                       "Jefferson County": interpolate(electricity_curve["Jefferson County"])}
    return electricity_sequence


# In[7]:


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
            
#Class 2: POI agent layer
class POIAgent(mesa.Agent):
    def __init__(self, df_poi_county, df_poi_value, df_poi_neighbor,electricity_sequence):
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
    
#Class 3: three layer network agent
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
        print("My average electricity value is " +str(electricity_value) + ".")
        print("My average home value is " +str(human_value) + ".")
        print("My average poi value is " +str(poi_value) + ".")
        return human_value, poi_value, electricity_value, human_value_collection, poi_value_collection


# In[8]:


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


# In[9]:


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




