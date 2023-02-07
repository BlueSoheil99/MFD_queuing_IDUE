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
    net_edges = file["edges_name"]
    edges_to_remove = file["edges_to_remove_name"]
    minor_links = file["minor_links"]
    highways_tunnels = file["highways_and_tunnels"]

    return network_name, feature_name, feature, net_edges, interval_begin, interval_end,\
        edges_to_remove, minor_links, highways_tunnels


def get_node_pair(net, edge_id):
    source = net.getEdge(edge_id).getFromNode().getID()
    sink = net.getEdge(edge_id).getToNode().getID()
    return source, sink


def get_edge_index(edges_diction, edge_id):
    edge_list = list(edges_diction.keys())
    i = edge_list.index(edge_id) if edge_id in edge_list else None
    return i


def make_adjacency(net, edges_diction):
    n_edges = len(edges_diction.keys())
    adjacency_mat = np.zeros((n_edges, n_edges), dtype=int)
    raw_edges = net.getEdges()

    for edge in raw_edges:
        edge_id = edge.getID()
        incoming_edges = net.getEdge(edge_id).getIncoming().keys()
        outgoing_edges = net.getEdge(edge_id).getOutgoing().keys()
        new_id = cleanID(edge_id)
        a = get_edge_index(edges_diction, new_id)
        for incoming in incoming_edges:
            new_id = cleanID(incoming.getID())
            b = get_edge_index(edges_diction, new_id)
            if a != b and (a is not None and b is not None):
                adjacency_mat[a][b] = 1
                adjacency_mat[b][a] = 1

        for outgoing in outgoing_edges:
            new_id = cleanID(outgoing.getID())
            b = get_edge_index(edges_diction, new_id)
            if a != b and (a is not None and b is not None):
                adjacency_mat[a][b] = 1
                adjacency_mat[b][a] = 1

    return adjacency_mat


def read_network(net_fname, net_edges_fname, edges_to_remove, minor_links, highways_tunnels):
    net = sumonet.readNet(net_fname)
    connected_edges = read_edgeID_subnetwork(net_edges_fname)
    net, edges = clean_network(net, connected_edges, edges_to_remove, minor_links, highways_tunnels)
    return net, edges


def cleanID(edge_id):
    # hashtag_index = edge_id.find("#")
    # if hashtag_index == -1:
    #     new_id = edge_id
    # else:
    #     new_id = edge_id[:hashtag_index]
    # return new_id
    return edge_id



def clean_network(net, connected_edges, edges_to_remove, minor_links, highways_tunnels):
    remove_edge_ids = []
    for file in [edges_to_remove, minor_links, highways_tunnels]:
        with open(file) as f:
            for line in f:
                remove_edge_ids.append(line.rstrip())
    # with open(edges_to_remove) as f:
    #     remove_edge_ids = []
    #     for line in f:
    #         remove_edge_ids.append(line.rstrip())

    clean_net = sumonet.Net()
    clean_edges = set()
    edges = net.getEdges()
    for edge in edges:
        new_id = cleanID(edge.getID())
        if edge.getID() in connected_edges \
                and new_id not in clean_edges \
                and new_id not in remove_edge_ids:
            clean_net.addEdge(new_id, edge.getFromNode(), edge.getToNode(),
                              edge.getPriority(), edge.getFunction(), edge.getName(), edge.getType())
            clean_edges.add(new_id)
    edges = clean_net.getEdges()
    return net, edges


def read_edgeID_subnetwork(fname):
    with open(fname) as f:
        edge_ids = []
        for line in f:
            edge_ids.append(line.rstrip().split(":")[1])
    return edge_ids

def filter_edges(net_fname):
    net, nodes, edges = read_network(net_fname)


def read_node_info(nodes):
    node_diction = {node.getID(): node.getCoord() for node in nodes}
    return node_diction


def read_edge_info(edges, feature_name, option, interval_begin, interval_end):
    edge_diction = {edge.getID(): 0 for edge in edges}
    edge_stats = sumoxml.parse(feature_name, "interval")
    num_lanes_per_edge = np.zeros(len(edge_diction))
    edge_names = list(edge_diction.keys())
    # as we need density for specific time intervals
    for interval in edge_stats:
        if interval_begin * 3600 <= float(interval.begin) < interval_end * 3600:
            n_no_attr = 0
            for edge in interval.edge:
                try:
                    new_id = cleanID(edge.id)
                    edge_diction[new_id] += float(edge.getAttribute(option))
                    i = edge_names.index(new_id)
                    num_lanes_per_edge[i] += 1
                except:
                    # print("{} has no attribute: {}".format(edge.id, option))
                    n_no_attr += n_no_attr

    # take mean of the density for cases that one edge with multiple lanes
    for i in range(len(num_lanes_per_edge)):
        if num_lanes_per_edge[i] > 0:
            edge_id = edge_names[i]
            edge_diction[edge_id] = edge_diction[edge_id] / num_lanes_per_edge[i]
    print("Total number of edges without {} are {}".format(option, n_no_attr))
    print("{} edges have zero density".format(list(edge_diction.values()).count(0)))

    return edge_diction
