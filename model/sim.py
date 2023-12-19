#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Supporting Post-disaster Recovery with Agent-based Modeling 
#on Multilayer Social-physical Networks.
#Simulator: PostDisasterSim.
#Authors: Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, Tong Yao, and Satish V. Ukkusuri.


# In[2]:


import time
import json
import mesa
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import random as random 


# In[3]:


#0. folder
#1. functions
#2. read home, poi, and water data
#3. home, poi, and water agents
#4. simulation
#5. implementation


# # 0. folder

# In[4]:


folder = "/home/umni2/a/umnilab/users/xue120/umni4/"
sim_folder = folder + "2023_abm/PostDisasterSim/"
data_folder = sim_folder + "data/"

#home
home_node = data_folder + "home/valid_user_rms.json"
home_edge = data_folder + "home/valid_user_edge.json"
home_poi_edge = data_folder + "home/valid_poi_user_edge.json"
home_feature_8 = data_folder + "home/feature_8_mean.json"
home_feature_9 = data_folder + "home/feature_9_mean.json"

#POI
poi_node = data_folder + "poi/poi.json"
poi_edge = data_folder + "poi/poi_edge.json"
poi_feature = data_folder + "poi/poi_feature.json"

#Water
water_feature = data_folder + "water/physical_60.json"

#Output
output_path = sim_folder + "results/"
output_type = "base/"


# In[5]:


random.seed(88)


# # 1. functions

# In[6]:


#function 1. get the human node neighborhood of human nodes #["0":["123","456"]]
#input: df_all = {"123": XXX,...}, df_edge = {"0": "123_456",...}
#output: df_neighbor = {"123":["456",...],"456":["123",...],...}
def get_current_neighbor(df_all, df_edge):
    df_neighbor = {node: list() for node in df_all}
    n_edge = len(df_edge)
    for i in range(n_edge):
        edge = df_edge[str(i)]
        edge_split = edge.split("_")
        node_1, node_2 = edge_split[0], edge_split[1]
        if node_1 in df_all and node_2 in df_all:
            df_neighbor[node_1].append(node_2)
            df_neighbor[node_2].append(node_1)
    return df_neighbor

#function 2. get the POI neighborhood of human nodes
#input: df_all = {"123": XXX,...}, df_edge = {"0": "123_4567",...}
#output: df_neighbor = {"123":["4567",...],...}
def get_current_poi_user_neighbor(df_all, df_edge):
    df_neighbor = {user: list() for user in df_all}
    n_edge = len(df_edge)
    for i in range(n_edge):
        edge = df_edge[str(i)]
        edge_split = edge.split("_")
        node_1, node_2 = edge_split[0], edge_split[1]
        if node_1 in df_all:
            df_neighbor[node_1].append(node_2)
    return df_neighbor


# In[7]:


#function 3.  the behavioral mode (BM)
def p_return(q_housing, q_income, q_human, q_social, q_physical, county):
    if county == "Harris County":
        f = -1.904+1.520*q_housing+1.638*q_human-1.756*q_social+1.171*q_physical
    else:
        f = -2.379+2.26*0.00001*q_income+3.298*q_human-4.845*q_social+1.675*q_physical
    p = 1.0/(1.0+np.exp(-1.0*f))
    return p


# In[8]:


#function 4.
def update_human_value(day,\
                       df_user_county, df_user_value, df_user_housing, df_user_income,\
                       df_user_neighbor, df_user_poi_neighbor, water_seq,\
                       df_poi_value):
    new_value = {user: 0.0 for user in df_user_value}
    mean_human_value = np.mean(list(df_user_value.values()))
    mean_POI_value = np.mean(list(df_poi_value.values()))
    
    for user in new_value:   
        human_value = mean_human_value  #initialization
        if user in df_user_neighbor:
            human_value_list = list()
            if len(df_user_neighbor[user])>0:
                for neighbor in df_user_neighbor[user]:
                    if neighbor in df_user_value:
                        human_value_list.append(df_user_value[neighbor])
                human_value = np.mean(human_value_list)
        
        poi_value = mean_POI_value    #initialization
        poi_neighbor = df_user_poi_neighbor[user]
        if len(poi_neighbor)> 0:
            poi_value =  np.mean([df_poi_value[poi] for poi in poi_neighbor])
        
        county = df_user_county[user]
        county_value = water_seq[county][day]
        
        q = p_return(df_user_housing[user], df_user_income[user], human_value, poi_value, county_value, county)
        if df_user_value[user] == 1:
            new_value[user] = 1
        else:
            if random.random() < q/45.0:
                new_value[user] = 1
            else:
                new_value[user] = 0
    return new_value


# In[9]:


#function 5.
def update_POI_value(day, df_poi_county, df_poi_value, df_poi_neighbor, water_seq):
    beta_s_all = {"Harris County":0.026, "Fort Bend County":0.093,\
                  "Brazoria County":0.093, "Galveston County": 0.093, "Jefferson County":0.093}
    K_s_all = {"Harris County": 0.671, "Fort Bend County": 0.736,\
               "Brazoria County": 0.736, "Galveston County": 0.736, "Jefferson County":0.736}
    beta_p_all = {"Harris County": 1.432, "Fort Bend County": 1.114,\
                  "Brazoria County": 1.114,  "Galveston County": 1.114, "Jefferson County": 1.114} 
    K_p_all = {"Harris County": 0.901, "Fort Bend County": 0.935,\
               "Brazoria County": 0.935, "Galveston County": 0.935, "Jefferson County": 0.935}  
    new_value = {poi: 0.0 for poi in df_poi_value}
    
    for poi in new_value:
        county = df_poi_county[poi]
        beta_s, beta_p = beta_s_all[county], beta_p_all[county]
        K_s, K_p = K_s_all[county], K_p_all[county]
    
        term_1 = df_poi_value[poi]

        term_2 = 0.001*beta_s*np.sum([df_poi_value[neighbor]*(1.0-df_poi_value[neighbor]/K_s)\
                         for neighbor in df_poi_neighbor[poi]])

        county_value = water_seq[county][day]
        term_3 = 0.1*beta_p*county_value*(1.0-county_value/K_p)
        
        new_value[poi] = min(term_1+3.5*(abs(term_2)+abs(term_3)),1.1)
    return new_value  


# In[10]:


#function 6.
def compute_k_days_average(ylist, k):
    a = int((k-1)/2)
    b = a+1
    n = len(ylist)
    ylist_new = list()
    for i in range(len(ylist)):
        entries = ylist[max(0, i-a): min(n, i+b)]
        ylist_new.append(np.mean(entries))
    return ylist_new


# # 2. read home, poi, and water data

# In[11]:


def read_home_data(user, user_edge, user_poi_edge, user_feature_8, user_feature_9):
    #user_node. #node. #37,943 nodes. #['id', 'lon', 'lat', 'county']
    #user_edge. #edge. #1,017,063 edges.  #{0:"19194_21733", 1:..] 
    #user_poi_edge. #edge. #2,202,192 edges. #{0:"19194_21733", 1:..}
    #path_8. "rlevel":{"12345": [1]*17}; Aug. 15, 16, ..., 31.   17 days. 
    #path_9. "rlevel":{"12345": [1]*29}; Sept. 1, 2, ..., 29.    29 days.
    
    with open(user, "r") as f1:
        df_user = json.load(f1)   
    with open(user_edge, "r") as f2: 
        df_user_edge = json.load(f2)  
    with open(user_poi_edge, "r") as f3: 
        df_user_poi_edge = json.load(f3) 
        
    with open(user_feature_8, "r") as f4:
        df_value_8 = json.load(f4)
    with open(user_feature_9, "r") as f5:
        df_value_9 = json.load(f5)
        
    df_value_8_9 = dict()
    for user in df_value_8["rlevel"]:
        rvalue_8, rvalue_9 = df_value_8["rlevel"][user], df_value_9["rlevel"][user]
        rvalue_8_9 = rvalue_8 + rvalue_9
        df_value_8_9[user] = rvalue_8_9
        
    df_all = dict()                    #df_all[user] = [county, value, housing, income]
    user_list, county_list = list(df_user["id"]), list(df_user["county"])
    n_user = len(user_list)
    for i in range(n_user):
        user = user_list[i]
        df_all[str(i)] = [county_list[i], df_value_8_9[user][15]]   #Aug. 30
        #1_county #2_recovery level. 
     
    housing_ratio = 53.0/(53.0+46.0)
    income_ratio = [0.099, 0.183, 0.268, 0.451, 0.521, 0.577, 0.690, 0.775, 1.00]
    income_level = [15000, 22500, 37500, 52500, 67500, 82500, 97500, 112500, 120000]
    n_income = len(income_ratio)
    
    for i in df_all:
        random_1, random_2 = random.random(), random.random()
        if random_1 < housing_ratio:
            housing = 1
        else:
            housing = 0
        df_all[i].append(housing)                    #3_housing
            
        for k in range(n_income):
            if random_2 <= income_ratio[k]:
                df_all[i].append(income_level[k])    #4_income
                break

    df_user_county = {i: df_all[i][0] for i in df_all}
    df_user_value = {i: df_all[i][1] for i in df_all}
    df_user_housing = {i: df_all[i][2] for i in df_all}
    df_user_income = {i: df_all[i][3] for i in df_all}
    df_user_neighbor = get_current_neighbor(df_all, df_user_edge)
    df_user_poi_neighbor = get_current_poi_user_neighbor(df_all, df_user_poi_edge)   
    
    return df_user_county, df_user_value, df_user_housing, df_user_income, df_user_neighbor, df_user_poi_neighbor


# In[12]:


def read_poi_data(poi, poi_edge, poi_feature):
    #1. read the files
    with open(poi, "r") as f1:  #57,647 nodes  #['id', 'lon', 'lat', 'county']
        df_poi = json.load(f1)
    with open(poi_edge, "r") as f2:
        df_poi_edge = json.load(f2)
    with open(poi_feature, "r") as f3:
        df_poi_feature = json.load(f3)
    
    #2. extract information
    df_all = dict()
    poi_list, county_list = list(df_poi["id"]), list(df_poi["county"])
    n_poi = len(poi_list)
    for i in range(n_poi):
        poi = poi_list[i]
        poi_feature = df_poi_feature[poi]
        rvalue = poi_feature[0] + poi_feature[1]
        rvalue = compute_k_days_average(rvalue, 7)
        rstart = min(rvalue[29]/(0.000001+np.mean(rvalue[14:14+7])), 1.5)    #Aug. 30.
        df_all[str(i)] = [county_list[i], rstart]       #1_county  #2_recovery level
        
    df_poi_county = {i: df_all[i][0] for i in df_all}
    df_poi_value = {i: df_all[i][1] for i in df_all}    
    print ("average poi value", round(np.mean(list(df_poi_value.values())), 3))
    
    #3. obtain the neighborhood
    df_poi_neighbor = get_current_neighbor(df_all, df_poi_edge)
    return df_poi_county, df_poi_value, df_poi_neighbor


# In[13]:


def read_water_data(water_path):
    water_data = json.load(open(water_path))
    water_seq = {"Harris County": water_data["ha"], "Fort Bend County": water_data["fb"],\
                 "Brazoria County": water_data["br"], "Galveston County": water_data["ga"],\
                 "Jefferson County": water_data["jf"]}
    return water_seq


# # 3. home, poi, and water agents

# In[14]:


#Class 1: home agent layer
class HomeAgentLayer(mesa.Agent):
    def __init__(self, df_user_county, df_user_value, df_user_housing, df_user_income,\
                 df_user_neighbor, df_user_poi_neighbor, water_seq):
        self.user_county = df_user_county
        self.user_value = df_user_value
        self.user_housing = df_user_housing
        self.user_income = df_user_income
        self.user_neighbor = df_user_neighbor
        self.user_poi_neighbor = df_user_poi_neighbor
        self.water_seq = water_seq
        
    def step(self, poi_value, day):
        self.user_value = update_human_value(day, \
                                              self.user_county, self.user_value, self.user_housing, self.user_income,\
                                              self.user_neighbor, self.user_poi_neighbor, self.water_seq,\
                                              poi_value)    

    def get_value(self):
        return (self.user_value)
    
    def get_mean_value(self):
        value_list = list(self.user_value.values())
        mean_value = np.mean(value_list)
        return (mean_value)


# In[15]:


#Class 2: POI agent layer
class POIAgent(mesa.Agent):
    def __init__(self, df_poi_county, df_poi_value, df_poi_neighbor, water_seq):
        self.poi_county = df_poi_county
        self.poi_value = df_poi_value
        self.poi_neighbor = df_poi_neighbor
        self.water_seq = water_seq
        
    def step(self, day):
        self.poi_value = update_POI_value(day, \
                                          self.poi_county, self.poi_value, self.poi_neighbor,\
                                          self.water_seq) 
    
    def get_value(self):
        return (self.poi_value)
    
    def get_mean_value(self):
        value_list = list(self.poi_value.values())
        mean_value = np.mean(value_list)
        return (mean_value)


# In[16]:


#Class 3: three layer network agent
class ThreeLayerNetworkAgent(mesa.Model):
    def __init__(self, df_user_county, df_user_value, df_user_housing, df_user_income, df_user_neighbor,\
                 df_user_poi_neighbor,\
                 df_poi_county, df_poi_value, df_poi_neighbor, water_seq):
        self.day = 0
        self.humanLayer = HomeAgentLayer(df_user_county, df_user_value, df_user_housing, df_user_income,\
                                         df_user_neighbor, df_user_poi_neighbor, water_seq)
        self.socialLayer = POIAgent(df_poi_county, df_poi_value, df_poi_neighbor, water_seq)
        self.water = water_seq

    def step(self):
        self.socialLayer.step(self.day)
        self.humanLayer.step(self.socialLayer.poi_value, self.day)
        self.day += 1
        
    def get_full(self):
        human_value_full = self.humanLayer.get_value()
        poi_value_full = self.socialLayer.get_value() 
        return human_value_full, poi_value_full
    
    def get_current_value(self):
        human_value = self.humanLayer.get_mean_value()*1.0
        poi_value = self.socialLayer.get_mean_value()*1.0
        water_value = np.mean([self.water[county][self.day] for county in self.water])
        human_value_all = self.humanLayer.user_value
        poi_value_all = self.socialLayer.poi_value
        
        print("My average home value is " + str(round(human_value, 3)))
        print("My average poi value is " + str(round(poi_value, 3)))
        print("My average water value is " + str(round(water_value, 3)))
        return human_value, poi_value, water_value, human_value_all, poi_value_all


# # 4. simulation

# In[17]:


def main(user, user_edge, user_poi_edge,\
         user_feature_8, user_feature_9,\
         poi, poi_edge, poi_feature, water_path):
    time1 = time.time()
    human_value, poi_value, water_value = list(), list(), list()
    human_all = {}
    poi_all = {}
    
    #1. read the data
    #User
    df_user_county, df_user_value, df_user_housing, df_user_income, df_user_neighbor, df_user_poi_neighbor =\
        read_home_data(user, user_edge, user_poi_edge, user_feature_8, user_feature_9)
    print ("finish loading home data")
    
    home = {"county": df_user_county, "housing": df_user_housing, "income": df_user_income}
    output_home = open(output_path + output_type + "output_home" + ".json",'w')
    json.dump(home, output_home)
    output_home.close()
    
    #POI
    df_poi_county, df_poi_value, df_poi_neighbor = read_poi_data(poi, poi_edge, poi_feature)
    print ("finish loading POI data")
    
    poi = {"county": df_poi_county}
    output_poi = open(output_path + output_type + "output_poi" + ".json",'w')
    json.dump(poi, output_poi)
    output_poi.close()
    
    #Water
    water = read_water_data(water_path)
    print ("finish loading water data")
    output_water = open(output_path + output_type + "output_water" + ".json",'w')
    json.dump(water, output_water)
    output_water.close()
    
    #2. build the network
    model = ThreeLayerNetworkAgent(df_user_county, df_user_value, df_user_housing, df_user_income, df_user_neighbor, \
                                   df_user_poi_neighbor,\
                                   df_poi_county, df_poi_value, df_poi_neighbor,\
                                   water)
    print ("finish building the three-layer network")
    time2 = time.time()
    print ("time until now: ", round(time2- time1,2))
    
    #3. simulate the Septmber.
    print ("start simulating the recovery from Aug. 30 to Oct. 28, 2017")
    for i in range(60):
        print ("--------------------------------")
        print ("--------------------------------")
        print ("day: ", i+1)
        human_i, poi_i, water_i, human_value_all, poi_value_all =\
            model.get_current_value()
        
        human_value.append(human_i)
        poi_value.append(poi_i)
        water_value.append(water_i)
        
        human_value_full, poi_value_full = model.get_full()
        human_all[str(i)] = human_value_full
        poi_all[str(i)] = poi_value_full
        
        print ("--------------------------------")
        model.step()
        time2 = time.time()
        print ("time until now: ", time2-time1)

    output_home = open(output_path + output_type + "/output_home_value" + ".json",'w')
    json.dump(human_all, output_home)
    output_home.close()

    output_poi = open(output_path + output_type + "/output_poi_value" + ".json",'w')
    json.dump(poi_all, output_poi)
    output_poi.close()
    
    return human_value, poi_value, water_value 


# # 5. implementation

# In[18]:


if __name__ == '__main__':
    main(home_node, home_edge, home_poi_edge, \
         home_feature_8, home_feature_9,\
         poi_node, poi_edge, poi_feature, water_feature)


# In[ ]:





# In[ ]:




