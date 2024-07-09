import pandas as pd
import scipy.io
import numpy as np
from matplotlib import pyplot as plt


def create_dep_lookup_table(routefile):
    dep_lookup_table = {'id':[], 'depart':[]}
    for trip in routefile.findall('./trip'):
        dep_lookup_table['id'].append(trip.get('id'))
        dep_lookup_table['depart'].append(trip.get('depart'))
    df = pd.DataFrame(data=dep_lookup_table)
    df.set_index('id', inplace=True)
    return df


def get_original_route(trip):
    try:
        final_route = trip.findall('route')[0]
    except:
        final_route = trip.findall('routeDistribution')[0].findall('route')[-2]
        # in case there are multiple routes, the last one is the main one - The one we should consider for demand
    return final_route


def generate_demand_mat(net_edges_and_labels:dict, vehroute_xml, routefile_xml, increase_percentage=0,
                        time_interval=1, sim_start=18000, sim_steps=180000, out_adr='output/pq_input/demand.mat'):
    # 1- MAKE EMPTY NUMPY ARRAY
    n_regions = len(np.unique(np.array(list(net_edges_and_labels.values()))))
    matrix = np.zeros((n_regions, n_regions, sim_steps))
    depart_lookup = create_dep_lookup_table(routefile_xml)
    # print(depart_lookup)

    # 2- READ THE DEMAND FILE
    for vehicle in vehroute_xml.findall('./vehicle'):
        if vehicle.get('type') == 'passenger':
            # the actual demand comes from the demand (route) file.
            # The vehroute file gives us the actual departure time which could be delayed from
            # the desired dep. time from actual demand
            veh_id = vehicle.get('id')
            dep_time = depart_lookup.loc[veh_id, 'depart']  # desired departure time
            # dep_time = vehicle.get('depart')  # actual departure time
            dep_step = int(float(dep_time) // time_interval)-int(sim_start//time_interval)

            if dep_step>=0 and dep_step<sim_steps:
                # for route in vehicle.iter('route'):
                route = get_original_route(vehicle)
                route_edges = route.get('edges').split()
                origin, destination = None, None

                for edge in route_edges[:7]:
                    if net_edges_and_labels.get(edge) is not None:
                        origin = net_edges_and_labels[edge]
                        break

                for edge in reversed(route_edges[-7:]):
                    if net_edges_and_labels.get(edge) is not None:
                        destination = net_edges_and_labels[edge]
                        break

                if origin is not None and destination is not None:
                    matrix[origin, destination, dep_step] += 1
                else:
                    print(f'vehicle {vehicle.get("id")} not valid origin or destination')
                    # todo make these okay
                    # one problem is with route replacements (see aug 11 slides)

    # 3- SAVE THE MATRIX IN MATLAB FORMAT
    name = out_adr.split('/')[-1]
    name = name.split('.')[0]
    scipy.io.savemat(out_adr, mdict={name: matrix})

    # 4- SHOW THE DEMAND
    # n_origins, n_destinations, dep_steps =np.shape(matrix)
    # window_size = 120 #seconds
    # total_destinations = np.sum(matrix, axis=0)
    # total_origins = np.sum(matrix, axis=1)
    # _draw_aggregated_data(total_destinations, window_size, n_destinations, sim_start,
    #                      label=f'generated trips for each destination. aggregation window: {window_size}s')
    # _draw_aggregated_data(total_origins, window_size, n_destinations, sim_start,
    #                      label=f'generated trips for each origin. aggregation window: {window_size}s')
    print('...demand generation DONE...')
    return matrix

#
# def _draw_aggregated_data(mat, window_size, n_lines, sim_start, label):
#     for i in range(n_lines):
#         x, data = _aggregate(mat[i, :], window_size=window_size)
#         plt.plot(x, data, label=f'region {i}')
#     plt.legend()
#     plt.title(label)
#     plt.xticks(x[::10], _get_hour(x, start=sim_start)[::10], rotation=45)
#     plt.show()
#
#
# def _aggregate(observations, window_size=10):
#     aggregated_list = []
#     window_start_indices = range(0, len(observations), window_size)
#     for i in range(0, len(observations), window_size):
#         window_end_index = min(i + window_size, len(observations))
#         window_sum = sum(observations[i:window_end_index])
#         aggregated_list.append(window_sum)
#     return list(window_start_indices), aggregated_list
#
#
# def _get_hour(indices, start=18000):
#     indices = [start+i for i in indices]
#     indices = [f'{i // 3600}:{(i%3600)//60}' for i in indices]
#     return indices