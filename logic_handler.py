import logic
from logic import *
import numpy as np



# def get_distance_matrix(adj_mat):
#     n = adj_mat.shape[0]
#     A = np.copy(adj_mat)
#     p = 1  # power of A
#     A_p = np.copy(A)
#     distance_mat = np.copy(adj_mat)
#     X = np.ones((n, n)) - adj_mat - np.eye(n)
#     # X(i,j) shows if we have detected the shortest path between i and j or not (if not, it's 1). X(i, i)s are 0 because
#     # I assume that distance_mat(i,i)=0. # todo Is that true?
#     # using algorithms like Dijkstra is time intensive
#     while X.any():
#         print(X)
#         A_p = np.dot(A_p, A)
#         p += 1
#         new_walks = np.logical_and(X, A_p)
#         X -= new_walks
#         distance_mat += new_walks * p
#     return distance_mat
#
#
# def get_similarity_matrix(distance_matrix, density_list):
#     n = distance_matrix.shape[0]
#     W = np.zeros((n, n))
#     #todo: how should be W[i,i]s (diagonal values)?
#     #todo make the code below faster
#     for row in W:
#         for col in row:
#             if distance_matrix[row, col] == 1:
#                 W[row, col] = np.exp(-(density_list[row] - density_list[col])**2)
#     return W
#
#
# def preprocess_network(adj_mat, densities):
#     dist_mat = get_distance_matrix(adj_mat)
#     W = get_similarity_matrix(dist_mat, densities)
#     return dist_mat, W
#
#
# def get_segments(densities, adj_mat, dist_mat, W):
#     #todo
#     seg_list = logic.initial_segmentation(W)
#     seg_list = logic.merging(seg_list, adj_mat, densities)
#     seg_list = logic.boundary_adjustment(seg_list)
#     return seg_list
#
#
# def get_metrics(densities, adj_mat, dist_mat, W):
#     #todo
#     return NS, TV


# def make_partitions(densities, adj_mat, dist_mat, W):
#     segments_assigned = get_segments(densities, adj_mat, dist_mat, W)
#     NS, TV = get_metrics(densities, adj_mat, dist_mat, W)
#     return segments_assigned, NS, TV


def get_segments(graph):
    initial_segmentation.get_segments(graph)
    merging.merge(graph)
    logic.boundary_adjustment(graph)
    return graph.labels


def get_metrics(graph):
    NS = logic.get_NS(graph)
    TV = logic.get_TV(graph)
    return NS, TV

def make_partitions(graph):
    segments_assigned = get_segments(graph)
    NS, TV = get_metrics(graph)
    return segments_assigned, NS, TV
