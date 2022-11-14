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
    neighbors = graph.rag[a_id]
    return np.argmin(neighbors)


def NS_ab(graph, a, b):
    return segment_var(graph, a) + segment_var(graph, b) + (segment_mean(graph, a) - segment_mean(graph, b))**2

# todo: see if you need to eventually calculate NS for all clusters.
#  if so, just make NS_list in the graph instance so that you don't calculate NS multiple time for each segment
#  def update_graph_NSs(graph):


def NS(graph, a_id):
    b_id = find_b(graph, a_id)
    return NS_ab(graph, a_id, a_id)/NS_ab(graph, a_id, b_id)


def TV(graph):
    labels = graph.labels
    seg_ids = np.unique(labels)
    N_i = np.array([len(labels[labels == seg_id]) for seg_id in seg_ids])
    TV = 0
    for id in seg_ids:
        TV += N_i[id]*NS(graph, id)
    return TV

