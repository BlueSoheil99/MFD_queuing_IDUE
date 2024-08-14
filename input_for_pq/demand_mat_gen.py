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
                    num_new_trips = 1
                    matrix[origin, destination, dep_step] += num_new_trips
                else:
                    print(f'vehicle {vehicle.get("id")} not valid origin or destination')
                    # todo make these okay
                    # one problem is with route replacements (see aug 11 slides)

    # 3 - increase demand
    print(f'number of trips: {matrix.sum()}')
    matrix = _increase_demand(matrix, sample_fraction=increase_percentage/100)
    print(f'number of trips after {increase_percentage}% increase: {matrix.sum()}')

    # 4- SAVE THE MATRIX IN MATLAB FORMAT
    name = out_adr.split('/')[-1]
    name = name.split('.')[0]
    scipy.io.savemat(out_adr, mdict={name: matrix})

    print('...demand generation DONE...')
    return matrix


def _increase_demand(array, sample_fraction=0.2):
    if sample_fraction == 0:
        return array
    # Find the indices and values of the non-zero elements
    non_zero_indices = np.argwhere(array != 0)
    non_zero_values = array[non_zero_indices[:, 0], non_zero_indices[:, 1], non_zero_indices[:, 2]]

    # Calculate the weights based on the values
    weights = non_zero_values

    # Calculate the number of elements to sample (sample_fraction of non-zero elements)
    # sample_size = int(sample_fraction * len(non_zero_values))
    sample_size = int(sample_fraction * non_zero_values.sum())

    # Randomly select sample_size indices from the non-zero indices with the specified weights
    sampled_indices = np.random.choice(len(non_zero_values), size=sample_size, replace=True, p=weights / weights.sum())

    # sampled_elements = non_zero_values[sampled_indices]
    sampled_indices = non_zero_indices[sampled_indices]
    # for idx in sampled_element_indices:
    #     array[idx[0], idx[1], idx[2]] += 1
    np.add.at(array, (sampled_indices[:, 0], sampled_indices[:, 1], sampled_indices[:, 2]), 1)
    return array



