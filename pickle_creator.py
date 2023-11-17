import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import io_handler
import pickle

Gaussian_Edge_Weight = 3
Gaussian_Neighbor_Weight = 1


def create_simple_pickle_file(src_adr='data/edge_data_output.xml',
                              out_adr="data/uniques_interval_data_occupancy.pickle"):
    create_smoothed_pickle_file(None, None, src_adr, out_adr, False, False)
    # tree = ET.parse(src_adr)
    # root = tree.getroot()
    #
    # unique_intervals = {}
    #
    # for interval in root.findall('./interval'):
    #     interval_id = interval.get("begin")
    #     unique_edges = {}
    #
    #     for edge in interval.iter("edge"):
    #         edge_id = edge.get("id")
    #
    #         if edge_id in unique_edges:
    #             unique_edges[edge_id] = {
    #                 "sampledSeconds": edge.get("sampledSeconds"),
    #                 "laneDensity": edge.get("laneDensity"),
    #                 "speed": edge.get("speed"),
    #                 "occupancy": edge.get("occupancy")
    #             }
    #         else:
    #             unique_edges[edge_id] = {
    #                 "sampledSeconds": edge.get("sampledSeconds"),
    #                 "laneDensity": edge.get("laneDensity"),
    #                 "speed": edge.get("speed"),
    #                 "occupancy": edge.get("occupancy")
    #             }
    #     unique_intervals[interval_id] = unique_edges
    # # return unique_intervals
    # with open(out_adr, "wb") as f:
    #     pickle.dump(unique_intervals, f)


def create_smoothed_pickle_file(adjacency_mat, edge_array, src_adr='data/edge_data_output._1min_interval.xml',
                                out_adr='data/1min_median_gaussian31_den_spd_occ.pickle', median=True, gaussian=True):
    tree = ET.parse(src_adr)
    root = tree.getroot()

    unique_intervals = {}

    for interval in root.findall('./interval'):
        interval_id = interval.get("begin")
        unique_edges = {}

        # reading the data for each interval
        features = ["sampledSeconds", "laneDensity", "speed", "occupancy"]
        for edge in interval.iter("edge"):
            edge_id = edge.get("id")

            # # 136 MB
            # edge_data = {feature: 0.0 if edge.get(feature) is None else float(edge.get(feature)) for feature in features}

            # # 25 MB
            # edge_data = {feature: None if edge.get(feature) is None else float(edge.get(feature)) for feature in features}

            # # 30 MB
            # edge_data = {feature: 0.0 if edge.get(feature) is None else edge.get(feature) for feature in features}

            # # similar to Pranati, 93 MB
            edge_data = {feature: edge.get(feature) for feature in features}

            unique_edges[edge_id] = edge_data

        # smoothing the data for each interval
        neighbor_DFs = {}
        if median or gaussian:
            for edge_id in unique_edges.keys():
                if len(np.argwhere(edge_array == edge_id)):
                    neighbors = _get_neighbor_IDs(edge_id, edge_array, adjacency_mat)
                    df = _get_neighbors_dataframe(neighbors, unique_edges)
                    neighbor_DFs[edge_id] = df

        if median:
            for edge_id in unique_edges.keys():
                if len(np.argwhere(edge_array == edge_id)):
                    # neighbors = _get_neighbor_IDs(edge_id, edge_array, adjacency_mat)
                    # df = _get_neighbors_dataframe(neighbors, unique_edges)
                    # unique_edges[edge_id] = _smooth(features, unique_edges[edge_id], df, True, False)
                    unique_edges[edge_id] = _smooth(features, unique_edges[edge_id], neighbor_DFs[edge_id], True, False)
        if gaussian:
            for edge_id in unique_edges.keys():
                if len(np.argwhere(edge_array == edge_id)):
                    # neighbors = _get_neighbor_IDs(edge_id, edge_array, adjacency_mat)
                    # df = _get_neighbors_dataframe(neighbors, unique_edges)
                    # unique_edges[edge_id] = _smooth(features, unique_edges[edge_id], df, False, True)
                    unique_edges[edge_id] = _smooth(features, unique_edges[edge_id], neighbor_DFs[edge_id], False, True)

        unique_intervals[interval_id] = unique_edges
        print(f'interval ID: {interval_id}  -> DONE')

    with open(out_adr, "wb") as f:
        pickle.dump(unique_intervals, f)


def _get_neighbor_IDs(edge_id, array_of_edges, adjacency_mat):
    x = np.argwhere(array_of_edges == edge_id)
    edge_index = np.argwhere(array_of_edges == edge_id)[0][0]
    neighbors = np.argwhere(adjacency_mat[edge_index] == 1)
    neighbors = neighbors.flatten()
    neighbors = array_of_edges[neighbors]
    return neighbors


def _get_neighbors_dataframe(neighbor_ids, data_dict):
    neighbors_data = list(map(data_dict.get, neighbor_ids))
    d = {key: list(neighbor[key] for neighbor in neighbors_data) for key in neighbors_data[0].keys()}
    neighbors_data = pd.DataFrame(data=d)
    return neighbors_data


def _smooth(feature_names, edge_data, neighbor_data, median, gaussian):
    if median:
        for feature in feature_names:
            # if _is_extreme(edge_data[feature]): # todo fix it
            if edge_data[feature] == 0:
                edge_data[feature] = np.median(neighbor_data.loc[:, feature])
    if gaussian:
        for feature in feature_names:
            # x = neighbor_data['speed'].astype(float)
            # if sum(x) > 0:
            #     print('edhey!')
            vals = [edge_data[feature]]+list(neighbor_data.loc[:, feature])
            w = [Gaussian_Edge_Weight]+[Gaussian_Neighbor_Weight]*len(neighbor_data)
            edge_data[feature] = np.average(vals, weights=w)
    return edge_data


if __name__ == '__main__':
    ## making simple picke file
    create_simple_pickle_file(src_adr='data/edge_data_output_min.xml',
                              out_adr="data/edge_data_output_min.pickle")

    ## making smoothed pickle file
    # _, list_of_edges, _, adjacency_matrix = io_handler.get_network()
    # print(list_of_edges)
    # create_smoothed_pickle_file(adjacency_matrix, list_of_edges, median=True, gaussian=True)


    #
    # with open("data/test 0.pickle", "rb") as f:
    #     file_0 = pickle.load(f)
    #     f.close()
    # with open("data/test 1.pickle", "rb") as f:
    #     file_1 = pickle.load(f)
    #     f.close()
    # with open("data/test 2.pickle", "rb") as f:
    #     file_2 = pickle.load(f)
    #     f.close()
    # with open("data/edge_vehicle_output_min0.pickle", "rb") as f:
    #     file_p = pickle.load(f)
    #     f.close()
    # print('done')

