Soft Robots Evolution
=======================================
We use the [Evosoro](https://github.com/skriegman/evosoro) Python library to simulate and design soft robots with multiple materials. We extend the model through the introduction of:
* a method for evolving materials of a soft robot in combination with its morphology;
* a novelty-based selection method to select the individuals which form the population in the next generation;
* a method for evolving the signal controlling the soft robot together with its morphology;
* an environment with simple obstacles to evolve complex behaviours.

[Read our report](https://github.com/ZarHenry96/Ev-SoftBots/blob/master/report.pdf) if you are interested in deepening the techniques adopted and results obtained.

Thanks to [Sam Kriegman](https://github.com/skriegman) for his useful starting codebase.

(1) Installation
------------
For a detailed explanation on how to install and run the model see [Installation](https://github.com/skriegman/evosoro#2-installation). If you encounter any issue while running the model, you might refer to [Known issues](https://github.com/skriegman/evosoro#4-known-issues).

(2) Materials Evolution
------------
In [Evosoro](https://github.com/skriegman/evosoro), the materials a soft robot can be made of are hard-coded in a configuration file which is read by [Voxelize](https://github.com/jonhiller/Voxelyze), a physics engine to simulate multi-material voxel. We extend the genotype of the soft robot, meaning the Compositional Pattern-Producing Network (CPPN), by including four new nodes, representing the new materials, in the output layer of the network. Then, we use a simple Genetic Algorithm (GA) to evolve the physical properties of these newly introduced materials. 
Here you can see some examples of the soft robots evolved using this strategy: both the yellow and orange materials represent muscles, while the brown material represents a tissue.
<img src="https://github.com/ZarHenry96/Ev-SoftBots/blob/master/img/materials-softbots.png" alt="materials evolution" width="500" height="250"/>

(3) Novelty-Based Search
------------
Differently from [Evosoro](https://github.com/skriegman/evosoro), where the soft robots that are going to form the population of the next generation are chosen based on multiple objective functions, we introduce an additional selection method which selects robots based on their "*novelty*". In our implementation, the "*novelty*" of a soft robot depends on its trajectory: the higher the diversity of the robot's trajectory, the higher its "*novelty*". The similarity/distance between trajectories is determined using the Angular Metric for Shape Similarity ([AMSS](https://www.konan-u.ac.jp/hp/seki/myarticles/nakamura2012paa.pdf)).
Here you can see some examples of the soft robots evolved using this selection method.

<img src="https://github.com/ZarHenry96/Ev-SoftBots/blob/master/img/novelty-softbots.png" alt="novelty-based search" width="500" height="500"/>

(4) Controller Evolution
------------
In [Evosoro](https://github.com/skriegman/evosoro), the expansion and contraction of active voxels are determined by an environmental parameter named temperature. This signal is modeled as a sinusoidal function with a customizable period and amplitude. Similar to what has been done for the materials, we extend the genotype of the soft robot by including the two parameters controlling the temperature and the Coefficient of linear Thermal Expansion (CTE) controlling how the active voxels react to the signal. Then, we use a simple GA to evolve these properties in combination with the morphology of the soft robot.
Here you can see some examples of the soft robots evolves using this strategy.

<img src="https://github.com/ZarHenry96/Ev-SoftBots/blob/master/img/controller-softbots.png" alt="controller evolution" width="500" height="250"/>

(5) Evolution vs Obstacles
------------
Inspired by the environments designed in [Evosoro](https://github.com/skriegman/evosoro), we decided to design our environment containing obstacles to evolve robots with complex behaviours. 
Here you can see an example of an evolved soft robots which succeed in overcoming the obstacles.

<img src="https://github.com/ZarHenry96/Ev-SoftBots/blob/master/img/over-obstacle-softbot.png" alt="controller evolution" width="300" height="250"/>
