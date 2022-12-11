import numpy as np
from Graph import Graph
from logic import var_metrics, merging, initial_segmentation, boundary_adjustment
import io_handler as io
import logic_handler as logic

input_addresses = "config.yaml"
ncut_times = 6
merge_times = 5
net, edges, densities, adj_mat = io.get_network(input_addresses)
graph = Graph(adj_mat, densities)

#####
# running NCut
####
for i in range(ncut_times-1):
    initial_segmentation.get_segments(graph)
    print(np.unique(graph.labels))
    print('members of the new segment:', sum(graph.labels == i+1))
    print(np.argwhere(graph.labels == i+1).flatten())  # what are the new segment's members?
    # io.show_network(net, edges, graph.labels, colormap="tab10", save_adr=f'output/ncut4/ncut4-{i+2}.jpg')
    io.show_network(net, edges, graph.labels, colormap="tab10")
    print(var_metrics.average_NS(graph))
    print('')

#####
# finding MFDs
# todo @Parnati
####
segment_ids = logic.get_segment_IDs(graph, list(edges))
print(segment_ids)

#####
# running Merging
####
for i in range(merge_times-1):
    merging.merge(graph)
    print(np.unique(graph.labels))  # Do we have right number of segments?
    # io.show_network(net, edges, graph.labels, colormap="tab10",
    #                 save_adr=f'output/ncut4/merge-{max_number_of_clusters-i-1}.jpg')
    io.show_network(net, edges, graph.labels, colormap="tab10")
    print(var_metrics.average_NS(graph))

#####
# below is for helping detect marginal edges,
# useless while doing NCut
####
# edges_tmp = list(edges)
# for i in range(ncut_times - 1):
#     members_id = np.argwhere(graph.labels == i+1)
#     with open("./output/seattle_cut1.txt", 'a') as f:
#         for k in range(len(members_id)):
#             f.write('{}\t{}\n'.format(str(i+1), edges_tmp[members_id[k][0]]))



# # [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12]
# adj = np.array([[0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
#                 [1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
#                 [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
#                 [1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0],
#                 [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
#                 [0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0],
#                 [0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0],
#                 [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
#                 [0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1],
#                 [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
#                 [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1],
#                 [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0]])
#
# # [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12]
# # den = np.array([35,35,50,50,50,50,50,10,10,10,10,10])  # this is fine
# den = np.array([60, 60, 50, 50, 50, 50, 50, 10, 10, 10, 10, 10])  # this is NOT fine
#
# g = Graph(adj, den)
# initial_segmentation.get_segments(g)
# initial_segmentation.get_segments(g)
# # labels = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
# # g.set_labels(labels)
# merging.merge(g)
# merging.merge(g)
#
# print(var_metrics.segment_mean(g, 0))
# print(var_metrics.segment_var(g, 0))
# print(var_metrics.segment_var(g, 1))
# print(var_metrics.segment_mean(g, 1))
# print(len(g))
# # [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17]
# adj = np.array([[0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                 [1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                 [0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                 [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
#                 [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
#                 [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0],
#                 [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
#                 [0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
#                 [0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0],
#                 [0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
#                 [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
#                 [0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0],
#                 [0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1],
#                 [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
#                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0],
#                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1],
#                 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0]])
#
# # [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17]
# den = np.array([50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 10, 10, 10, 10, 10, 10, 10])
# g = Graph(adj, den)
# print(len(g))
