#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.
#Simulator: PostDisasterSim.
#Authors: Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, Tong Yao, and Satish V. Ukkusuri.


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
def v_return(q_house, q_income, q_human, q_social, q_physical, county):
    if county == "Harris County":
        f = -1.904 + 1.520 * q_house +                1.638 * q_human - 1.756 * q_social + 1.171 * q_physical
    else:
        f = -2.379 + 2.26 * 0.00001 * q_income +                3.298 * q_human - 4.845 * q_social + 1.675 * q_physical
    return_value = 1.0/(1.0 + np.exp(-1.0 * f))
    return return_value
                  
#function 3.
#{1:1}
def calculate_new_human_value(day, df_user_house, df_user_income, df_user_value,                              df_user_neighbor, df_poi_value, df_user_county, water_sequence):
    new_value = {key: 0.0 for key in df_user_value}
    #poi_value 
    poi_value =  np.mean([df_poi_value[key] for key in df_poi_value])
    idx = 0 
    
    print ("# row", len(new_value))
    for key in new_value:  
        if idx % 30000 ==0:
            print ("Human: ", idx)
        idx = idx+1    
        #human value
        human_value_list = list()
        if key in df_user_neighbor:
            if len(df_user_neighbor[key]) > 0:
                for neighbor in df_user_neighbor[key]:
                    if neighbor in df_user_value:
                        human_value_list.append(df_user_value[neighbor])
            human_value = np.mean(human_value_list)
        else: 
            human_value = 0.7
          
        #county_value
        if key in df_user_county:
            county_value = water_sequence[df_user_county[key]][day]
        else:
            county_value = 0.7
         
        regression_result = v_return(df_user_house[key], df_user_income[key],                                     human_value, poi_value, county_value,                                     df_user_county[key])
        if df_user_value[key] == 1:
            new_value[key] = 1
        else:
            if random.random() < regression_result*1.0/30.0:
                new_value[key] = 1
            else:
                new_value[key] = 0
    return new_value

#function 4.
def calculate_new_POI_value(day, df_poi_value, df_poi_neighbor, df_poi_county, water_sequence):
    beta_s_all = {"Harris County": 0.026, "Fort Bend County": 0.093,                 "Brazoria County": 0.093, "Galveston County": 0.093, "Jefferson County":0.093}
    K_s_all = {"Harris County": 0.671, "Fort Bend County": 0.736,              "Brazoria County": 0.736, "Galveston County": 0.736, "Jefferson County":0.736}
    beta_p_all = {"Harris County": 1.432, "Fort Bend County": 1.114, "Brazoria County": 1.114,                 "Galveston County": 1.114, "Jefferson County": 1.114} 
    K_p_all = {"Harris County": 0.901, "Fort Bend County": 0.935,                 "Brazoria County": 0.935, "Galveston County": 0.935, "Jefferson County": 0.935}  
    new_value = {key: 0.0 for key in df_poi_value}
    
    idx = 0
    print ("# row", len(new_value))
    for key in new_value:
        idx = idx + 1
        if idx % 30000 == 0:
            print ("POI: ", idx)
        poi_county = df_poi_county[key]
        beta_s, beta_p = beta_s_all[poi_county], beta_p_all[poi_county]
        K_s, K_p = K_s_all[poi_county], K_p_all[poi_county]
    
        #first term
        term_1 = df_poi_value[key]

        #second term
        n_neigh = len(df_poi_neighbor[key])
        term_2 = np.sum([0.001 * beta_s * df_poi_value[nei]*(1.0-df_poi_value[nei]/K_s)                          for nei in df_poi_neighbor[key]])

        #third term
        county_value = water_sequence[poi_county][day]
        term_3 = 0.10 * beta_p * county_value * (1.0 - county_value*1.0/K_p)
        
        #update
        new_value[key] = min(term_1 + abs(term_2) + abs(term_3), 1.0)
    return new_value    
    
#function 5.
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
    
    ratio_house = 53.0 / (53.0 + 46.0)
    income_ratio = [0.099, 0.183, 0.268, 0.451, 0.521, 0.577, 0.690, 0.775, 1.00]
    income_level = [11000, 15000, 22500, 37500, 52500, 67500, 82500, 97500, 120000]
    
    for key in df_user_value_order_start:
        random_race = random.random()
        if random_race < ratio_house:
            df_user_value_order_start[key].append(1)
        else:
            df_user_value_order_start[key].append(0)  
            
        random_house = random.random()
        for k in range(len(income_ratio)):
            if random_house <= income_ratio[k]:
                df_user_value_order_start[key].append(income_level[k])
                break
    
    #4. extract county, value, race, house for users
    #input: df_user_value_order_start
    #output: df_user_county, df_user_value, df_user_race, df_user_house
    df_user_county = {key: df_user_value_order_start[key][0] for key in df_user_value_order_start}
    df_user_value = {key: df_user_value_order_start[key][1] for key in df_user_value_order_start}
    df_user_house = {key: df_user_value_order_start[key][2] for key in df_user_value_order_start}
    df_user_income = {key: df_user_value_order_start[key][3] for key in df_user_value_order_start}
    
    df_user_neighbor = get_current_neighbor(df_user_value_order_start, df_user_edge)
        
    return df_user_county, df_user_value, df_user_house, df_user_income, df_user_neighbor


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


def read_water_data(water_path):
    water_data = json.load(open(water_path))
    water_sequence = {"Harris County": water_data["ha"],                       "Fort Bend County": water_data["fb"],                       "Brazoria County": water_data["br"],                       "Galveston County": water_data["ga"],                       "Jefferson County": water_data["jf"]}
    return water_sequence


# In[7]:


#Class 1: home agent layer
class HomeAgentLayer(mesa.Agent):
    """An agent with fixed initial activity value."""
    def __init__(self, df_user_county, df_user_value,                 df_user_house, df_user_income,                  df_user_neighbor, water_sequence):
        self.user_county = df_user_county
        self.user_value = df_user_value
        self.user_house = df_user_house
        self.user_income = df_user_income
        self.user_neighbor = df_user_neighbor
        self.home_day = 0
        self.water_sequence = water_sequence
        
    def step(self, poi_value):
        new_value = calculate_new_human_value(self.home_day, self.user_house, self.user_income,                                   self.user_value, self.user_neighbor,                                     poi_value, self.user_county, self.water_sequence)
        self.user_value = new_value    
        self.home_day += 1

    def print_activity_value_full(self):
        return (self.user_value)
    
    def print_activity_value(self):
        return (np.mean(list(self.user_value.values())))
            
#Class 2: POI agent layer
class POIAgent(mesa.Agent):
    def __init__(self, df_poi_county, df_poi_value, df_poi_neighbor,water_sequence):
        self.poi_county = df_poi_county
        self.poi_value = df_poi_value
        self.poi_neighbor = df_poi_neighbor
        self.poi_day = 0
        self.water_sequence = water_sequence
        
    def step(self):
        new_value = calculate_new_POI_value(self.poi_day, self.poi_value,                                            self.poi_neighbor, self.poi_county, self.water_sequence)
        self.poi_value = new_value 
        self.poi_day += 1
    
    def print_activity_value_full(self):
        return (self.poi_value)
    
    def print_activity_value(self):
        return (np.mean(list(self.poi_value.values())))
    
#Class 3: three layer network agent
class ThreeLayerNetworkAgent(mesa.Model):
    def __init__(self, df_user_county, df_user_value, df_user_house,                 df_user_income,  df_user_neighbor, 
                 df_poi_county, df_poi_value, df_poi_neighbor, water_sequence):
        self.humanLayer = HomeAgentLayer(df_user_county, df_user_value,                                         df_user_house, df_user_income,df_user_neighbor, water_sequence)
        self.socialLayer = POIAgent(df_poi_county, df_poi_value,df_poi_neighbor, water_sequence)
        self.day = 0
        self.water_sequence = water_sequence

    def step(self):
        self.socialLayer.step()
        self.humanLayer.step(self.socialLayer.poi_value)
        self.day += 1
    
    def show_full(self):
        human_value_full = self.humanLayer.print_activity_value_full()
        poi_value_full = self.socialLayer.print_activity_value_full() 
        return human_value_full, poi_value_full
    
    def show_current_value(self):
        human_value = self.humanLayer.print_activity_value()
        poi_value = self.socialLayer.print_activity_value()*1.0
        water_value = np.sum([self.water_sequence[key][self.day]*1.0/5.0                                    for key in self.water_sequence])
        human_value_collection = self.humanLayer.user_value
        poi_value_collection = self.socialLayer.poi_value
        
        print("Day is " +str(self.day) + ".")
        print("My average home value is " +str(human_value) + ".")
        print("My average poi value is " +str(poi_value) + ".")
        print("My average water value is " +str(water_value) + ".")
        return human_value, poi_value, water_value, human_value_collection, poi_value_collection


# In[8]:


human_collection = {}
poi_collection = {}


# In[9]:


def main(user_path_1, user_path_2, user_path_3, poi_path_1, poi_path_2, poi_path_3, water_path):
    time1 = time.time()
    human_value, poi_value, water_value = list(), list(), list()
    
    #1. read the data
    df_user_county, df_user_value, df_user_house, df_user_income, df_user_neighbor =        read_home_data(user_path_1, user_path_2, user_path_3)
    print ("finish loading home data")
    
    #output1
    output_home_dict = {"county": df_user_county,                        "house": df_user_house,                        "income": df_user_income}
    output_home_file = open("s1/output_home" + ".json",'w')
    json.dump(output_home_dict, output_home_file)
    output_home_file.close()
    

    df_poi_county, df_poi_value, df_poi_neighbor =        read_poi_data(poi_path_1, poi_path_2, poi_path_3)
    print ("finish loading POI data")
    #output2
    output_poi_dict = {"county": df_poi_county}
    output_poi_file = open("s1/output_poi" + ".json",'w')
    json.dump(output_poi_dict, output_poi_file)
    output_poi_file.close()
    

    water_sequence = read_water_data(water_path)
    print ("finish loading water data")
    output_water_file = open("s1/output_water" + ".json",'w')
    json.dump(water_sequence, output_water_file)
    output_water_file.close()
    
    #2. build the network
    model = ThreeLayerNetworkAgent(df_user_county, df_user_value, df_user_house,                 df_user_income,  df_user_neighbor,                 df_poi_county, df_poi_value, df_poi_neighbor, water_sequence)
    print ("finish building the three-layer network")
    time2 = time.time()
    print ("time until now: ", time2- time1)
    
    #3. simulate the Septmber.
    print ("start simulating the recovery from Sept. 1 to Sept. 30, 2017")
    for i in range(60):
        print ("--------------------------------")
        print ("--------------------------------")
        print ("day: ", i+1)
        human_value_i, poi_value_i, water_value_i,                 human_value_collection, poi_value_collection            = model.show_current_value()
        
        human_value.append(human_value_i)
        poi_value.append(poi_value_i)
        water_value.append(i)
        
        human_value_full, poi_value_full = model.show_full()
        human_collection[str(i)] = human_value_full
        poi_collection[str(i)] = poi_value_full
        
        print ("--------------------------------")
        model.step()
        time2 = time.time()
        print ("time until now: ", time2- time1)

    output_home_value_file = open("s1/output_home_value" + ".json",'w')
    json.dump(human_collection, output_home_value_file)
    output_home_value_file.close()

    output_poi_value_file = open("s1/output_poi_value" + ".json",'w')
    json.dump(poi_collection, output_poi_value_file)
    output_poi_value_file.close()
    
    return human_value, poi_value, water_value 


# In[10]:


if __name__ == '__main__':
    loc = "/data/xue120/2022_abm/6-simulation/"
    home_node = loc + "code_4_5_6/code_4_output_house.json"
    home_edge = loc + "code_4_5_6/code_5_output_house_edge.json"
    home_activity = loc + "code_4_5_6/code_6_human_activity.json"
    
    poi_node = loc + "code_1_2_3/code_1_output_poi.json"
    poi_edge = loc + "code_1_2_3/code_2_output_poi_adj.json"
    poi_activity = loc + "code_1_2_3/code_3_output_poi_activity.json"
    
    water_activity = loc + "physical_60.json"

    main(home_node, home_edge, home_activity, poi_node, poi_edge, poi_activity, water_activity)


# In[ ]:





# In[ ]:




