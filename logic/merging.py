import numpy as np


_ALPHA = 0.5


def merge(graph, alpha=_ALPHA, min_boundary=0, exclude_fixed_regions=True):

    """
    :param graph:
    :param alpha: accounts for the degree we consider number of boundaries into merging algo
    :param min_boundary: drops neighbors with fewer boundaries from consideration
    :return:
    """
    # first_unfixed_region = 0
    # if exclude_fixed_regions: first_unfixed_region = graph.first_unfixed_region

    RAG = _clean_rag(np.copy(graph.rag), min_boundary)  # region adjacency matrix
    region_A = -alpha * RAG[:, :, 0] + RAG[:, :, 1]  # if alpha is zero you basically don't need to have rag[:, :, 0]
    # region_A = graph.rag  # the ORIGINAL method
    num_regions = region_A.shape[0]
    # region_A[region_A == 0] = np.inf
    region_A = _invalids_to_inf(region_A, graph.fixed_regions)
    min_index = np.argmin(region_A)
    #or min_index = np.argmin(region_A[region_A>0]) instead of two lines above
    reg1 = (min_index // num_regions)
    reg2 = (min_index % num_regions)
    # reg1 = (min_index // num_regions) + first_unfixed_region
    # reg2 = (min_index % num_regions) + first_unfixed_region
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


def _invalids_to_inf(rag, fixed_regions):
    # print(rag)
    rag[rag == 0] = np.inf
    for region in fixed_regions:
        rag[region, :] = np.inf
        rag[:, region] = np.inf
    # print(rag)
    return rag
