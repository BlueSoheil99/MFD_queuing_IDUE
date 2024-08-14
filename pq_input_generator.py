import yaml
import io_handler as io
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt

from Graph import Graph
import logic_handler as logic

from input_for_pq.demand_mat_gen import generate_demand_mat
from input_for_pq.region_params_gen import generate_region_params_basic, generate_equations_df
from input_for_pq.region_connection_gen import generate_region_connections

from inout import Plot_MFD
from input_for_pq import draw_plots


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


def get_vehicle_accumulation_and_completion(routes_and_times, segmentation_dict):
    labels = sorted(np.unique(list(segmentation_dict.values())))
    vehicle_accumulation = np.zeros((len(labels), 12*3600))
    vehicle_completion = np.zeros((len(labels), 12*3600))
    invalid_trips = 0

    for tripID in routes_and_times.keys():
        tripdata = routes_and_times[tripID]
        index = tripdata['departure']//10
        trip_edges = tripdata['route times']
        # if tripID == '205760':
        #     print('danger!')

        last_region = None
        for edge in trip_edges.keys():
            last_region = segmentation_dict.get(edge)
            if last_region is not None:
                break
        if last_region is None:
            invalid_trips += 1
            continue  # go to the next trip

        for edge, traveltime in trip_edges.items():
            label = segmentation_dict.get(edge)
            new_index = (traveltime/10) + index
            ### for vehicle accumulation:
            if label is not None:
                vehicle_accumulation[label, int(index):int(new_index)] += 1
                if label != last_region: # the case where the trip exits a region
                    vehicle_completion[last_region, int(index)] += 1
                    # we add '1' completion to the time that this trip finished
                    # traveling on its previous edge which was for the last region
                last_region = label
            else:
                vehicle_accumulation[last_region, int(index):int(new_index)] += 1
            index = new_index
        # the case where the trip is finished
        vehicle_completion[last_region, int(index)] += 1
        # here 'index' is when the trip finished traveling on its last edge of its route

    print(f'invalid trips: {invalid_trips}')
    return vehicle_accumulation, vehicle_completion


if __name__ == '__main__':
    '''
    for more information on what this codes outputs should be, look at output/pq_input/readme.md
    
    In this code we work on:
    config.csv
    demand.mat,
    region_connection.csv,
    region_params_mfd.csv,
    region_params_basic.csv 
    '''

    # read config file and related network and files
    config_address = 'config files/pq_input_generation config.yaml'
    tripinfo_adr, demand_adr, vehroute_adr, pq_input_folder, routes_and_times_adr, routes_and_times_adr_cong = \
        _read_yaml(['trip_info', 'demand_file', 'veh_route', 'pq_input_folder', 'veh_route_time', 'veh_route_time_cong'],
                   config_address)

    print('reading xml files')
    demand_xml = _readxml(demand_adr)
    vehroute_xml = _readxml(vehroute_adr)

    with open(routes_and_times_adr, "rb") as f:
        routes_and_times = pickle.load(f)
        f.close()
    with open(routes_and_times_adr_cong, "rb") as f:
        routes_and_times_cong = pickle.load(f)
        f.close()

    print('reading segmented network')
    net, edges, densities, adj_mat, labels = io.get_network(config_address)
    graph = Graph(adj_mat, densities, labels)
    io.show_network(net, edges, graph.labels)

    edges_and_labels = {key: value for key, value in zip(edges, labels)}
    # todo edges_and_labels = add_nearest_labels_for_forgotten_edges(edges_and_labels, net)

    # Generate inputs for perimeter control/point queue model codes
    print('### GENERATING config.csv')
    config_csv_keys = ['model_type', 'time_interval (s)', 'simulation_steps', 'demand_stop_step', 'min_outflow_zero']
    config_dict = {key: [val] for key, val in zip(config_csv_keys, _read_yaml(config_csv_keys, config_address))}
    print(config_dict)
    data = pd.DataFrame(config_dict)
    data.to_csv(pq_input_folder+'config.csv', index=False)

    print('### GENERATING demand.mat')
    time_interval, sim_start = _read_yaml(['time_interval (s)', 'sim_start'], config_address)
    demand_matrix = generate_demand_mat(edges_and_labels, vehroute_xml, demand_xml,
                                        increase_percentage=0,
                                        time_interval=float(time_interval),
                                        sim_start=int(sim_start),
                                        sim_steps=int(config_dict['demand_stop_step'][0]),
                                        out_adr=pq_input_folder+'demand.mat')

    print('### GENERATING graphs')
    window_size = 60  # seconds
    num_labels = len(np.unique(labels))
    if num_labels > 10:
        draw_plots.set_colormap(plt.cm.tab20)

    # show figures from the calibrated simulation
    vehicle_accumulation, vehicle_completion = get_vehicle_accumulation_and_completion(routes_and_times, edges_and_labels)
    draw_plots.show_vehicle_accumulation(vehicle_accumulation, np.unique(labels), int(sim_start))
    draw_plots.draw_aggregated_data(vehicle_completion, window_size, num_labels, int(sim_start),
                                    label=f'completed trips for each region. aggregation window: {window_size}s')
    draw_plots.draw_empirical_completion_rates(vehicle_accumulation, vehicle_completion, window_size,
                                               label='calibrated sim. Completion rates')

    # from the congested simulation
    vehicle_accumulation, vehicle_completion = get_vehicle_accumulation_and_completion(routes_and_times_cong, edges_and_labels)
    completion_lines = draw_plots.draw_empirical_completion_rates(vehicle_accumulation, vehicle_completion, window_size,
                                                                  label='Trips exited from/finished in each region \nempirical comp. rate')

    # Showing trip generation trends
    n_origins, n_destinations, dep_steps = np.shape(demand_matrix)
    window_size = 120  # seconds
    total_destinations = np.sum(demand_matrix, axis=0)
    total_origins = np.sum(demand_matrix, axis=1)
    draw_plots.draw_aggregated_data(total_destinations, window_size, n_destinations, int(sim_start),
                                    label=f'generated trips for each destination. aggregation window: {window_size}s')
    draw_plots.draw_aggregated_data(total_origins, window_size, n_destinations, int(sim_start),
                                    label=f'generated trips for each origin. aggregation window: {window_size}s')


    print('### GENERATING region_params_mfd.csv')
    completion_df = generate_equations_df(completion_lines)
    completion_df['Region'] = completion_df['Region'] + 1  # adjusting labels for PQ code use
    completion_df.to_csv(pq_input_folder + 'region_params_mfd_c.csv', index=False)

    MFD_start_time = 18000.00
    MFD_end_time = 36000.00  # after 5:10 hours
    boundary_ids = logic.get_boundary_IDs(graph, edges, get_neighbors=True)
    segment_ids = logic.get_segment_IDs(graph, list(edges))
    mfd_fit_lines = Plot_MFD.MFD_plotter((segment_ids, boundary_ids), separated=True, normalized=False,
                                         start_time=MFD_start_time, end_time=MFD_end_time, num_vs_prod=True)
    mfd_df = generate_equations_df(mfd_fit_lines)
    mfd_df['Region'] = mfd_df['Region']+1  # adjusting labels for PQ code use
    mfd_df.to_csv(pq_input_folder+'region_params_mfd.csv', index=False)


    print('### GENERATING region_params_basic.csv')
    # capacity_n can be adjusted based on MFD investigation
    params_df = generate_region_params_basic(routes_and_times, edges_and_labels, network=net, mfd_lines=mfd_fit_lines)
    params_df['Region'] = params_df['Region']+1  # adjusting labels for PQ code use
    params_df['avg_trip_length (m)'] = round(params_df['avg_trip_length (m)']*3, 1)
    params_df.to_csv(pq_input_folder+'region_params_basic.csv', index=False)
    draw_plots.draw_calculated_completion_rates(vehicle_accumulation, window_size, mfd_fit_lines, params_df,
                                                label='MFD function / averge trip length*3 \ncalculated comp. rate/3')

    print('### GENERATING region_connection.csv')
    signal_info_adr = _read_yaml(['signal_info_adr'], config_address)[0]
    signal_info = pd.read_csv(signal_info_adr)
    connection_df = generate_region_connections(net, labels, boundary_ids, signal_info, vehicle_l=4, minGap=1.4, tau=1)
    # adjusting labels for PQ code use
    connection_df['start_region'] = connection_df['start_region']+1
    connection_df['end_region'] = connection_df['end_region']+1
    connection_df.to_csv(pq_input_folder+'region_connection.csv', index=False)






