import numpy as np
from scipy.linalg import eigh
from logic.var_metrics import segment_var
from sklearn.cluster import KMeans


def get_parent_id(graph):
    # todo what are parent's characteristics?
    segments = np.unique(graph.labels)
    p = segments[0]
    for i in range(len(segments)):
        if segment_var(graph, segments[i]) > segment_var(graph, p):
            p = segments[i]
        elif segment_var(graph, segments[i]) == segment_var(graph, p):
            n1 = np.sum(graph.labels == p)
            n2 = np.sum(graph.labels == segments[i])
            if n2 > n1:
                p = segments[i]
    return p


def get_W_and_D(graph, mask):
    W = np.copy(graph.similarities)
    args_to_delete = np.argwhere(mask == 0)
    W = np.delete(W, args_to_delete, axis=0)
    W = np.delete(W, args_to_delete, axis=1)
    D = np.diag(np.sum(W, axis=1))
    return W, D


def get_segments(network):
    parent = get_parent_id(network)
    mask = (network.labels == parent)
    W, D = get_W_and_D(network, mask)
    # we should solve (D-W)y = l.D.y where y is eigenvector and equals (1+x)-b(1-x).
    # y vector will eventually come from 0=yT.D.1
    # now how to find x? y = (1+x) - (1-x)*[(x+1)T.d_list/(1-x)T.d_list]. take another look at shi2000.
    # Why did they change y to x in their eigenvalue system?
    eigvals, eigvecs = eigh((D-W), D, eigvals_only=False, subset_by_index=[0, 1])
    x = eigvecs[:, 1]
    # you should do the bi-partitioning. x values are not 0 and 1. they're real values. Is clustering OK?
    # clustering with k = 2 on nodes in parent cluster
    new_clusters = KMeans(n_clusters=2).fit(x.reshape(-1, 1))
    new_clusters = new_clusters.labels_
    n = len(np.unique(network.labels))
    # when segments start from 0, the biggest label is n-1, so we assign label n to a new segment and keep parent label
    # for the other segment
    new_clusters[new_clusters == 1] = n
    new_clusters[new_clusters == 0] = parent
    # make sure that new clusters are mapped to big graph using masks
    new_labels = np.copy(network.labels)
    counter = 0
    for i in range(len(mask)):
        if mask[i] == 1:
            new_labels[i] = new_clusters[counter]
            counter += 1
    network.set_labels(new_labels.astype(int), calculate_rag=True)
