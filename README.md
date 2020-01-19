Soft Robots Evolution
=======================================
We use the [Evosoro](https://github.com/skriegman/evosoro) Python library to design and simulate soft robots made up of multiple materials. In particular, we have introduced:
* a method for evolving the materials of the soft robot in combination with its morphology;
* a novelty-based selection method based on trajectories;
* a method for evolving the signal determining the robot's movement together with its morphology;
* an environment with simple obstacles in order to evolve complex behaviours.

[Read our report](https://github.com/ZarHenry96/Ev-SoftBots/blob/master/report.pdf) if you are interested in deepening the techniques adopted and the results obtained.

Thanks to [Sam Kriegman](https://github.com/skriegman) for his useful starting codebase.

(1) Installation
------------
For a detailed explanation on how to install and run the project see [Installation](https://github.com/skriegman/evosoro#2-installation). If you encounter any issue while running it, you might refer to [Known issues](https://github.com/skriegman/evosoro#4-known-issues).

(2) Materials Evolution
------------
In [Evosoro](https://github.com/skriegman/evosoro), the materials a soft robot is made of are hard-coded in a configuration file that is read by [Voxelize](https://github.com/jonhiller/Voxelyze), a physics engine to simulate multi-material robots. We have extended the genotype of the soft robot, i.e. the Compositional Pattern-Producing Network (CPPN), by including four new nodes in the output layer of the network, corresponding to four new materials. Then, we have implemented a simple Genetic Algorithm (GA) to evolve the physical properties of the newly introduced materials. 
Here you can see some examples of soft robots evolved using this strategy: both yellow and orange materials correspond to muscles, while the brown material represents a tissue.
<img src="https://github.com/ZarHenry96/Ev-SoftBots/blob/master/img/materials-softbots.png" alt="materials evolution" width="500" height="250"/>

(3) Novelty-Based Search
------------
Differently from [Evosoro](https://github.com/skriegman/evosoro), where the soft robots that form the next generation are chosen based on multiple objective functions, we have introduced an additional selection method based on the robots "*novelty*". In our implementation, the "*novelty*" of a soft robot depends on its trajectory: the higher the diversity of the robot's trajectory, the higher its "*novelty*". The similarity between trajectories is determined using the Angular Metric for Shape Similarity ([AMSS](https://www.konan-u.ac.jp/hp/seki/myarticles/nakamura2012paa.pdf)).
Here you can see some examples of soft robots evolved using this selection method.

<img src="https://github.com/ZarHenry96/Ev-SoftBots/blob/master/img/novelty-softbots.png" alt="novelty-based search" width="500" height="500"/>

(4) Controller Evolution
------------
In [Evosoro](https://github.com/skriegman/evosoro), the expansion and contraction of active voxels are determined by the variation of an environmental parameter, namely the temperature, which is modeled as a sinusoidal function with customizable period and amplitude. Similarly to what has been done for the materials, we have extended the genotype of the soft robot by including: the temperature period and amplitude; the Coefficient of linear Thermal Expansion (CTE) determining how the active voxels react to the signal. Then, we have implemented a simple GA to evolve these properties in combination with the morphology of the soft robot.
Here you can see some examples of soft robots evolves using this strategy.

<img src="https://github.com/ZarHenry96/Ev-SoftBots/blob/master/img/controller-softbots.png" alt="controller evolution" width="500" height="250"/>

(5) Evolution vs Obstacles
------------
Inspired by the environments seen in [Evosoro](https://github.com/skriegman/evosoro), we have decided to design our environment with obstacles in order to evolve robots able to overcome them. 
Here you can see an example of soft robot which succeeds in overcoming the obstacles.

<img src="https://github.com/ZarHenry96/Ev-SoftBots/blob/master/img/over-obstacle-softbot.png" alt="controller evolution" width="540" height="250"/>
