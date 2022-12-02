import inout.checking as io_check

from inout import utility as util

input_addresses = "config.yaml"
out_folder = "./output/"
out_name = "seattle"

net_fname, info_fname, option, net_edges_fname, interval_begin, interval_end, edges_to_remove = util.init_config(input_addresses)

# check the connectivity of the network, and based on checking output in /output/,
# choose a set of the connected subnetworks with the most links
io_check.connectivity(input_addresses, out_folder=out_folder, out_name=out_name)

net, edges = util.read_network(net_fname, net_edges_fname, edges_to_remove)
io_check.redundant_edges(edges, info_fname, option)



