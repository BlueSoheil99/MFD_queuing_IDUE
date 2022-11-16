
#Hey Pranati!

# I suggest that you make a new directory (name can be inout) and make other .py files related to this file.
# Also you can have a .txt file in that folder to save the address of input files. You can hardcode the addresses or
# input file names for now but we'll have to make it cleaner later
import numpy as np
import matplotlib.pyplot as plt

from inout import utility as util
from inout import plot_network as vis


def get_network(input_addresses="config.yaml"):
    net_fname, info_fname, option = util.init_config(input_addresses)
    # read network
    net, nodes, edges = util.read_network(net_fname)
    # organize the network info into dictionaries
    node_diction = util.read_node_info(nodes)
    edge_diction = util.read_edge_info(edges, info_fname, option)
    # convert the network into adjacency matrix and density list
    # now I aggregate densities of whole day
    # TODO: revise the code if we need a specific time frame of density info
    adjacency_matrix = util.make_adjacency(net, node_diction, edge_diction)
    list_of_edges = edge_diction.keys()
    list_of_densities = edge_diction.values()
    return net, list_of_edges, list_of_densities, adjacency_matrix
    # return matrix with numpy array. That should be more efficient


def show_network(net, edges_list, region_id, width_edge=2, alpha=0.5, mapscale=1.0, colormap="tab10"):
    fig, ax = plt.init_plot()

    vmin = min(region_id)
    vmax = max(region_id)

    colormap = vis.init_colors(colormap, vmin, vmax)

    for key, value in zip(edges_list, region_id):
        shape = net.getEdge(key).getShape()
        x_vec = np.array(shape)[:, 0]
        y_vec = np.array(shape)[:, 1]
        ax.plot(x_vec * mapscale, y_vec * mapscale, color=vis.get_color(colormap, value, "partition"),
                lw=width_edge, alpha=alpha, zorder=-100)

    plt.xlabel("x coord")
    plt.ylabel("y coord")
    plt.show()

    # plot the network with each segment defined with a color
    # the input is list with len=|V| each element shows the seg# for each link
    # ex: we have 4 segments, the list would be like: [1, 1, 1, 2, 2, 3, 4, 4, 3, 1 ,...]

