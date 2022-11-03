import io_handler as io
import logic_handler as logic

input_addresses = []
max_number_of_clusters = 10

densities, adj_mat = io.get_network(input_addresses)
dist_mat, W = logic.preprocess_network(adj_mat, densities)
#todo: you can make the class 'network' but I don't know if that's helpful!

for i in range(max_number_of_clusters):
    segment_IDs, SN, TV = logic.make_partitions(densities, adj_mat, dist_mat, W)
    print(f'for {i} clusters: SN={SN},  TV={TV}')
    io.show_network(segment_IDs)

