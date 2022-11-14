import numpy as np


class Graph:
    def __init__(self, adjacency_matrix, density_list):
        self.n = adjacency_matrix.shape[0]
        self.adjacency = adjacency_matrix
        self.densities = density_list
        self.distances, self.similarities = preprocess_network(self.adjacency, self.densities)
        self.labels = np.zeros(self.n)
        self.rag = np.zeros((1, 1))  # Region Adjacency Graph.

    def __len__(self):
        return self.n

    def set_labels(self, labels, calculate_rag=True):
        self.labels = labels
        if calculate_rag:
            self.rag = get_rag(labels, self.adjacency, self.densities)


def preprocess_network(adj_mat, densities):
    dist_mat = get_distance_matrix(adj_mat)
    W = get_similarity_matrix(dist_mat, densities)
    return dist_mat, W


def get_distance_matrix(adj_mat):
    n = adj_mat.shape[0]
    # A = np.copy(adj_mat)
    p = 1  # power of A
    A_p = np.copy(adj_mat)
    distance_mat = np.copy(adj_mat)
    X = np.ones((n, n)) - adj_mat - np.eye(n)
    # X(i,j) shows if we have detected the shortest path between i and j or not (if not, it's 1). X(i, i)s are 0 because
    # I assume that distance_mat(i,i)=0. # todo Is that true?
    # using algorithms like Dijkstra is time intensive
    while X.any():
        print(X)
        A_p = np.dot(A_p, adj_mat)
        p += 1
        new_walks = np.logical_and(X, A_p)
        X -= new_walks
        distance_mat += new_walks * p
    return distance_mat


def get_similarity_matrix(distance_matrix, density_list):
    n = distance_matrix.shape[0]
    W = np.zeros((n, n))
    # todo: how should be W[i,i]s (diagonal values)?
    # todo make the code below faster
    sigma = np.var(density_list)
    for row in range(n):
        for col in range(row, n):
            if distance_matrix[row, col] == 1:
                # todo: do we really have to use distance matrix? why not adjacency matrix?
                # the main formula is different than the one in paper. It doesn't conclude sigma
                similarity = np.exp(-(density_list[row] - density_list[col]) ** 2 / sigma)
                W[row, col] = similarity
                W[col, row] = similarity
    return W


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
        # n = labels.count(cluster_id)
        n = np.sum(labels == cluster_id)
        mask = (labels == cluster_id)
        means_list.append(sum(densities[mask]) / n)
        # for i in mask:
        for i in range(len(mask)):
            if mask[i] == 1:
                # neighbors = adj_mat[i]
                neighbors = np.argwhere(adj_mat[i] == 1).flatten()
                for neighbor in neighbors:
                    if labels[neighbor] != cluster_id:
                        region_adj_mat[cluster_id, labels[neighbor]] = 1

    for row in range(num_regions):
        for column in range(num_regions):
            if region_adj_mat[row, column] == 1:
                region_adj_mat[row, column] = abs(means_list[row] - means_list[column])
                # todo: take a look at formula (18) in Ji(2012) and see if changes are needed

    return region_adj_mat
