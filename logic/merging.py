import numpy as np


def merge(graph):
    labels = graph.labels.copy()
    region_A = graph.rag  # region adjacency matrix
    num_regions = region_A.shape[0]
    region_A[region_A == 0] = np.inf
    min_index = np.argmin(region_A)
    #or min_index = np.argmin(region_A[region_A>0]) instead of two lines above
    reg1 = min_index // num_regions
    reg2 = min_index % num_regions
    labels[labels == reg2] = reg1
    # this means you can finally have labels of for example 1, 2, and 4 with no 3 and you should fix it.
    labels += num_regions
    seg_IDs = np.unique(labels)
    num_regions -= 1
    for id in range(num_regions):
        old_id = seg_IDs[id]
        labels[labels == old_id] = id
    graph.set_labels(labels, calculate_rag=True)
