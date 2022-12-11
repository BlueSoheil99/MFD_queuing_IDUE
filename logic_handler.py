import logic
from logic import *
import copy
import numpy as np


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


