# How to run the program

- install [SUMO](https://sumo.dlr.de/docs/Downloads.php)
- install required packages: 
  - _conda_ `conda install --yes --file requirements.txt` or
  - _pip_ `pip install -r requirements.txt`
- edit `config.yaml` 
- run `main.py` (for now this .py file is not working, and we use debug.py, interactive.py, and manual_segmentation.py)

### What .py files can be run?

- debug.py
  - it works instead of main.py until we finalize our codes and their architecture. Then main.py will be the code to run the algorithm
- interactive.py
  - Using this, instead of letting Ncut and merging algorithms select the segment(s) to work on, we do that manually. The idea is first we find the best partitioning manually, and then design the algorithm to reach that segmentation.
- manual_segmentation.py
  - used when we have manually determined segments and their corresponding links' IDs and put .txt files in `/data/manual detected edges in regions`
- feature_plotter.py
  - used to make .gif files from our simulated network features
- pickle_creator.py
  - is used to 1-create pickle files from 1-minute simulation and 2-smooth data from simulation(spatial smoothing. temporal smoothing could also be used)
