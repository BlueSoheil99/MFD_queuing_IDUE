import numpy as np


_ALPHA = 0.5


def merge(graph, alpha=_ALPHA, min_boundary=0):
    """
    :param graph:
    :param alpha: accounts for the degree we consider number of boundaries into merging algo
    :param min_boundary: drops neighbors with fewer boundaries from consideration
    :return:
    """
    RAG = _clean_rag(np.copy(graph.rag), min_boundary)  # region adjacency matrix
    # x = RAG[0, 0]
    # print(x)
    region_A = -alpha * RAG[:, :, 0] + RAG[:, :, 1]  # id alpha is zero you basically don't need to have rag[:, :, 0]
    # region_A = graph.rag  # the ORIGINAL method
    # print(region_A)  # DEBUG
    num_regions = region_A.shape[0]
    region_A[region_A == 0] = np.inf
    min_index = np.argmin(region_A)
    #or min_index = np.argmin(region_A[region_A>0]) instead of two lines above
    reg1 = min_index // num_regions
    reg2 = min_index % num_regions
    _merge_segments(graph, reg1, reg2)


def _merge_segments(graph, reg1, reg2):
    labels = graph.labels.copy()
    num_regions = len(np.unique(labels))
    labels[labels == reg2] = reg1
    # this means you can finally have labels of for example 1, 2, and 4 with no 3 and you should fix it.
    labels += num_regions
    seg_IDs = np.unique(labels)
    num_regions -= 1
    for id in range(num_regions):
        old_id = seg_IDs[id]
        labels[labels == old_id] = id
    graph.set_labels(labels, calculate_rag=True)


def _clean_rag(rag, min_boundary):
    # we need a copy of the original RAG but with considering that neighbors with very low number of boundaries maybe
    # shouldn't be considered as neighbors
    # it is NOT an efficient code but it's ok as we have small 'n's.
    n = len(rag)
    RAG = np.zeros(rag.shape)
    for row in range(n):
        for column in range(n):
            if rag[row, column, 0] >= min_boundary:
                RAG[row, column] = rag[row, column]
    return RAG