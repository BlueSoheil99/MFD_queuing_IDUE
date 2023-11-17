import numpy as np


class Graph:
    def __init__(self, adjacency_matrix, density_list, label_list):
        self.n = adjacency_matrix.shape[0]
        self.adjacency = adjacency_matrix
        self.densities = density_list
        self.distances, self.similarities = _preprocess_network(self.adjacency, self.densities)
        # self.labels = np.zeros(self.n).astype(int)
        self.labels = label_list
        self.first_unfixed_region = max(label_list)
        # self.first_unfixed_region = 0
        self.rag = np.zeros((1, 1, 2))  # Region Adjacency Graph.
        # / RAG[0]-> shows number of boundary links/ RAG[1]-> shows difference between mean densities

    def __len__(self):
        return self.n

    def set_labels(self, labels, calculate_rag=True):
        self.labels = labels
        if calculate_rag:
            self.rag = _get_rag(labels, self.adjacency, self.densities, self.first_unfixed_region)

    def smooth_densities(self, median=True, gaussian=True):
        if median:
            self.densities = _salt_and_pepper(self.adjacency, self.densities)
        if gaussian:
            self.densities = _gaussian_smooth(self.adjacency, self.densities)

    def get_similarity_matrix(self, mask=None):
        if mask is None:
            return _get_similarity_matrix(self.distances, self.densities)
        else:
            args_to_delete = np.argwhere(mask == 0)
            dis = np.copy(self.distances)
            dis = np.delete(dis, args_to_delete, axis=0)
            dis = np.delete(dis, args_to_delete, axis=1)
            den = np.copy(self.densities)
            den = np.delete(den, args_to_delete)
            return _get_similarity_matrix(dis, den)

    def get_neighbor_indices_and_regions(self, edge_index):
        neighbors_idx = np.argwhere(self.adjacency[edge_index] == 1).flatten()
        return {index: self.labels[index] for index in neighbors_idx}

    def get_boundary_indices(self, get_neighbors=False):
        # returns a dictionary: keys: segment IDs,
        #                       values: {boundary edges for each segment:their neighbors and their segments}
        # if you want neighbors of boundaries: get_neighbors=True
        labels = np.unique(self.labels)
        boundaries_and_neighbors = dict()
        for i in labels:
            region_boundaries_neighbors = dict()
            region_edges = np.argwhere(self.labels == i).flatten()
            for edge_index in region_edges:
                neighbors = self.get_neighbor_indices_and_regions(edge_index)
                # contains "neighbor_index: neighbor_region_id" pairs
                for k, v in neighbors.items():
                    if v != i:
                        region_boundaries_neighbors[edge_index] = neighbors
                        break
            boundaries_and_neighbors[i] = region_boundaries_neighbors.copy()

        if get_neighbors:
            return boundaries_and_neighbors
        else:
            return {key: list(value.keys()) for key, value in boundaries_and_neighbors.items()}


def _preprocess_network(adj_mat, densities):
    # dist_mat = _get_distance_matrix(adj_mat)
    # todo: uncomment the line above when calculating distance matrix really makes a difference
    dist_mat = np.copy(adj_mat)
    W = _get_similarity_matrix(dist_mat, densities)
    return dist_mat, W


def _get_distance_matrix(adj_mat):
    n = adj_mat.shape[0]
    p = 1  # power of A
    A_p = np.copy(adj_mat)
    distance_mat = np.copy(adj_mat)
    X = np.ones((n, n)) - adj_mat - np.eye(n)
    # X(i,j) shows if we have detected the shortest path between i and j or not (if not, it's 1). X(i, i)s are 0 because
    # I assume that distance_mat(i,i)=0.
    # using algorithms like Dijkstra is time intensive
    while X.any():
        print(X)
        A_p = np.dot(A_p, adj_mat)  #todo tiimmmeee.
        p += 1
        new_walks = np.logical_and(X, A_p)
        X -= new_walks
        distance_mat += new_walks * p
    return distance_mat


def _get_similarity_matrix(distance_matrix, density_list):
    n = distance_matrix.shape[0]
    W = np.zeros((n, n))
    # todo: how should be W[i,i]s (diagonal values)?
    # todo make the code below faster
    sigma = np.var(density_list)
    for row in range(n):
        for col in range(row, n):
            if distance_matrix[row, col] == 1:
                # todo the main formula is different than the one in paper. It doesn't include sigma
                similarity = np.exp(-(density_list[row] - density_list[col]) ** 2 / sigma)
                W[row, col] = similarity
                W[col, row] = similarity
    return W


# def _get_rag(labels, adj_mat, densities, starting_index):
#     '''
#         returns region adjacency matrix
#         must be similar to skimage.future.graph.rag_mean_color
#     :param labels:
#     :param adj_mat:
#     :param densities:
#     :return: RAG
#
#     psudo code:
#     n = number of clusters
#     rag = make a zero n*n array.
#     mean_list = list(n)
#     for each cluster x:
#         find mean of cluster x
#         for node in cluster x:
#             S[node] = 0
#             next = 0
#             next_found = False
#             for neighbor in adjacency_matrix[node]:
#                 if label[neighbor] != x:
#                     rag[x, label[neighbor]] = 1
#                     rag[label[neighbor], x] = 1 (maybe not needed)
#     change 1s in rag into [#boundary links, distance of cluster means]
#     '''
#
#     num_regions = len(np.unique(labels))
#     region_adj_mat = np.zeros((num_regions, num_regions, 2))
#     means_list = list()  # it should be filled in order
#
#     for cluster_id in np.unique(labels):
#         # S = [i for i in np.unique(labels) if labels[i] == cluster_id]
#         # n = labels.count(cluster_id)
#         n = np.sum(labels == cluster_id)
#         mask = (labels == cluster_id)
#         means_list.append(sum(densities[mask]) / n)
#         # for i in mask:
#         for i in range(len(mask)):
#             if mask[i] == 1:
#                 # neighbors = adj_mat[i]
#                 neighbors = np.argwhere(adj_mat[i] == 1).flatten()
#                 for neighbor in neighbors:
#                     if labels[neighbor] != cluster_id:
#                         # region_adj_mat[cluster_id, labels[neighbor]] = 1
#                         region_adj_mat[cluster_id, labels[neighbor], 0] += 1
#
#     for row in range(num_regions):
#         for column in range(num_regions):
#             # if region_adj_mat[row, column] == 1:
#             if region_adj_mat[row, column, 0] != 0:
#                 region_adj_mat[row, column, 1] = abs(means_list[row] - means_list[column])
#                 # todo: take a look at formula (18) in Ji(2012) and see if changes are needed
#     return region_adj_mat

def _get_rag(labels, adj_mat, densities, starting_index):
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
    change 1s in rag into [#boundary links, distance of cluster means]
    '''

    num_regions = len(np.unique(labels)) - starting_index
    region_adj_mat = np.zeros((num_regions, num_regions, 2))
    means_list = list()  # it should be filled in order

    for cluster_id in np.unique(labels):
        if cluster_id>=starting_index:
            # n = np.sum(labels == cluster_id)
            mask = (labels == cluster_id)
            # means_list.append(sum(densities[mask]) / n)
            means_list.append(np.mean(densities[labels==cluster_id]))
            for i in range(len(mask)):
                if mask[i] == 1:
                    # neighbors = adj_mat[i]
                    neighbors = np.argwhere(adj_mat[i] == 1).flatten()
                    for neighbor in neighbors:
                        if labels[neighbor] != cluster_id and labels[neighbor]>=starting_index:
                            # region_adj_mat[cluster_id, labels[neighbor]] = 1
                            region_adj_mat[cluster_id-starting_index, labels[neighbor]-starting_index, 0] += 1

    for row in range(num_regions):
        for column in range(num_regions):
            # if region_adj_mat[row, column] == 1:
            if region_adj_mat[row, column, 0] != 0:
                region_adj_mat[row, column, 1] = abs(means_list[row] - means_list[column])
                # todo: take a look at formula (18) in Ji(2012) and see if changes are needed
    return region_adj_mat

def _salt_and_pepper(adj_mat, densities):
    # to reduce noises, this function acts like a median/salt_and_pepper image kernel and deletes zeros and high vals
    q95 = int(np.percentile(densities, 95))
    mask = np.logical_or(densities == 0, densities > q95)
    # mask = (densities == 0)
    for index in range(len(densities)):
        if mask[index] == 1:
            neighbors = np.argwhere(adj_mat[index] == 1)
            # x = densities[neighbors]
            median = np.median(densities[neighbors])
            densities[index] = max(median, 0.5)  # todo is 0.5 good?
    return densities


def _gaussian_smooth(adj_mat, densities):
    # to make densities more homogenous as gaussian filter does in image processing and smooths an image
    total_weights = np.sum(adj_mat, axis=1)
    total_weights = total_weights*2 + 4  # weight for each link = 4, weight for each neighbor = 2 # todo check new vals
    temp = np.sum(np.copy(adj_mat) * densities, axis=1)
    temp = temp*2 + 4*densities
    new_den = temp/total_weights
    # x = densities - new_den
    return new_den
