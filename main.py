import io_handler as io
import logic_handler as logic
from Graph import Graph

input_addresses = "config.yaml"
max_number_of_clusters = 10

net, edges, densities, adj_mat = io.get_network(input_addresses)
graph = Graph(adj_mat, densities)


segments_and_metrics = logic.make_partitions(graph, max_number_of_clusters)
for i in range(max_number_of_clusters):
    print(f'for {i} segments: SN={segments_and_metrics[i][1]},  TV={segments_and_metrics[i][2]}')
    io.show_network(net, edges, segments_and_metrics[i][0])

