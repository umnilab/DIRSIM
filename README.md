# PostDisasterSim
An agent-based simulator mimicking how social-physical multilayer system recovers after a disaster.

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

* **data**: Preprocess mobile phone location data from Quadrant (https://www.quadrant.io/mobile-location-data), POI data from SafeGraph (https://www.safegraph.com/). 
* **model**: Define agents in the three-layer network and their recovery dynamics.
* **results**: Simulate the system recovery under varying scenarios.

## Results

<p align="center">
  <img src="https://github.com/JiaweiXue/PostDisasterSim/blob/master/figures/simulation-flowchart.png" width="120">
</p>

## License
MIT license
