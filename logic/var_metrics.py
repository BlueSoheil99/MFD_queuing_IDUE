import numpy as np


def segment_var(graph, segment_id):
    mask = (graph.labels == segment_id)
    n = np.sum(mask > 0)
    densities = graph.densities[mask]
    mean = np.sum(densities)/n
    densities = (densities - mean)**2
    return np.sum(densities)/n


def segment_mean(graph, segment_id):
    mask = (graph.labels == segment_id)
    n = np.sum(mask > 0)
    densities = graph.densities[mask]
    return np.sum(densities) / n


def find_b(graph, a_id):
    neighbors = np.argwhere(graph.rag[a_id] != 0)
    b = neighbors[0]
    if len(neighbors) > 1:
        min_NS = NS_ab(graph, a_id, b)
        for neighbor in neighbors[1:]:
            if min_NS > NS_ab(graph, a_id, neighbor):
                b = neighbor
                min_NS = NS_ab(graph, a_id, b)

    return b


def NS_ab(graph, a, b):
    return segment_var(graph, a) + segment_var(graph, b) + (segment_mean(graph, a) - segment_mean(graph, b))**2


# todo def update_graph_NSs(graph):  ?


def NS(graph, a_id):
    b_id = find_b(graph, a_id)
    return NS_ab(graph, a_id, a_id)/NS_ab(graph, a_id, b_id)


def average_NS(graph):
    '''
    average NS which is used in evaluation of a given partitioning. Refer to Ji(2012) formula (11)
    :param graph:
    :return: Average NS
    '''
    IDs = np.unique(graph.labels)
    summation = 0
    for id in IDs:
        summation += NS(graph, id)
    return summation/len(IDs)


def TV(graph):
    labels = graph.labels
    seg_ids = np.unique(labels)
    N_i = np.array([len(labels[labels == seg_id]) for seg_id in seg_ids])  # it's not necessarily ordered
    TV = 0
    for id in seg_ids:
        TV += N_i[id]*segment_var(graph, id)
    return TV

