import numpy as np
from Graph import Graph
from logic import var_metrics, merging, initial_segmentation, boundary_adjustment
import io_handler as io


input_addresses = "config.yaml"
max_number_of_clusters = 10
net, edges, densities, adj_mat = io.get_network(input_addresses)
graph = Graph(adj_mat, densities)
for i in range(max_number_of_clusters-1):
    initial_segmentation.get_segments(graph)
    print(np.unique(graph.labels))  # Do we have right number of segments?
    print('members of the new segment:', sum(graph.labels == i+1))
    print(np.argwhere(graph.labels == i+1))  # what are the new segment's members?
    io.show_network(net, edges, graph.labels, colormap="tab10")

# segments_and_metrics = logic.make_partitions(graph, max_number_of_clusters)
# for i in range(max_number_of_clusters):
#     print(f'for {i} segments: SN={segments_and_metrics[i][1]},  TV={segments_and_metrics[i][2]}')
#     io.show_network(net, edges, segments_and_metrics[i][0])


              # [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12]
adj = np.array([[0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                [1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
                [0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0],
                [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1],
                [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0]])

              # [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12]
# den = np.array([35,35,50,50,50,50,50,10,10,10,10,10])  # this is fine
den = np.array([60,60,50,50,50,50,50,10,10,10,10,10])  # this is NOT fine

g = Graph(adj, den)
initial_segmentation.get_segments(g)
initial_segmentation.get_segments(g)
# labels = np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
# g.set_labels(labels)
merging.merge(g)
merging.merge(g)

print(var_metrics.segment_mean(g, 0))
print(var_metrics.segment_var(g, 0))
print(var_metrics.segment_var(g, 1))
print(var_metrics.segment_mean(g, 1))
print(len(g))
              # [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17]
adj = np.array([[0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                [1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                [0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0],
                [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0],
                [0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1],
                [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0]])

             # [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17]
den = np.array([50,50,50,50,50,50,50,50,50,50,10,10,10,10,10,10,10])
g = Graph(adj, den)
print(len(g))
