import numpy as np

def get_rag(labels, adj_mat, densities):
    '''
        returns region adjacency matrix
        must be similar to skimage.future.graph.rag_mean_color
    :param labels:
    :param adj_mat:
    :param densities:
    :return: RAG

    psudo code:
    n = number of clusters
    rag = make a zero n*n array.
    mean_list = list(n)
    for each cluster x:
        find mean of cluster x
        for node in cluster x:
            S[node] = 0
            next = 0
            next_found = False
            for neighbor in adjacency_matrix[node]:
                if label[neighbor] != x:
                    rag[x, label[neighbor]] = 1
                    rag[label[neighbor], x] = 1 (maybe not needed)
    change 1s in rag into distance of cluster means
    '''

    num_regions = len(np.unique(labels))
    region_adj_mat = np.zeros((num_regions, num_regions))
    means_list = list()  # it should be filled in order

    for cluster_id in np.unique(labels):
        # S = [i for i in np.unique(labels) if labels[i] == cluster_id]
        n = labels.count(cluster_id)
        mask = labels[labels == cluster_id]
        means_list.append(sum(densities[mask])/n)
        for i in mask:
            if i == 1:
                neighbors = adj_mat[i]
                for neighbor in neighbors:
                    if labels[neighbor] != cluster_id:
                        region_adj_mat[cluster_id, labels[neighbor]] = 1

    for row in range(num_regions):
        for column in range(num_regions):
            if region_adj_mat[row, column] == 1:
                region_adj_mat[row, column] = abs(means_list[row] - means_list[column])

    return region_adj_mat


def merge(labels, adj_mat, densities):
    labels = np.array(labels)
    region_A = get_rag(labels, adj_mat, densities)
    num_regions = region_A.shape[0]
    min_index = np.argmin(region_A)
    reg1 = min_index // num_regions
    reg2 = min_index % num_regions
    # if labels start from 1, add 1 to these values
    bigger_region_num = max(reg1, reg2)
    smaller_region_num = min(reg1, reg2)
    labels[labels == bigger_region_num] = smaller_region_num
    # this means you can finally have labels of for example 1, 2, and 4 with no 3
    # the question is now: #todo should you fix it?
    # num_regions -= 1
    # different_labels = np.unique(labels)
    # old_new_labels = [(i, i) for i in different_labels]
    # old_new_labels[] = smaller_region_num
    # for i in range(num_regions):
    #     if different_labels[i] != bigger_region_num:
    #         # old_new_labels[different_labels[i]] = i
    #         labels[labels == different_labels[i]] = i
    #     else:
    #         new_label = smaller_region_num
    # i = 0
    # while i in range(num_regions):
    #
    #     i += 1

    return labels





