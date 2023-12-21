# PostDisasterSim
An agent-based model that simulates how a socio-physical multilayer system recovers after a disaster.

## Project 
* National Science Foundation 1638311 (CRISP Type 2/Collaborative Research: Critical Transitions in the Resilience and Recovery of Interdependent Social and Physical Networks).

## Introduction

* PostDisasterSim simulates the post-disaster recovery (PDR) of the social-physical system, enabling us to understand its details and evaluate various policies.
* It is composed of three successive components: (1) network definition; (2) agent interaction modeling; and (3) agent-based simulation.
* Network definition: build the three-layer network using mobility phone location data, Point-of-interest (POI) foot traffic data.  
* Agent interaction modeling: specify how agents interact with each other during the PDR process.
* Agent-based simulation: simulate the recovery of each agent in the three-layer network temporally.

## Publication

**Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.**
Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, Tong Yao, Satish V. Ukkusuri\*. Under review. 2023.

## Requirements
* Python 3.6
* Mesa 0.9.0

## Directory Structure

* **0_data**. Released: the shapefile of Texas; the recovery level of physical infrastructures; Not released: mobile phone location data; POI data from SafeGraph (https://www.safegraph.com/).

* **1_data_preprocessing**. extract mobile phone location data within the five counties.

* **2_network_constructor**. define agents in the three-layer network.

1. Codes in "network_constructor/home/" define nodes and edges in the human layer.

2. Codes in "network_constructor/poi/" define nodes and edges in the social infrastructure layer.

* **3_model**. the code under "model/" is our ABM model. It takes the outputs of previous codes and simulates the dynamic of the three-layer system.

* **4_validation**. validate the simulation outcome with ground truth from mobile phone location and POI data.
   
* **5_results**. simulate the system recovery under the nine scenarios.

* **6_figures**. figures shown in this GitHub Repository.

## Overview
Overview of used data, three-layer socio-physical network, and the agent-based model (ABM) for post-disaster recovery.
<p align="center">
  <img src="https://github.com/JiaweiXue/PostDisasterSim/blob/main/6_figures/overview.png" width="700">
</p>

## Simulation Flowchart
The long-term PDR process. (a, b) The dynamics of recovery levels (i.e. $r_{a}(t)$) for agents representing users and POIs. (c) The flowchart that summarizes the procedure of agent interactions in the PDR process.
<p align="center">
  <img src="https://github.com/JiaweiXue/PostDisasterSim/blob/main/6_figures/simulation-flowchart.png" width="600">
</p>

## License
MIT license
