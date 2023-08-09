import yaml
import io_handler as io
import xml.etree.ElementTree as ET

from input_for_pq.demand_mat_gen import generate_demand_mat
from input_for_pq.region_params_gen import generate_region_params_basic, generate_region_params_mfd


def _readxml(address):
    tree = ET.parse(address)
    root = tree.getroot()
    return root


def _read_addresses(features:list, config_adr='config files/pq_input_generation config.yaml'):
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
    demand.mat,
    region_connection.csv,
    region_params_mfd.csv,
    region_params_basic.csv --except limit_n which should be set manually based on MFD investigation
    '''

    # read addresses
    config_addresses = 'config files/pq_input_generation config.yaml'
    tripinfo_adr, vehroute_adr, demand_out_adr = \
        _read_addresses(['trip_info', 'veh_route', 'demand_output_adr'], config_addresses)

    # # read files
    print('reading xml files')
    # tripinfo_xml = _readxml(tripinfo_adr)
    vehroute_xml = _readxml(vehroute_adr)

    # # reading the segmented network
    print('reading segmented network')
    net, edges, densities, adj_mat, labels = io.get_network(config_addresses)
    edges_and_labels = {key: value for key, value in zip(edges, labels)}

    # generate inputs for perimeter control/point queue model codes
    # generate_demand_mat(edges, labels, tripinfo_adr, demand_out_adr)
    generate_demand_mat(edges_and_labels, vehroute_xml, demand_out_adr)
    generate_region_params_basic(vehroute_xml)
    generate_region_params_mfd()
