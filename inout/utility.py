import yaml
import sumolib.net as sumonet
import sumolib.xml as sumoxml
import numpy as np


def init_config(fname="config.yaml"):
    file = yaml.safe_load(open(fname))
    data_folder = file["data_folder"]
    network_name = "{}{}".format(data_folder, file["network_name"])
    feature_name = "{}{}".format(data_folder, file["info_name"])
    feature = file["feature"]
    interval_begin = file["interval_begin"]
    interval_end = file["interval_end"]

    return network_name, feature_name, feature, interval_begin, interval_end


def get_node_pair(net, edge_id):
    source = net.getEdge(edge_id).getFromNode().getID()
    sink = net.getEdge(edge_id).getToNode().getID()
    return source, sink


def get_node_index(node_diction, node_id):
    node_list = list(node_diction.keys())
    i = node_list.index(node_id)
    return i


def make_adjacency(net, node_diction, edges_diction):
    n_nodes = len(node_diction.keys())
    adjacency_mat = np.zeros((n_nodes, n_nodes), dtype=int)

    for key, value in edges_diction.items():
        source, sink = get_node_pair(net, key)
        i = get_node_index(node_diction, source)
        j = get_node_index(node_diction, sink)
        adjacency_mat[i][j] = 1
    return adjacency_mat


def read_network(net_fname):
    net = sumonet.readNet(net_fname)
    nodes = net.getNodes()
    edges = net.getEdges()
    return net, nodes, edges


def read_node_info(nodes):
    node_diction = {node.getID(): node.getCoord() for node in nodes}
    return node_diction


def read_edge_info(edges, feature_name, option, interval_begin):
    edge_diction = {edge.getID(): 0 for edge in edges}
    edge_stats = sumoxml.parse(feature_name, "interval")
    # as we need density for specific time intervals
    for interval in edge_stats:
        if interval.begin == interval_begin:
            i = 0
            for edge in interval.edge:
                try:
                    edge_diction[edge.id] += float(edge.getAttribute(option))
                except:
                    print("{} has no attribute: {}".format(edge.id, option))
                    i = i + 1
            print("Total Number of Edges without {} are {}".format(option, i))
    return edge_diction
