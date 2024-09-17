import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt

# def generate_region_params_basic(vehroute_output, edge_output_minute_address, segmentation_dict, network, mfd_lines):
#     with open(edge_output_minute_address, "rb") as f:
#         edge_data_minute = pickle.load(f)
#         f.close()
#
#     labels = sorted(np.unique(list(segmentation_dict.values())))
#     lengths_traveled_in_regions = {label: [] for label in labels}
#     edge_lengths = {edgeid: network.getEdge(edgeid).getLength() for edgeid in segmentation_dict.keys()}
#
#     taken_edges = 0
#     unrecognized_edges = []
#     unrecognized_trips = []
#
#     for trip in vehroute_output.findall('vehicle'):
#         trip_regional_traveled_length = {label: 0 for label in labels}
#         trip_regional_traveled_time = {label: 0 for label in labels}
#         try:
#             final_route = trip.findall('route')[0]
#         except:
#             final_route = trip.findall('routeDistribution')[0].findall('route')[-2]
#         trip_edges = final_route.get('edges').split()
#         taken_edges += len(trip_edges)
#         edge_travel_times = get_travel_times(trip, trip_edges, edge_data_minute)
#
#         for edge in trip_edges:
#             label = segmentation_dict.get(edge)
#             if label is None:
#                 unrecognized_edges.append(edge)
#             else:
#                 trip_regional_traveled_length[label] += edge_lengths[edge]
#                 # trip_regional_traveled_time[label] += edge_travel_times[edge]
#
#         if all(value == 0 for value in trip_regional_traveled_length.values()):
#             unrecognized_trips.append(trip)
#         else:
#             for label in labels:
#                 if trip_regional_traveled_length[label] != 0:
#                     lengths_traveled_in_regions[label].append(trip_regional_traveled_length[label])
#
#     print(f'- In total, {taken_edges} edges were taken in trips.\n'
#           f'-- {len(np.unique(unrecognized_edges))} edges could not be recognized for {len(unrecognized_edges)} times\n'
#           f'-- {len(unrecognized_trips)} trips could not be processed')
#     with open('output/pq_input/invalid_edges.txt','w') as f:
#         f.write("\nedge:".join(np.unique(unrecognized_edges)))
#
#
#     avg_trip_length = {label: round(sum(lengths_traveled_in_regions[label]) / len(lengths_traveled_in_regions[label]), 2)
#                        for label in labels}
#     # limit_n = [round(get_max_mfd_x(mfd_lines[i])*2.5) for i in labels]
#     capacity_n = [round(get_max_mfd_x(mfd_lines[i])) for i in labels]
#     init_vehicles = [1] * len(labels)
#     if_destination = [1] * len(labels)
#     df = pd.DataFrame({'Region': labels,
#                        'capacity_n': capacity_n,
#                        'avg_trip_length (m)': list(avg_trip_length.values()),
#                        'init_vehicles': init_vehicles,
#                        'if_destination': if_destination})
#     return df


def generate_region_params_basic(routes_and_times, segmentation_dict, network, mfd_lines):
    labels = sorted(np.unique(list(segmentation_dict.values())))
    lengths_traveled_in_regions = {label: [] for label in labels}
    times_traveled_in_regions = {label: [] for label in labels}
    edge_lengths = {edgeid: network.getEdge(edgeid).getLength() for edgeid in segmentation_dict.keys()}
    taken_edges = 0             # for debug
    unrecognized_edges = []     # for debug
    unrecognized_trips = []     # for debug

    for tripID in routes_and_times.keys():
        tripdata = routes_and_times[tripID]
        trip_edges = tripdata['route times']
        taken_edges += len(trip_edges.keys())
        trip_regional_traveled_length = {label: 0 for label in labels}
        trip_regional_traveled_time = {label: 0 for label in labels}
        ##
        for edge, traveltime in trip_edges.items():
            label = segmentation_dict.get(edge)
            if label is None:
                unrecognized_edges.append(edge)
            else:
                trip_regional_traveled_length[label] += edge_lengths[edge]
                trip_regional_traveled_time[label] += traveltime
        ##
        if all(value == 0 for value in trip_regional_traveled_length.values()):
            unrecognized_trips.append(tripID)
        else:
            for label in labels:
                if trip_regional_traveled_length[label] != 0:
                    lengths_traveled_in_regions[label].append(trip_regional_traveled_length[label])
                    times_traveled_in_regions[label].append(trip_regional_traveled_time[label])

    print(f'- In total, {taken_edges} edges were taken in trips.\n'
          f'-- {len(np.unique(unrecognized_edges))} edges could not be recognized for {len(unrecognized_edges)} times\n'
          f'-- {len(unrecognized_trips)} trips could not be processed')
    with open('output/pq_input/invalid_edges.txt','w') as f:
        f.write("\nedge:".join(np.unique(unrecognized_edges)))

    avg_trip_length = {label: round(np.average(lengths_traveled_in_regions[label],
                                               weights=times_traveled_in_regions[label]), 1) for label in labels}

    fig, axs = plt.subplots(len(labels)//2+1, 2)
    fig.suptitle('lengths traveled in each region')
    for i in range(len(labels)):
        label=labels[i]
        ax = axs.flat[i]
        ax.hist(lengths_traveled_in_regions[label], rwidth=0.90, label=f'region {label}')
        ax.legend()
    plt.show()

    fig, axs = plt.subplots(len(labels)//2+1, 2)
    fig.suptitle('Times traveled in each region')
    for i in range(len(labels)):
        label=labels[i]
        ax = axs.flat[i]
        ax.hist(times_traveled_in_regions[label], rwidth=0.90, label=f'region {label}')
        ax.legend()
    plt.show()

    capacity_n = [round(get_max_mfd_x(mfd_lines[i])) for i in labels]
    jam_n = [round(get_jam_mfd_x(mfd_lines[i])) for i in labels]
    init_vehicles = [1] * len(labels)
    if_destination = [1] * len(labels)
    df = pd.DataFrame({'Region': labels,
                       'capacity_n': capacity_n,
                       'avg_trip_length (m)': list(avg_trip_length.values()),
                       'init_vehicles': init_vehicles,
                       'if_destination': if_destination,
                       'jam_n': jam_n})
    return df


def get_max_mfd_x(mfd_fit):
    poly_function = np.poly1d(mfd_fit)
    poly_derivative = poly_function.deriv()
    critical_points = np.roots(poly_derivative)
    return min(critical_points)
    # y_values = poly_function(critical_points)
    # maximum_y = max(y_values)
    # return round(maximum_y)


def get_jam_mfd_x(mfd_fit):
    poly_function = np.poly1d(mfd_fit)
    poly_derivative = poly_function.deriv()
    critical_points = np.roots(poly_derivative)
    return max(critical_points)


def get_travel_times(trip, route, edge_data_minute):
    dep = int(round(float(trip.get('depart')), 0))
    arr = int(round(float(trip.get('arrival')), 0))

    print(f'--- travel time: {arr-dep}')

    travel_times = {edge: [] for edge in route}
    for interval_id, edges_data in edge_data_minute.items():
        minute = float(interval_id)//60
        if (minute >= dep//60) and (minute <= arr//60):
            interval_times = []
            for edge in route:
                travel_time = edges_data[edge].get('traveltime')
                if travel_time is not None:
                    travel_time = float(travel_time)
                # else:
                #     travel_time = free_flow_travel_times[edge]

                    travel_times[edge].append(travel_time)
                    interval_times.append(travel_time)
            print(f'at {interval_id} avg. travel time is {sum(interval_times)}')

    # travel_times = {edge: round(np.mean(travel_times[edge]),1) for edge in travel_times.keys()}
    travel_times = {edge: np.mean(travel_times[edge]) for edge in travel_times.keys() if len(travel_times[edge]) > 0}
    print(f'estimated travel time: {sum(travel_times.values())}')
    return travel_times


def _get_mfd_equation(mfd_coefficients):
    eq = ''
    for d in range(len(mfd_coefficients)):
        if d != 0 and mfd_coefficients[d]>=0:
            eq += '+'
        n_str = ''
        degree = len(mfd_coefficients) - d-1
        if degree==1:
            n_str = '* n '
        elif degree>1:
            n_str = f'* n^{degree} '
        eq += np.format_float_scientific(mfd_coefficients[d], precision=4) + n_str
    return eq


def generate_equations_df(equation_lines_dict):
    eq_str = [_get_mfd_equation(mfd) for mfd in equation_lines_dict.values()]
    eq_dict = {'Region': list(equation_lines_dict.keys()), 'mfd': eq_str}
    df = pd.DataFrame(data=eq_dict)
    return df