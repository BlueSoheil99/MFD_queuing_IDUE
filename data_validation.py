from Graph import Graph
import io_handler as io
from inout import utility as util
import numpy as np


def get_network(input_addresses="config.yaml"):
    net_fname, info_fname, option, net_edges_fname, interval_begin, interval_end, edges_to_remove, \
    minor_edges, highways = util.init_config(input_addresses)
    # read network
    net, edges = util.read_network(net_fname, net_edges_fname, edges_to_remove, minor_edges, highways)
    # organize the network info into dictionaries
    density_diction = util.read_edge_info(edges, info_fname, 'density', interval_begin, interval_end)
    speed_diction = util.read_edge_info(edges, info_fname, 'speed', interval_begin, interval_end)

    adjacency_matrix = util.make_adjacency(net, density_diction)
    array_of_edges = np.array(list(density_diction.keys()))
    array_of_densities = np.array(list(density_diction.values()))
    array_of_speeds = np.array(list(speed_diction.values()))
    return net, array_of_edges, array_of_densities, array_of_speeds, adjacency_matrix


if __name__ == '__main__':
    '''This file is created for making a comparison between simulation outputs and SDOT data (flow)'''

    input_addresses = "config files/data_validation_config.yaml"
    net, edges, densities, speeds, adj_mat = get_network(input_addresses)
    flows = densities*speeds*3.6
    # generate flow
    graph = Graph(adj_mat, flows)
    io.show_network(net, edges, flows, colormap_name="binary")

    # todo add plots from SDOT data

    # segment_ids = files_to_dict(path_to_file)
    # graph.set_labels(_get_manual_segment_labels(np.array(list(edges)), segment_ids))
    #
    # logic.print_metrics(graph, new_NS=False)
    # io.show_network(net, edges, graph.labels)
    #
    # MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time)
    # MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time, separated=True)
    # MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time, separated=True, normalized=False)
    # print(segment_ids)
