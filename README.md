# Source code for the paper _"Reliability and generalization of gait biometrics using 3D inertial sensor data and 3D optical system trajectories"_

Requirements:


`csv_files` contains the exported markers' trajectories into CSV files, and the captured accelerations also in CSV files. The markers trajectories were exported using the [**MoCap Toolbox**](https://www.jyu.fi/hytk/fi/laitokset/mutku/en/research/materials/mocaptoolbox), generating a file for each marker.

First, it is necessary to keep the folder `csv_files` in this directory. Then, the notebooks can be run using Jupyter without any previous step. Each Jupyter notebook corresponds to at least one assessment of the paper:

* `experiment_identification.ipynb`

**How reliable is it to distinguish different subjects based on their gait using their trajectories or accelerations?**

**Is there any additional identity information about the subjects in accelerometer's and markers' trajectories beside than the way they walk?**

* `experiment_pairs.ipynb`

**How reliable and generalizing is it to learn common characteristics between data from the same subject and data from different individuals?**

* `experiment_harmonics.ipynb` and `experiment_frequencies.ipynb`

**What information are more relevant to determine the identity characteristics present in walking data?**

