import scipy.io
import numpy as np


def generate_demand_mat(net_edges_and_labels:dict, vehroute_xml, time_intervals=180000, out_adr='output/pq_input/demand.mat'):
    # 1- MAKE EMPTY NUMPY ARRAY
    n_regions = len(np.unique(np.array(list(net_edges_and_labels.values()))))
    matrix = np.zeros((n_regions, n_regions, time_intervals))

    # 2- READ TRIPINFO.XML FILE
    for vehicle in vehroute_xml.findall('./vehicle'):
        if vehicle.get('type') == 'passenger':
            dep_step = int(float(vehicle.get('depart')) * 10)-18000  # because simulation step interval is 0.1 seconds
            # todo using 18000 is not clean
            for route in vehicle.iter('route'):
                route_edges = route.get('edges').split()
                origin, destination = None, None

                for edge in route_edges[:5]:
                    if net_edges_and_labels.get(edge) is not None:
                        origin = net_edges_and_labels[edge]
                        break

                for edge in reversed(route_edges[-5:]):
                    if net_edges_and_labels.get(edge) is not None:
                        destination = net_edges_and_labels[edge]
                        break

                if origin is not None and destination is not None:
                    matrix[origin, destination, dep_step] += 1
                else:
                    print(f'vehicle {vehicle.get("id")} not valid origin or destination')
                    # todo make these okay

    # 3- SAVE THE MATRIX IN MATLAB FORMAT
    name = out_adr.split('/')[-1]
    name = name.split('.')[0]
    scipy.io.savemat(out_adr, mdict={name: matrix})
    print('...demand generation DONE...')