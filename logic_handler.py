import logic
from logic import *
import copy


# def get_segments(graph):
#     initial_segmentation.get_segments(graph)
#     merging.merge(graph)
#     # todo logic.boundary_adjustment(graph)
#     return graph.labels


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
