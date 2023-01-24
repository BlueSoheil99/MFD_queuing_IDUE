import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from inout import plot_network as pln
from inout import utility as util
from inout import plot_network as vis
import pandas as pd  # for debugging

matplotlib.use("Qt5Agg")


def get_network(input_addresses="config.yaml"):
    net_fname, info_fname, option, net_edges_fname, interval_begin, interval_end, edges_to_remove = \
        util.init_config(input_addresses)
    # read network
    net, edges = util.read_network(net_fname, net_edges_fname, edges_to_remove)
    # organize the network info into dictionaries
    edge_diction = util.read_edge_info(edges, info_fname, option, interval_begin, interval_end)
    print(edge_diction)

    adjacency_matrix = util.make_adjacency(net, edge_diction)
    data = pd.DataFrame(adjacency_matrix)  # debug
    data.to_csv('data/adjacency_matrix.csv', index=False)  # debug
    # todo use the lines above for the first run, then use the line below for next runs
    # adjacency_matrix = read_adj('data/adjacency_matrix.csv')  # debug

    list_of_edges = edge_diction.keys()
    list_of_densities = np.array(list(edge_diction.values()))
    return net, list_of_edges, list_of_densities, adjacency_matrix


def read_adj(address):  # DEBUG
    import pandas as pd
    data = pd.read_csv(address)
    return data.to_numpy()


def show_network(net, edges_list, region_id, width_edge=2, alpha=0.5, mapscale=4.0, colormap_name="tab10",
                 save_adr=None):
    fig, ax = pln.init_plot()

    vmin = min(region_id)
    vmax = max(region_id)

    if colormap_name == "tab10":
        colormap = vis.init_colors(colormap_name, vmin, vmax)
    else:
        colormap = vis.init_colors(colormap_name, vmin, vmax, normalized=True)

    edges_list = list(edges_list)

    for edge in net.getEdges():
        raw_id = edge.getID()
        new_id = util.cleanID(raw_id)

        if new_id in edges_list:
            shape = net.getEdge(raw_id).getShape()
            x_vec = np.array(shape)[:, 0]
            y_vec = np.array(shape)[:, 1]
            idx = edges_list.index(new_id)
            if colormap_name == "tab10":
                ax.plot(x_vec * mapscale, y_vec * mapscale, color=colormap.colors[region_id[idx]],
                        lw=width_edge, alpha=alpha, zorder=-100)
            else:
                ax.plot(x_vec * mapscale, y_vec * mapscale, color=vis.get_color(colormap, region_id[idx]),
                        lw=width_edge, alpha=alpha, zorder=-100)
        else:
            shape = net.getEdge(raw_id).getShape()
            x_vec = np.array(shape)[:, 0]
            y_vec = np.array(shape)[:, 1]
            ax.plot(x_vec * mapscale, y_vec * mapscale, color="white", lw=width_edge, alpha=0.2, zorder=-100)
            # ax.plot(x_vec * mapscale, y_vec * mapscale, color="gray", lw=width_edge, alpha=0.2, zorder=-100)

    plt.xlabel("x coord")
    plt.ylabel("y coord")
    if colormap_name == "tab10":
        plt.text(0.0, 1.05, "Region: ", horizontalalignment='center',
                 verticalalignment='center', transform=ax.transAxes,
                 bbox=dict(facecolor="black", alpha=0.5))
        for i in range(vmin, vmax + 1):
            plt.text(0.1 * i + 0.2, 1.05, str(i), horizontalalignment='center',
                     verticalalignment='center', transform=ax.transAxes,
                     bbox=dict(facecolor=colormap.colors[i], alpha=0.5))
    plt.show()
    if save_adr is not None:
        plt.savefig(save_adr)
