import os
import numpy as np
from Graph import Graph
import logic_handler as logic
from logic import var_metrics
import io_handler as io
from MFD import Plot_MFD as MFD


def print_metrics(graph):
    labels = np.unique(graph.labels)
    print('mean densities:', str([round(var_metrics.segment_mean(graph, i), 3) for i in labels]))
    print('mean variance:', str([round(var_metrics.segment_var(graph, i), 3) for i in labels]))
    print('NSs:', str([round(var_metrics.NS(graph, i), 4) for i in labels]))
    print('average NS:', str(round(var_metrics.average_NS(graph), 4)))
    print('TV:', str(round(var_metrics.TV(graph))))
    print('')


def files_to_dict(dir_path):
    if not os.path.exists(dir_path):
        raise ValueError(f"Directory {dir_path} does not exist.")

    result = {}
    i = 0
    for filename in os.listdir(dir_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'r') as f:
                values = f.read().splitlines()
            result[i] = values
            i += 1

    return result


def _get_manual_segment_labels(edges, segment_ids):
    labels = np.zeros(len(edges)).astype(int)
    x = len(segment_ids.keys())
    labels[:] = x
    for seg_id in segment_ids.keys():
        for edge in segment_ids[seg_id]:
            i = np.argwhere(edges == edge)
            labels[i] = seg_id
    return labels


path_to_file = 'Data/manual detected edges in regions'
input_addresses = "config.yaml"
MFD_start_time = 18000.00
MFD_end_time = 36000.00

net, edges, densities, adj_mat = io.get_network(input_addresses)
graph = Graph(adj_mat, densities)

segment_ids = files_to_dict(path_to_file)
graph.set_labels(_get_manual_segment_labels(np.array(list(edges)), segment_ids))

print_metrics(graph)
io.show_network(net, edges, graph.labels)

segment_ids = logic.get_segment_IDs(graph, list(edges))
MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time)

