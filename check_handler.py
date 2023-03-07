import inout.checking as io_check

from inout import utility as util

input_addresses = "config.yaml"
out_folder = "./output/"
out_name = "seattle"

# net_fname, info_fname, option, net_edges_fname, interval_begin, interval_end, edges_to_remove, \
#     minor_links, highways_tunnels = util.init_config(input_addresses)
# #
# # # check the connectivity of the network, and based on checking output in /output/,
# # # choose a set of the connected subnetworks with the most links
# io_check.connectivity(input_addresses, out_folder=out_folder, out_name=out_name)
#
# net, edges = util.read_network(net_fname, net_edges_fname, edges_to_remove, minor_links, highways_tunnels)
# io_check.zero_density_edges(edges, info_fname, option)

#####
# !!!NOTE!!! Uncomment the following if we want to
# detect marginal links based on NCut results.
# =================================================
# After running 30 times of NCut,
# we try to remove marginal links.
# =================================================
# Because the following won't be used anywhere else,
# I didn't create any functions in utility.py
#####
cut_result_name = out_folder + "seattle_cut1.txt"
io_check.detect_marginal_edges(cut_result_name)



