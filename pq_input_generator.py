import yaml
import io_handler as io
import xml.etree.ElementTree as ET
import pandas as pd

from input_for_pq.demand_mat_gen import generate_demand_mat
from input_for_pq.region_params_gen import generate_region_params_basic, generate_region_params_mfd


def _readxml(address):
    tree = ET.parse(address)
    root = tree.getroot()
    return root


def _read_yaml(features:list, config_adr='config files/pq_input_generation config.yaml'):
    config_file = yaml.safe_load(open(config_adr))
    addresses = []
    for feature in features:
        adr = config_file[feature]
        addresses.append(adr)
    return addresses


if __name__ == '__main__':
    '''
    for more information on what this codes outputs should be, look at output/pq_input/readme.md
    
    In this code we work on:
    config.csv
    demand.mat,
    region_connection.csv,
    region_params_mfd.csv,
    region_params_basic.csv --except limit_n which should be set manually based on MFD investigation
    '''

    # read config file and related network and files
    config_address = 'config files/pq_input_generation config.yaml'
    tripinfo_adr, vehroute_adr, pq_input_folder = \
        _read_yaml(['trip_info', 'veh_route', 'pq_input_folder'], config_address)

    print('reading xml files')
    # tripinfo_xml = _readxml(tripinfo_adr)
    vehroute_xml = _readxml(vehroute_adr)

    print('reading segmented network')
    net, edges, densities, adj_mat, labels = io.get_network(config_address)
    edges_and_labels = {key: value for key, value in zip(edges, labels)}

    # generate inputs for perimeter control/point queue model codes
    # # config.csv
    config_csv_keys = ['model_type', 'time_interval (s)', 'simulation_steps', 'deman_stop_step']
    config_dict = {key: [val] for key, val in zip(config_csv_keys, _read_yaml(config_csv_keys, config_address))}
    print(config_dict)
    data = pd.DataFrame(config_dict)
    data.to_csv(pq_input_folder+'config.csv', index=False)

    # # demand.mat
    generate_demand_mat(edges_and_labels, vehroute_xml,
                        time_intervals=int(config_dict['simulation_steps'][0]),
                        out_adr=pq_input_folder+'demand.mat')

    # #
    generate_region_params_basic(vehroute_xml)
    generate_region_params_mfd()
