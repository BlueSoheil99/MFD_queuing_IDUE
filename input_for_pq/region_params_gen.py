import numpy as np
import pandas as pd


def generate_region_params_basic(vehroute_output, segmentation_dict, network, mfd_lines, out_adr):
    labels = sorted(np.unique(list(segmentation_dict.values())))
    region_trip_length = {label: [] for label in labels}
    edge_lengths = {edgeid: network.getEdge(edgeid).getLength() for edgeid in segmentation_dict.keys()}

    taken_edges = 0
    unrecognized_edges = []
    unrecognized_trips = []

    for trip in vehroute_output.findall('vehicle'):
        trip_regions_length = {label: 0 for label in labels}
        try:
            final_route = trip.findall('route')[0]
        except:
            final_route = trip.findall('routeDistribution')[0].findall('route')[0]
        trip_edges = final_route.get('edges').split()
        taken_edges += len(trip_edges)

        for edge in trip_edges:
            if segmentation_dict.get(edge) is None:
                unrecognized_edges.append(edge)
            else:
                label = segmentation_dict[edge]
                trip_regions_length[label] += edge_lengths[edge]

        if all(value == 0 for value in trip_regions_length.values()):
            unrecognized_trips.append(trip)
        else:
            for label in labels:
                if trip_regions_length[label] != 0:
                    region_trip_length[label].append(trip_regions_length[label])
    print(f'- In total, {taken_edges} edges were taken in trips.\n'
          f'-- {len(np.unique(unrecognized_edges))} edges could not be recognized for {len(unrecognized_edges)} times\n'
          f'-- {len(unrecognized_trips)} trips could not be processed')

    avg_trip_length = {label: round(sum(region_trip_length[label]) / len(region_trip_length[label]), 2)
                       for label in labels}
    limit_n = [get_max_mfd(mfd_lines[i]) for i in labels]
    init_vehicles = [1] * len(labels)
    if_destination = [1] * len(labels)
    df = pd.DataFrame({'region': labels,
                       'limit_n': limit_n,
                       'avg_trip_length (m)': list(avg_trip_length.values()),
                       'init_vehicles': init_vehicles,
                       'if_destination': if_destination})
    df.to_csv(out_adr)
    return df


def get_max_mfd(mfd_fit):
    poly_function = np.poly1d(mfd_fit)
    poly_derivative = poly_function.deriv()
    critical_points = np.roots(poly_derivative)
    y_values = poly_function(critical_points)
    maximum_y = max(y_values)
    return round(maximum_y)

# def generate_region_params_mfd():
#     import
#     return 0
