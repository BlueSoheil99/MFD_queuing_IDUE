from logic import initial_segmentation, merging, boundary_adjustment, var_metrics, shape_metrics


# def initial_segmentation(similarity_mat):
#     return initial_segmentation.get_segments(similarity_mat)


# def merging(graph):
#     have an input to show how clusters are neighbor
    # merging.merge(graph)


def boundary_adjustment():
    return boundary_adjustment


def get_NS(graph):
    return var_metrics.NS(graph)


def get_TV(graph):
    return var_metrics.TV(graph)
