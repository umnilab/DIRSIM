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

* **data**: mobile phone location data from Quadrant (https://www.quadrant.io/mobile-location-data), POI data from SafeGraph (https://www.safegraph.com/). 
* **network_constructor**: define agents in the three-layer network.

1. Codes in "network_constructor/home/" define nodes and edges in the human layer using the Quadrant data.

2. Codes in "network_constructor/poi/" define nodes and edges in the social infrastructure layer using the SafeGraph data.

* **model**: the code under "model/" is our ABM model. It takes the outputs of previous codes and simulates the dynamic of the three-layer system.
   
* **results**: simulate the system recovery under the nine scenarios.

## Overview
Overview of used data, three-layer socio-physical network, and the agent-based model (ABM) for post-disaster recovery.
<p align="center">
  <img src="https://github.com/JiaweiXue/PostDisasterSim/blob/main/figures/overview.png" width="700">
</p>

## Simulation Flowchart
The long-term PDR process. (a) The dynamics of recovery levels (i.e. $r_{a}(t)$) for agents representing users and POIs. (b) The flowchart that summarizes the procedure of agent interactions in the PDR process.
<p align="center">
  <img src="https://github.com/JiaweiXue/PostDisasterSim/blob/main/figures/simulation-flowchart.png" width="600">
</p>

## License
MIT license
