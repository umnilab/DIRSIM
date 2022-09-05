# PostDisasterSim (PDS)
An agent-based simulator mimicking how social-physical multilayer system recovers after a disaster.

## Project 
* National Science Foundation 1638311.
* CRISP Type 2/Collaborative Research: Critical Transitions in the Resilience and Recovery of Interdependent Social and Physical Networks

## Introduction

* PostDisasterSim simulates the post-disaster recovery (PDR) of the social-physical system, enabling us to understand its details and evaluate various policies.
* It is composed of three successive components: (1) network definition; (2) agent interaction modeling; (3) agent-based simulation.
* Network definition: build the three-layer network using mobility phone location data, Point-of-interest (POI) data, and electricity data.  
* Agent interaction modeling: specify how agents interact with each other during the PDR process.
* Agent-based simulation: simulate the recovery of each agent in the three-layer network temporally.

## Publication

**Supporting Post-disaster Recovery with Agent-based Modeling on Multilayer Social-physical Networks.**
Jiawei Xue, Sangung Park, Washim Uddin Mondal, Sandro Martinelli Reia, Satish V. Ukkusuri\*. Under review. 2022.

## Requirements
* Python 3.6
* Mesa 0.9.0

## Directory Structure

* **data**: preprocess mobile phone location data from Quadrant (https://www.quadrant.io/mobile-location-data), POI data from SafeGraph (https://www.safegraph.com/). 
* **model**: define agents in the three-layer network and their recovery dynamics.

1. Codes under folders "code_1_POI_node", "code_2_POI_edge",  and "code_3_POI_dynamic" define nodes and edges in the POI layer and extract the dynamic of POI activities from the SafeGraph POI data.

2. Codes under "code_4_Mobility_node", "code_5_Mobility_edge",  and "code_6_Mobility_dynamic" define nodes and edges in the home layer and extract the dynamic of return-home behavior from the Quadrant mobility data.

3. The Code under "code_7_ABM" is our ABM model. It takes the outputs of codes 1-6 as the input and simulates the dynamic of our three-layer system.
* **results**: simulate the system recovery under varying scenarios.

## Overview
Overview of used data, multilayer social-physical network, and the agent-based model for post-disaster recovery.
<p align="center">
  <img src="https://github.com/JiaweiXue/PostDisasterSim/blob/main/figures/overview.png" width="700">
</p>

## Simulation Flowchart
The long-term PDR process. (a) The dynamics of activity strength (i.e. $r_{a}(t)$) for agents representing homes and POIs. (b) The flowchart summarizing the procedure of agent interactions in the PDR process.
<p align="center">
  <img src="https://github.com/JiaweiXue/PostDisasterSim/blob/main/figures/simulation-flowchart.png" width="600">
</p>

## License
MIT license
