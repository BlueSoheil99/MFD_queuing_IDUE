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
from input_for_pq.region_params_gen import generate_region_params_basic
from input_for_pq.region_connection_gen import generate_region_connections

from inout import Plot_MFD
from inout import draw_plots


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


def get_mfd_equation(mfd_coefficients):
    # eq = str(np.poly1d(mfd_coefficients)).split('\n')[1].replace('x', 'n')
    eq = ''
    for d in range(len(mfd_coefficients)):
        if d != 0 and mfd_coefficients[d]>0:
            eq += '+'
        n_str = ''
        degree = len(mfd_coefficients) - d-1
        if degree==1:
            n_str = '* n '
        elif degree>1:
            n_str = f'* n^{degree} '
        eq += np.format_float_scientific(mfd_coefficients[d], precision=4) + n_str
    return eq


def _draw_aggregated_data(mat, window_size, n_lines, sim_start, label):
    cmap = plt.cm.tab20
    for i in range(n_lines):
        x, data = _aggregate(mat[i, :], window_size=window_size)
        plt.plot(x, data, label=f'region {i}', color=cmap(i))
    plt.legend()
    plt.title(label)
    plt.xticks(x[::10], _get_hour(x, start=sim_start)[::10], rotation=45)
    plt.show()


def _aggregate(observations, window_size=10):
    aggregated_list = []
    window_start_indices = range(0, len(observations), window_size)
    for i in range(0, len(observations), window_size):
        window_end_index = min(i + window_size, len(observations))
        window_sum = sum(observations[i:window_end_index])
        aggregated_list.append(window_sum)
    return list(window_start_indices), aggregated_list


def _get_hour(indices, start=18000):
    indices = [int(start+i) for i in indices]
    indices = [f'{i // 3600}:{(i%3600)//60}' for i in indices]
    return indices


def show_vehicle_accumulation(accumulation:dict, labels, sim_start):
    cmap = plt.cm.tab20
    for label in labels:
        plt.plot(accumulation[label], label=f'region {label+1}', color=cmap(label))
    plt.legend()
    plt.title('Vehicle accumulations')
    plt.xlabel('Time')
    plt.ylabel('#Vehicles')
    x = np.linspace(0,len(accumulation[0]), len(accumulation[0]))
    plt.xticks(x[::15*60], _get_hour(x, start=sim_start)[::15*60], rotation=45)
    plt.show()


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
    region_params_basic.csv --except limit_n which should be set manually based on MFD investigation
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
    config_csv_keys = ['model_type', 'time_interval (s)', 'simulation_steps', 'demand_stop_step']
    config_dict = {key: [val] for key, val in zip(config_csv_keys, _read_yaml(config_csv_keys, config_address))}
    print(config_dict)
    data = pd.DataFrame(config_dict)
    data.to_csv(pq_input_folder+'config.csv', index=False)

    # # ---------- demand.mat
    print('### GENERATING demand.mat')
    time_interval, sim_start = _read_yaml(['time_interval (s)', 'sim_start'], config_address)
    demand_matrix = generate_demand_mat(edges_and_labels, vehroute_xml, demand_xml,
                                        time_interval=float(time_interval),
                                        sim_start=int(sim_start),
                                        sim_steps=int(config_dict['demand_stop_step'][0]),
                                        out_adr=pq_input_folder+'demand.mat')


    print('### GENERATING graphs')
    window_size = 60  # seconds
    num_labels = len(np.unique(labels))
    cmap = plt.cm.tab10
    if num_labels > 10: cmap = plt.cm.tab20

    # show figures from the calibrated simulation
    vehicle_accumulation, vehicle_completion = get_vehicle_accumulation_and_completion(routes_and_times, edges_and_labels)
    draw_plots.show_vehicle_accumulation(vehicle_accumulation, np.unique(labels), int(sim_start))
    draw_plots.draw_aggregated_data(vehicle_completion, window_size, num_labels, int(sim_start),
                          label=f'completed trips for each region. aggregation window: {window_size}s')


    # todo: put this into draw plot.py
    for i in range(num_labels):
        # making minute level aggregations
        x1, N = _aggregate(vehicle_accumulation[i, :5*3600], window_size=window_size)
        x2, C = _aggregate(vehicle_completion[i, :5*3600], window_size=window_size)
        N, C = np.array(N) / window_size, np.array(C) / window_size
        plt.scatter(N, C, s=3, color=cmap(i))
        # fitting a 3rd degree line
        polyfit_c = np.polyfit(N, C, 3)
        # x_curve = np.linspace(min(N), max(N) + 500, 1000)
        x_curve = np.linspace(min(N), int(max(N)*1.1), 1000)
        y_curve = np.polyval(polyfit_c, x_curve)
        # plt.plot(x_curve, y_curve, color=cmap(i), linewidth=0.6)
        plt.plot(x_curve, y_curve, color=cmap(i), label=f'region {i+1}')
    plt.legend()
    plt.title('calibrated sim. Completion rates')
    plt.xlabel('Number of vehicles')
    plt.ylabel('veh/sec')
    plt.show()

    # from the congested simulation
    vehicle_accumulation, vehicle_completion = get_vehicle_accumulation_and_completion(routes_and_times_cong, edges_and_labels)
    # completion_lines = draw_plots.draw_completion_rates()

    completion_lines = dict()
    for i in range(num_labels):
        # making minute level aggregations
        x1, N = _aggregate(vehicle_accumulation[i, :5*3600], window_size=window_size)
        x2, C = _aggregate(vehicle_completion[i, :5*3600], window_size=window_size)
        N, C = np.array(N) / window_size, np.array(C) / window_size
        # plt.scatter(N, C, s=3, color=cmap(i))
        # fitting a 3rd degree line
        polyfit_c = np.polyfit(N, C, 3)
        completion_lines[i] = polyfit_c
        # x_curve = np.linspace(min(N), max(N) + 500, 1000)
        x_curve = np.linspace(min(N), int(max(N)*0.95), 1000)
        y_curve = np.polyval(polyfit_c, x_curve)
        # plt.plot(x_curve, y_curve, color=cmap(i), linewidth=0.6)
        plt.plot(x_curve, y_curve, color=cmap(i), label=f'region {i+1}')
    plt.legend()
    # plt.title('Congesetd sim. Completion rates\n Empirical format')
    plt.title('Trips exited from/finished in each region \nempirical comp. rate')
    plt.xlabel('Number of vehicles')
    plt.ylabel('veh/sec')
    plt.show()

    n_origins, n_destinations, dep_steps = np.shape(demand_matrix)
    window_size = 120  # seconds
    total_destinations = np.sum(demand_matrix, axis=0)
    total_origins = np.sum(demand_matrix, axis=1)
    _draw_aggregated_data(total_destinations, window_size, n_destinations, int(sim_start),
                          label=f'generated trips for each destination. aggregation window: {window_size}s')
    _draw_aggregated_data(total_origins, window_size, n_destinations, int(sim_start),
                          label=f'generated trips for each origin. aggregation window: {window_size}s')

    #
    print('### GENERATING region_params_mfd.csv')
    MFD_start_time = 18000.00
    MFD_end_time = 36000.00  # after 5:10 hours
    boundary_ids = logic.get_boundary_IDs(graph, edges, get_neighbors=True)
    segment_ids = logic.get_segment_IDs(graph, list(edges))
    #
    mfd_fit_lines = Plot_MFD.MFD_plotter((segment_ids, boundary_ids), separated=True, normalized=False,
                                         start_time=MFD_start_time, end_time=MFD_end_time, num_vs_prod=True)


    mfd_str = [get_mfd_equation(mfd) for mfd in mfd_fit_lines.values()]
    mfd_dict = {'Region': list(mfd_fit_lines.keys()), 'mfd': mfd_str}
    mfd_df = pd.DataFrame(data=mfd_dict)
    mfd_df['Region'] = mfd_df['Region']+1 # adjusting labels for PQ code use
    mfd_df.to_csv(pq_input_folder+'region_params_mfd.csv', index=False)


    # mfd_fit_lines = completion_lines
    # mfd_str = [get_mfd_equation(mfd) for mfd in mfd_fit_lines.values()]
    # mfd_dict = {'Region': list(mfd_fit_lines.keys()), 'mfd': mfd_str}
    # mfd_df = pd.DataFrame(data=mfd_dict)
    # mfd_df['Region'] = mfd_df['Region']+1 # adjusting labels for PQ code use
    # mfd_df.to_csv(pq_input_folder+'region_params_mfd_c.csv', index=False)

    print('### GENERATING region_params_basic.csv')
    params_df = generate_region_params_basic(routes_and_times, edges_and_labels, network=net, mfd_lines=mfd_fit_lines)
    params_df['Region'] = params_df['Region']+1 # adjusting labels for PQ code use
    params_df.to_csv(pq_input_folder+'region_params_basic.csv', index=False)


    for i in range(num_labels):
        # making minute level aggregations
        x1, N = _aggregate(vehicle_accumulation[i, :5*3600], window_size=window_size)
        N = np.array(N) / window_size
        x_curve = np.linspace(min(N), int(max(N)*0.95), 1000)

        y_curve = np.polyval(mfd_fit_lines[i], x_curve)
        y_curve =y_curve/float(params_df[params_df['Region']==i+1]['avg_trip_length (m)'])
        # plt.plot(x_curve, y_curve, color=cmap(i), linewidth=0.6)
        plt.plot(x_curve, y_curve, color=cmap(i), label=f'region {i+1}')
    plt.legend()
    plt.title('MFD function / averge trip length*3 \ncalculated comp. rate/3')
    plt.xlabel('Number of vehicles')
    plt.ylabel('veh/second')
    plt.show()

    mfd_fit_lines = completion_lines
    mfd_str = [get_mfd_equation(mfd) for mfd in mfd_fit_lines.values()]
    mfd_dict = {'Region': list(mfd_fit_lines.keys()), 'mfd': mfd_str}
    mfd_df = pd.DataFrame(data=mfd_dict)
    mfd_df['Region'] = mfd_df['Region']+1 # adjusting labels for PQ code use
    mfd_df.to_csv(pq_input_folder+'region_params_mfd_c.csv', index=False)

    # for i in range(num_labels):
    #     # making minute level aggregations
    #     x1, N = _aggregate(vehicle_accumulation[i, :5*3600], window_size=window_size)
    #
    #     x_curve = np.linspace(min(N), int(max(N)*0.95), 1000)
    #     y_curve = np.polyval(mfd_fit_lines[i], x_curve)
    #     # plt.plot(x_curve, y_curve, color=cmap(i), linewidth=0.6)
    #     plt.plot(x_curve, y_curve, color=cmap(i), label=f'region {i+1}')
    # plt.legend()
    # plt.title('Completion rates')
    # plt.xlabel('Number of vehicles')
    # plt.ylabel('veh/second')
    # plt.show()

    print('### GENERATING region_connection.csv')
    signal_info_adr = _read_yaml(['signal_info_adr'], config_address)[0]
    signal_info = pd.read_csv(signal_info_adr)
    connection_df = generate_region_connections(net, labels, boundary_ids, signal_info, vehicle_l=4, minGap=1.4, tau=1)
    # adjusting labels for PQ code use
    connection_df['start_region'] = connection_df['start_region']+1
    connection_df['end_region'] = connection_df['end_region']+1
    connection_df.to_csv(pq_input_folder+'region_connection.csv', index=False)






