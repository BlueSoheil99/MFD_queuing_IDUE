import yaml
import io_handler as io
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

from Graph import Graph
import logic_handler as logic

from input_for_pq.demand_mat_gen import generate_demand_mat
from input_for_pq.region_params_gen import generate_region_params_basic

from MFD import Plot_MFD

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


def A_goingto_B(link1, link2, network):
    outgoing = network.getEdge(link1).getOutgoing()
    outgoing = list(outgoing.keys())
    outgoing = [edge.getID() for edge in outgoing]
    if link2 in outgoing:
        return True
    return False


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
    # todo edges_and_labels = add_nearest_labels_for_forgotten_edges(edges_and_labels, net)

    # Generate inputs for perimeter control/point queue model codes
    print('### GENERATING config.csv')
    config_csv_keys = ['model_type', 'time_interval (s)', 'simulation_steps', 'deman_stop_step']
    config_dict = {key: [val] for key, val in zip(config_csv_keys, _read_yaml(config_csv_keys, config_address))}
    print(config_dict)
    data = pd.DataFrame(config_dict)
    data.to_csv(pq_input_folder+'config.csv', index=False)

    # ---------- demand.mat
    print('### GENERATING demand.mat')
    time_interval, sim_start = _read_yaml(['time_interval (s)', 'SUMO_sim_start'], config_address)
    # generate_demand_mat(edges_and_labels, vehroute_xml,
    #                     time_interval=float(time_interval),
    #                     sim_start=int(sim_start),
    #                     sim_steps=int(config_dict['simulation_steps'][0]),
    #                     out_adr=pq_input_folder+'demand.mat')


    print('### GENERATING region_params_mfd.csv')
    MFD_start_time = 18000.00
    MFD_end_time = 37800.00  # after 6.5 hours
    graph = Graph(adj_mat, densities, labels)
    boundary_ids = logic.get_boundary_IDs(graph, edges, get_neighbors=True)
    segment_ids = logic.get_segment_IDs(graph, list(edges))
    # mfd_fit_lines = Plot_MFD.MFD_plotter((segment_ids, boundary_ids), start_time=MFD_start_time,
    #                                      end_time=MFD_end_time, num_vs_prod=True)
    # mfd_str = [str(np.poly1d(mfd)).split('\n')[1].replace('x', 'n') for mfd in mfd_fit_lines.values()]
    # mfd_dict = {'Region': list(mfd_fit_lines.keys()), 'mfd': mfd_str}
    # mfd_df = pd.DataFrame(data=mfd_dict)
    # mfd_df.to_csv(pq_input_folder+'region_params_mfd.csv')
    #
    # print('### GENERATING region_params_basic.csv')
    # generate_region_params_basic(vehroute_xml, edges_and_labels,
    #                              network=net, mfd_lines=mfd_fit_lines,
    #                              out_adr=pq_input_folder+'region_params_basic.csv')

    print('### GENERATING region_connection.csv')
    # generate_region_conncetion()
    for current_region, boundaries in boundary_ids.items():
        neighbors_outflows = {i: 0 for i in labels if i != current_region}
        for boundary, b_neighbors in boundaries.items():
            # surrounding_regions = list(np.unique(b_neighbors.values())).remove(regionid)
            for b_neighbor, neighbor_reg in b_neighbors.items():
                import pdb
                pdb.set_trace()
                if neighbor_reg != current_region:
                    # see if we are going TO  this neighbor link or going FROM this neighbor link
                    if A_goingto_B(boundary, b_neighbor, net):
                        neighborEdge = net.getEdge(b_neighbor)
                        # https://sumo.dlr.de/pydoc/sumolib.net.edge.html
                        speed = neighborEdge.getSpeed()
                        length = neighborEdge.getLength()
                        nLanes = neighborEdge.getLaneNumber()
                        vehicle_l = 4
                        vehicles_gap = 1.5
                        density = 1/(vehicle_l+vehicles_gap)  #veh/m
                        capacity = length/(vehicle_l+vehicles_gap)*nLanes
                        # neighbors_outflows[neighbor_reg] += net.getEdge(b_neighbor).get('capacity')
                        neighbors_outflows[neighbor_reg] += capacity
    # todo generate the file here -- use veh/min for max_outflow







