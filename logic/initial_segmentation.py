import numpy as np
from scipy.linalg import eigh, eig
from logic.var_metrics import segment_var
from sklearn.cluster import KMeans


def get_parent_id(graph):
    # todo what are parent's characteristics?
    segments = np.unique(graph.labels)
    variances = [segment_var(graph, i) for i in segments]
    variances = np.sqrt(variances)
    variances = [(variances[i] + sum(graph.labels == segments[i])) for i in range(len(segments))]
    p = np.argmax(variances)

    # segments = np.unique(graph.labels)
    # p = segments[0]
    # for i in range(len(segments)):
    #     if segment_var(graph, segments[i]) > segment_var(graph, p):
    #         p = segments[i]
    #     elif segment_var(graph, segments[i]) == segment_var(graph, p):
    #         n1 = np.sum(graph.labels == p)
    #         n2 = np.sum(graph.labels == segments[i])
    #         if n2 > n1:
    #             p = segments[i]
    return p


def get_W_and_D(graph, mask):
    W = np.copy(graph.similarities)
    args_to_delete = np.argwhere(mask == 0)
    W = np.delete(W, args_to_delete, axis=0)
    W = np.delete(W, args_to_delete, axis=1)
    D = np.sum(W, axis=1)
    D[D==0] = 0.01  #todo better criterion
    # To make D from a semi-definite matrix to a definite matrix
    D = np.diag(D)
    return W, D


def check(a, b):  # DEBUG
    """
    DEBUG
    In  a @ vi = λ * b @ vi see if:
    1) a is a real symmetric matrix
    2) b is a real symmetric matrix
    3) b is positive definite
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eigh.html#scipy.linalg.eigh
    :param: a and b in generalized eigenvalue system a @ vi = λ * b @ vi
    :return: Three bools for three conditions above
    """
    ans1 = (a == a.T).all()
    ans2 = (b == b.T).all()
    eigs = np.linalg.eigvals(b)
    ans3 = np.all(eigs > 0)
    semi = np.all(eigs >= 0)  # do we have b as positive semi-definite?
    indexes = np.argwhere(eigs == 0)
    return [ans1, ans2, ans3]


def get_segments(network):
    parent = get_parent_id(network)
    mask = (network.labels == parent)
    W, D = get_W_and_D(network, mask)
    # we should solve (D-W)y = l.D.y where y is eigenvector and equals (1+x)-b(1-x).
    # y vector will eventually come from 0=yT.D.1
    # now how to find x? y = (1+x) - (1-x)*[(x+1)T.d_list/(1-x)T.d_list].
    # In shi2000, they changed y to x in their eigenvalue system. because by discretizing y we will simply reach x!

    conditions = check((D-W), D)  # DEBUG
    # In order to be able to use eigh function, all conditions must be True,
    # function check shows that matrix D is gonna be semidefinite and I should see if I can get y with another function
    #  or if the system cannot be solved. The solution? I just changed zeros on D's diagonal into a small number!
    eigvals, eigvecs = eigh((D-W), D, eigvals_only=False, subset_by_index=[0, 1])
    x = eigvecs[:, 1]

    # you should do the bi-partitioning. x values are not 0 and 1. they're real values. todo Is clustering OK?
    # clustering with k = 2 on nodes in parent cluster
    new_clusters = KMeans(n_clusters=2).fit(x.reshape(-1, 1))
    new_clusters = new_clusters.labels_
    uniq = np.unique(new_clusters)  # DEBUG

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
