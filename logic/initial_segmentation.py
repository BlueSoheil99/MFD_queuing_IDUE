import numpy as np
from scipy.linalg import eigh
from skimage.future import graph


def get_D(similarity_mat):
    return np.dot(np.sum(similarity_mat, axis=1), np.ones(similarity_mat.shape[0]))


def get_segments(similarity_mat):
    # we should solve (W-D)y = l.D.y where y is eigenvector and equals (1+x)-b(1-x).
    # y vector will eventually come from 0=yT.D.1
    D = get_D(similarity_mat)
    eigvals, eigvecs = eigh((similarity_mat-D), D, eigvals_only=False, subset_by_index=[0, 1])
    y = eigvecs[1]
    # todo now how to find x? y = (1+x) - (1-x)*[(x+1)T.d_list/(1-x)T.d_list]. take another look at shi2000
    x=y
    # todo you should do the bi-partitioning. x values are not 0 and 1. they're real values
    return (x+1)/2


def get_segments(similarity_mat):  # another way to implement.
    n = similarity_mat.shape[0]
    labels = np.linspace(0, n-1, n)
    labels = graph.cut_normalized(labels, similarity_mat, thresh=0.1, num_cuts=10, in_place=False)
    # todo set these appropriately- thresh should be low so that we get two segments each time
    # I feel you need to implement the whole thing (somehow copying skimage code) to be able to get a partition for each
    # number of cluster. cut_normalized function gives us one result and that's the optimal results. for now maybe you
    # can use it and get labels with like 10 different values and continue to implement mergeing section. But later you
    # may need to change this as discussed
    return labels

