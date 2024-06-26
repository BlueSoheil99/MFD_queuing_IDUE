Based on the original method by 
[Ji and Geroliminis (2012)](https://doi.org/10.1016/j.trb.2012.08.005), 
this work tries to use the results of a [calibrated simulation of Downtown Seattle](https://github.com/BlueSoheil99/DowntownSeattleSUMO)
traffic network in order to partition the region into homogeneous regions with well-defiend MFDs. 

<p align="center" width="100%">
<img width="75%" src="https://github.com/Ohay-Angah/mfd-queuing-idue/blob/partition/data/resultsSample.png"><br>
Results of Downtown Seattle partitioning and MFDs for each region<br>
</p>

# How to run the program

- install [SUMO](https://sumo.dlr.de/docs/Downloads.php)
- install required packages: 
  - _conda_ `conda install --yes --file requirements.txt` or
  - _pip_ `pip install -r requirements.txt`
- edit config files in `config files` folder if needed 
- run any of `.py` files below:


### What .py files can be run?


- **interactive.py**
  - Using this, instead of letting Ncut and merging algorithms select the segment(s) to work on, we do that manually.
  - It has a CLI-based user interface.
  - In this file, we can cut or merge segments based on the main algorithm or based on our judgement on a selected segment.
  - If you want to have some regions fixed and unchanged during the segmentation, change `fixed_regions` parameter
  - To get MFDs, put `number_production` as the CLI input.
  - The starting segmentation to work with is selected in `config.yaml` file. 
  - use `export` command to save the segmentation in `output/segmentation results` folder
  - If you have manually determined segments and their corresponding 
  links' IDs in.txt files, put them in  `data/config data/manual segmentation` folder,
  and change `config files/config.yaml` accordingly. Manual segmentation can be done using
  select mode tool in SUMO netedit software and its save button.


- **pq_input_generator.py**
  - Uses `input_for_pq` package to generate inputs needed for the perimeter control codes 
  based on the calibrated simulation and the partitioning. 
  

- pickle_creator.py
  - is used to: I) create pickle files from 1-minute simulation and II) spatially smooth the data from simulation (temporal smoothing can also be implemented).
  Smoothing, however, was not used for final results. Smoothing is similar to image smoothing.
  - pickle files have smaller size than .xml files and are faster to read.
  

- feature_plotter.py
  - used to make .gif files from our simulated network features
  

- segmentation_main.py
  - This code runs the modified automatic algorithm. We switched to running the next 
  file since it gave us more flexibility.

### Notes
-`inout.Plot_MFD._plot_number_production_theoretical_curve` is the function used for MFD generation.
`get_top_links` function helps in neglecting roads with no traffic or low priority (as defined in OSM maps). 
Other functions in `inout.Plot_MFD` might need further debugging.
