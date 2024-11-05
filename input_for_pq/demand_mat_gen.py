import pandas as pd
import scipy.io
import numpy as np
import random
from matplotlib import pyplot as plt


def _increase_demand_lookupTable(lookup_table:pd.DataFrame, increase_percentage):
    print(f"before increase: {lookup_table['repetition'].sum()}")
    if increase_percentage == 0:
        pass
    else:
        sample_size = int(increase_percentage/100*lookup_table['repetition'].sum())
        added_ids = random.choices(lookup_table.index, k=sample_size)
        # for added_id in added_ids:
        #     lookup_table.loc[added_id, 'repetition'] = lookup_table.loc[added_id, 'repetition'] + 1
        added_id_counts = pd.Series(added_ids).value_counts()
        lookup_table.loc[added_id_counts.index, 'repetition'] += added_id_counts
    print(f"after increase: {lookup_table['repetition'].sum()}")


def create_dep_lookup_table(demandfile):
    dep_lookup_table = {'id':[], 'depart':[], 'repetition':[], 'fromTaz':[], 'toTaz':[]}
    for trip in demandfile.findall('./trip'):
        if trip.get('type') == 'passenger':
            dep_lookup_table['id'].append(trip.get('id'))
            dep_lookup_table['depart'].append(trip.get('depart'))
            dep_lookup_table['repetition'].append(1)
            dep_lookup_table['fromTaz'].append(trip.get('fromTaz'))
            dep_lookup_table['toTaz'].append(trip.get('toTaz'))
        else:
            pass
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


def generate_demand_mat(net_edges_and_labels: dict, pseudo_regions_lookup: dict,
                        vehroute_xml, demandfile_xml, increase_percentage=0,
                        time_interval=1, sim_start=18000, sim_steps=180000, out_dir='output/pq_input/'):
    # 1- MAKE EMPTY NUMPY ARRAY
    n_regions = len(np.unique(np.array(list(net_edges_and_labels.values()))))
    matrix = np.zeros((n_regions, n_regions, sim_steps))

    n_pseudo_regions = len(set(pseudo_regions_lookup.values()))
    matrix_pseudo = np.zeros((n_regions+n_pseudo_regions, n_regions+n_pseudo_regions, sim_steps))

    # 2 - make a lookup_table from deamnd_file and increase demand
    # copy trips in vehroute file, instead of final matrix,
    # so that both demand and demand_with_pseudo_regions matrices have same trips
    demand_lookup = create_dep_lookup_table(demandfile_xml)
    _increase_demand_lookupTable(demand_lookup, increase_percentage)

    # 3- READ THE DEMAND FILE
    for vehicle in vehroute_xml.findall('./vehicle'):
        if vehicle.get('type') == 'passenger':
            # the actual demand comes from the demand (route) file.
            # The vehroute file gives us the actual departure time which could be delayed from
            # the desired dep. time from actual demand
            veh_id = vehicle.get('id')
            dep_time = demand_lookup.loc[veh_id, 'depart']  # desired departure time
            # dep_time = vehicle.get('depart')  # actual departure time
            dep_step = int(float(dep_time) // time_interval)-int(sim_start//time_interval)

            if dep_step>=0 and dep_step<sim_steps:
                # for route in vehicle.iter('route'):
                route = get_original_route(vehicle)
                route_edges = route.get('edges').split()
                origin, destination = None, None
                oTaz, dTaz = demand_lookup.loc[veh_id, 'fromTaz'], demand_lookup.loc[veh_id, 'toTaz']

                for edge in route_edges[:7]:
                    if net_edges_and_labels.get(edge) is not None:
                        origin = net_edges_and_labels[edge]
                        break

                for edge in reversed(route_edges[-7:]):
                    if net_edges_and_labels.get(edge) is not None:
                        destination = net_edges_and_labels[edge]
                        break

                if origin is not None and destination is not None:
                    num_new_trips = demand_lookup.loc[veh_id, 'repetition']
                    matrix[origin, destination, dep_step] += num_new_trips

                    # now we add the trip to the matrix for simulation with pseudo regions(TAZs)
                    porigin = pseudo_regions_lookup.get(oTaz, 0)
                    pdest = pseudo_regions_lookup.get(dTaz, 0)
                    origin = (n_regions-1)+porigin if porigin!=0 else origin
                    destination = (n_regions-1)+pdest if pdest!=0 else destination
                    matrix_pseudo[origin, destination, dep_step] += num_new_trips

                else:
                    print(f'vehicle {vehicle.get("id")} not valid origin or destination')
                    # todo make these okay
                    # one problem is with route replacements (see aug 11 slides)
            else:
                # print(f'vehicle {vehicle.get("id")}')
                pass

    # 3 - increase demand
    print(f'number of trips: {matrix.sum()} - {matrix_pseudo.sum()}')
    # matrix = _increase_demand(matrix, sample_fraction=increase_percentage/100)
    # print(f'number of trips after {increase_percentage}% increase: {matrix.sum()}')

    # 4- SAVE THE MATRIX IN MATLAB FORMAT
    # name = out_adr.split('/')[-1]
    # name = name.split('.')[0]
    name='demand'
    scipy.io.savemat(out_dir+'demand.mat', mdict={name: matrix})
    scipy.io.savemat(out_dir+'demand_pseudoRegions.mat', mdict={name: matrix_pseudo})

    print('...demand generation DONE...')
    return matrix, matrix_pseudo


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



