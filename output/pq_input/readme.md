# How to prepare the inputs
### _The network, regions, connections between regions, regions' parameters, and demand_

Edit the following files for configuring up the inputs
(sorry for now I have to lean on MATLAB, which cannot load/write `yaml` smoothly)
- `config.csv`
- `region_connection.csv`
- `region_params_basic.csv`
- `region_params_mfd.csv`
- `demand.mat`

## config.csv

- `model_type` can be "Q" (our model), "PQ" (Qianqian's model), "DQ" (double queue model)
- We use 1 second as the `time_interval`

| model_type | time_interval (s) | simulation_steps | demand_stop_step | 
| ------ | ------ | ------ | ------ |
| Q | 1 | 7200 | 2700 |


## region_connection.csv

- `start_region`: start region of the region link
- `end_region`: end region of the region link
- `max_outflow`: maximum outflow capacity
- `initial_n_vehs`: initially how many vehicles in each region

| start_region | end_region | max_outflow | initial_n_vehs |
| ------ | ------ | ------ | ------ |
| 1 | 2 | 3 | 0                                  |
| 1 | 12 | 3 | 0                                 |
| 1 | 13 | 3 | 0                                 |
| 2 | 1 | 3 | 0                                  |
| 2 | 3 | 3 | 0                                  |
| 2 | 13 | 3 | 0                                 |
| 2 | 14 | 3 | 0                                 |
| 3 | 2 | 3 | 0                                  |
| 3 | 4 | 3 | 0                                  |
| 3 | 14 | 3 | 0                                 |
| 4 | 3 | 3 | 0                                  |
| 4 | 5 | 3 | 0                                  |
| 4 | 14 | 3 | 0                                 |
| 4 | 15 | 3 | 0                                 |
| 5 | 4 | 3 | 0                                  |
| 5 | 6 | 3 | 0                                  |
| 5 | 15 | 3 | 0                                 |
| 6 | 5 | 3 | 0                                  |
| 6 | 7 | 3 | 0                                  |
| 6 | 15 | 3 | 0                                 |
| 6 | 16 | 3 | 0                                 |
| 7 | 6 | 3 | 0                                  |
| 7 | 8 | 3 | 0                                  |
| 7 | 16 | 3 | 0                                 |
| 8 | 7 | 3 | 0                                  |
| 8 | 9 | 3 | 0                                  |
| 8 | 16 | 3 | 0                                 |
| 8 | 17 | 3 | 0                                 |
| 9 | 8 | 3 | 0                                  |
| 9 | 10 | 3 | 0                                 |
| 9 | 17 | 3 | 0                                 |
| 10 | 9 | 3 | 0                                 |
| 10 | 11 | 3 | 0                                |
| 10 | 17 | 3 | 0                                |
| 10 | 18 | 3 | 0                                |
| 11 | 10 | 3 | 0                                |
| 11 | 12 | 3 | 0                                |
| 11 | 18 | 3 | 0                                |
| 12 | 1 | 3 | 0                                 |
| 12 | 11 | 3 | 0                                |
| 12 | 13 | 3 | 0                                |
| 12 | 18 | 3 | 0                                |
| 13 | 1 | 3 | 0                                 |
| 13 | 2 | 3 | 0                                 |
| 13 | 12 | 3 | 0                                |
| 13 | 14 | 4 | 0                                |
| 13 | 18 | 4 | 0                                |
| 13 | 19 | 5 | 0                                |
| 14 | 2 | 3 | 0                                 |
| 14 | 3 | 3 | 0                                 |
| 14 | 4 | 3 | 0                                 |
| 14 | 13 | 4 | 0                                |
| 14 | 15 | 4 | 0                                |
| 14 | 19 | 4 | 0                                |
| 15 | 4 | 3 | 0                                 |
| 15 | 5 | 3 | 0                                 |
| 15 | 6 | 3 | 0                                 |
| 15 | 14 | 4 | 0                                |
| 15 | 16 | 4 | 0                                |
| 15 | 19 | 5 | 0                                |
| 16 | 6 | 3 | 0                                 |
| 16 | 7 | 3 | 0                                 |
| 16 | 8 | 3 | 0                                 |
| 16 | 15 | 4 | 0                                |
| 16 | 17 | 5 | 0                                |
| 16 | 19 | 5 | 0                                |
| 17 | 8 | 3 | 0                                 |
| 17 | 9 | 3 | 0                                 |
| 17 | 10 | 3 | 0                                |
| 17 | 16 | 4 | 0                                |
| 17 | 18 | 4 | 0                                |
| 17 | 19 | 5 | 0                                |
| 18 | 10 | 3 | 0                                |
| 18 | 11 | 3 | 0                                |
| 18 | 12 | 3 | 0                                |
| 18 | 13 | 4 | 0                                |
| 18 | 17 | 4 | 0                                |
| 18 | 19 | 5 | 0                                |
| 19 | 13 | 5 | 0                                |
| 19 | 14 | 5 | 0                                |
| 19 | 15 | 5 | 0                                |
| 19 | 16 | 5 | 0                                |
| 19 | 17 | 5 | 0                                |
| 19 | 18 | 5 | 0                                |



## region_params_basic.csv
- Give the same region names associating with region_connection.csv
- Use limit_n to configure the upper bound of the number of vehicles in each region
- avg_trip_length is the average trip length of each region
- `init_vehicles` is to set how many vehicles are already existing in each region before running the simulation.
- `if_destination` whether the region is a destination according to demand set

| Region | capacity_n | avg_trip_length (m) | init_vehicles | if_destination | 
| ------ |------------| ------ | ------ | ------ |
| 1 | 4000       | 6100 | 1 | 0                                                 | 
| 2 | 4000       | 6100 | 1 | 0                                                 | 
| 3 | 4000       | 6100 | 1 | 0                                                 | 
| 4 | 4000       | 5800 | 1 | 0                                                 | 
| 5 | 4000       | 5800 | 1 | 0                                                 | 
| 6 | 4000       | 5800 | 1 | 0                                                 | 
| 7 | 4000       | 5500 | 1 | 0                                                 | 
| 8 | 4000       | 5500 | 1 | 0                                                 | 
| 9 | 4000       | 5500 | 1 | 0                                                 | 
| 10 | 4000       | 5800 | 1 | 0                                                | 
| 11 | 4000       | 5800 | 1 | 0                                                | 
| 12 | 4000       | 5800 | 1 | 0                                                | 
| 13 | 4000       | 4800 | 1 | 1                                                | 
| 14 | 4000       | 4800 | 1 | 1                                                | 
| 15 | 4000       | 4500 | 1 | 1                                                | 
| 16 | 4000       | 4500 | 1 | 1                                                | 
| 17 | 4000       | 4500 | 1 | 1                                                | 
| 18 | 4000       | 4500 | 1 | 1                                                | 
| 19 | 4000       | 3600 | 1 | 1                                                | 


## region_params_mfd.csv
- `mfd` MFD functions as a string

| Region |	mfd |
| ----- | ----- |
| 1	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 2	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 3	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 4	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 5	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 6	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 7	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 8	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 9	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 10	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 11	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 12	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 13	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 14	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 15	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 16	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 17	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 18	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |
| 19	| 1.4877e-07* n^3- 2.9815e-3* n^2+15* n |


## demand.mat

- `demand` is a 3D dataset, MATLAB is convenient to play with `.mat` files
- Fortunately, Python can output a 3D matrix as `.mat`, according to [Matrix from Python to MATLAB](https://stackoverflow.com/questions/1095265/matrix-from-python-to-matlab)
- Referring to `demand.mat` for the exact matrix format

## License

MIT
