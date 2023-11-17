import scipy.io
import numpy as np


def generate_demand_mat(net_edges_and_labels:dict, vehroute_xml, time_interval=1, sim_start=18000, sim_steps=180000, out_adr='output/pq_input/demand.mat'):
    # 1- MAKE EMPTY NUMPY ARRAY
    n_regions = len(np.unique(np.array(list(net_edges_and_labels.values()))))
    matrix = np.zeros((n_regions, n_regions, sim_steps))

    # 2- READ TRIPINFO.XML FILE
    for vehicle in vehroute_xml.findall('./vehicle'):
        if vehicle.get('type') == 'passenger':
            if vehicle.get('id') in ['442_442_170:301.0:304.0', '5000_440_26062:393.0:414.0']:
                print('debugggg')
            dep_step = int(float(vehicle.get('depart')) // time_interval)-int(sim_start//time_interval)
            # TODO this might be wrong
            for route in vehicle.iter('route'):
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
                break  # in case there are multiple routes, the first one is the final one

    # 3- SAVE THE MATRIX IN MATLAB FORMAT
    name = out_adr.split('/')[-1]
    name = name.split('.')[0]
    scipy.io.savemat(out_adr, mdict={name: matrix})
    print('...demand generation DONE...')