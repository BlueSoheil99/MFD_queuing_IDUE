import initial_segmentation, merging, boundary_adjustment


def initial_segmentation(similarity_mat):
    return initial_segmentation.get_segments(similarity_mat)


def merging(labels_list, adj_mat, densities):
    #have an input to show how clusters are neighbor
    return merging.merge(labels_list, adj_mat, densities)


def boundary_adjustment():
    return None