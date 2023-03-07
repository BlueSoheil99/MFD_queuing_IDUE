import logic
from logic import var_metrics, initial_segmentation, merging
import copy
import numpy as np


def print_metrics(graph, new_NS=True, NS_boundary_limit=0):
    labels = np.unique(graph.labels)
    print('mean densities:', str([round(var_metrics.segment_mean(graph, i), 3) for i in labels]))
    print('mean variance:', str([round(var_metrics.segment_var(graph, i), 3) for i in labels]))
    print('"b"s: ', str([var_metrics.find_b(graph, i) for i in labels]))
    print('NSs:', str([round(var_metrics.NS(graph, i), 4) for i in labels]))
    print('average NS:', str(round(var_metrics.average_NS(graph), 4)))
    if new_NS:
        print('new NSs:', str([round(var_metrics.NS(graph, i, NS_boundary_limit), 4) for i in labels]))
        print('average new NS:', str(round(var_metrics.average_NS(graph, NS_boundary_limit), 4)))
        print('new "b"s: ', str([var_metrics.find_b(graph, i, NS_boundary_limit) for i in labels]))
    print('TV:', str(round(var_metrics.TV(graph))))
    print('#of links: ', str([sum(graph.labels == i) for i in labels]))
    print(graph.rag[:, :, 0])
    print('')

def get_metrics(graph):
    NS = logic.get_NS(graph)
    TV = logic.get_TV(graph)
    return NS, TV


def make_partitions(graph, max_clusters):
    for i in range(max_clusters-1):
        initial_segmentation.get_segments(graph)
    graphs = list()
    graphs.append(copy.deepcopy(graph))
    while len(graphs) != max_clusters:
        merging.merge(graph)
        graphs.append(copy.deepcopy(graph))
    answers = dict()
    for i in range(len(graphs)):
        NS, TV = get_metrics(graphs[i])
        answers[max_clusters-i] = graphs[i].labels, NS, TV
    # todo use NSs to find the optimal number of clusters
    # todo include boundary_adjustment
    return answers


def get_segment_IDs(graph, edgeID_list):
    edgeID_list = np.array(edgeID_list)
    labels = np.unique(graph.labels)
    lookup = dict()
    for i in labels:
        args = np.argwhere(graph.labels==i)
        args = args.flatten()
        lookup[i] = list(edgeID_list[args])
    return lookup


