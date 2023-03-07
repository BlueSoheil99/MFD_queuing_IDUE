import os
import numpy as np
from Graph import Graph
import logic_handler as logic
import io_handler as io
from MFD import Plot_MFD as MFD


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
    print(np.unique(labels))
    return labels


if __name__ == '__main__':
    path_to_file = 'Data/manual detected edges in regions'
    input_addresses = "config.yaml"
    MFD_start_time = 18000.00
    MFD_end_time = 36000.00

    net, edges, densities, adj_mat = io.get_network(input_addresses)
    graph = Graph(adj_mat, densities)

    segment_ids = files_to_dict(path_to_file)
    graph.set_labels(_get_manual_segment_labels(np.array(list(edges)), segment_ids))

    logic.print_metrics(graph, new_NS=False)
    io.show_network(net, edges, graph.labels)

    MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time)
    MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time, separated=True)
    MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time, separated=True, normalized=False)
    print(segment_ids)
