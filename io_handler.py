import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import mplcursors
from inout import plot_network as pln
from inout import utility as util
from inout import plot_network as vis
import pandas as pd  # for debugging


# matplotlib.use("Qt5Agg")


def get_network(input_addresses="config files/config.yaml"):
    net_fname, info_fname, option, net_edges_fname, interval_begin, interval_end, \
    edges_to_remove, minor_edges, predetermined_regions_folder = util.init_config(input_addresses)
    # read network
    net, edges, predetermined_regions_dict = util.read_network(net_fname, net_edges_fname,
                                                               edges_to_remove, minor_edges, predetermined_regions_folder)
    # organize the network info into dictionaries
    edge_diction = util.read_edge_info(edges, info_fname, option, interval_begin, interval_end)
    print(edge_diction)

    adjacency_matrix = util.make_adjacency(net, edge_diction)

    array_of_edges = np.array(list(edge_diction.keys()))
    array_of_densities = np.array(list(edge_diction.values()))
    array_of_labels = (np.ones(len(array_of_edges))*len(predetermined_regions_dict)).astype(int)
    # if we fix n regions, number of all regions would be n+1.
    # Previously, the initial region was labeled 0, but now, we start the segmentation from region with label = n
    for item in predetermined_regions_dict.items():
        seg_id = int(item[0])
        seg_edge_IDs = item[1]

        # indices = np.searchsorted(array_of_edges, seg_edge_IDs)
        # array_of_labels[indices] = seg_id
        for edge_id in seg_edge_IDs:
            index = np.argwhere(array_of_edges == edge_id)
            array_of_labels[index] = seg_id

    return net, array_of_edges, array_of_densities, adjacency_matrix, array_of_labels


# def show_network(net, edges_list, region_id, width_edge=2.5, alpha=0.15, mapscale=4.0, colormap_name="tab10",
def show_network(net, edges_list, region_id, width_edge=2, alpha=0.5, mapscale=4.0, colormap_name="tab10",
                 save_adr=None, title='', interactive_func=None, colorbar_range=None):
    fig, ax = pln.init_plot()

    if colorbar_range is None:
        vmin = min(region_id)
        vmax = max(region_id)
    else:
        vmin = colorbar_range[0]
        vmax = colorbar_range[1]

    if "tab" in colormap_name:
        if colormap_name =='tab10':
            if len(np.unique(region_id)) > 10:
                colormap_name = 'tab20'
            else:
                colormap_name = 'tab10'
        colormap = vis.init_colors(colormap_name, vmin, vmax)
    else:
        colormap = vis.init_colors(colormap_name, vmin, vmax, normalized=True)

    edges_list = list(edges_list)
    links=[]

    for edge in net.getEdges():
        raw_id = edge.getID()
        new_id = util.cleanID(raw_id)

        if new_id in edges_list:  # in this case, we will draw that edge
            shape = net.getEdge(raw_id).getShape()
            x_vec = np.array(shape)[:, 0]
            y_vec = np.array(shape)[:, 1]
            idx = edges_list.index(new_id)
            if "tab" in colormap_name:
                link, = ax.plot(x_vec * mapscale, y_vec * mapscale, color=colormap.colors[region_id[idx]],
                        lw=width_edge, alpha=alpha, zorder=-100, label=new_id)
            else:
                link, = ax.plot(x_vec * mapscale, y_vec * mapscale, color=vis.get_color(colormap, region_id[idx]),
                        lw=width_edge, alpha=alpha, zorder=-100, label=new_id)
            links.append(link)
        else:
            shape = net.getEdge(raw_id).getShape()
            x_vec = np.array(shape)[:, 0]
            y_vec = np.array(shape)[:, 1]
            # ax.plot(x_vec * mapscale, y_vec * mapscale, color="white", lw=width_edge, alpha=0.2, zorder=-100)
            # ax.plot(x_vec * mapscale, y_vec * mapscale, color="magenta", lw=width_edge, alpha=0.2, zorder=-100)

    plt.xlabel("x coord")
    plt.ylabel("y coord")
    if "tab" in colormap_name:
        h_layers = math.ceil(len(range(vmin, vmax + 1)) / 10)
        plt.text(0.0, 1.03 + 0.1 * h_layers, "Region: ", horizontalalignment='center',
                 verticalalignment='center', transform=ax.transAxes,
                 bbox=dict(facecolor="none", alpha=0.5))
        for i in range(vmin, vmax + 1):
            if i < 10:
                plt.text(0.1 * i + 0.2, 1.03 + 0.1 * h_layers, str(i), horizontalalignment='center',
                         verticalalignment='center', transform=ax.transAxes,
                         bbox=dict(facecolor=colormap.colors[i], alpha=0.5))
            else:
                plt.text(0.1 * (i - 10) + 0.2, 1.03 + 0.1 * (h_layers - 1), str(i), horizontalalignment='center',
                         verticalalignment='center', transform=ax.transAxes,
                         bbox=dict(facecolor=colormap.colors[i], alpha=0.5))

    if colorbar_range is not None:
        divider = make_axes_locatable(ax)
        cax = divider.append_axes("bottom", size="5%", pad='20%')
        fig.colorbar(colormap, cax=cax, orientation="horizontal")
        # fig.colorbar(colormap, cax=cax)
        cax.xaxis.set_ticks_position("bottom")
    else:
        plt.axis('off')

    plt.tight_layout()
    plt.title(title)
    # plt.axis('off')

    if interactive_func is not None:
        print('interactive map ON')
        # # mplcursors.cursor(links)
        # mplcursors.cursor().connect(
        #     "add", lambda sel: sel.annotation.set_text(sel.artist.get_label()))
        cursor = mplcursors.cursor(links)
        @cursor.connect("add")
        def _(sel):
            label = sel.artist.get_label()
            sel.annotation.set_text(label)
            interactive_func(label)
            # txt = interactive_func(label)
            # print(txt)

    if save_adr is None:
        plt.show()
    else:
        plt.savefig(save_adr, dpi=400)
