import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
import pickle

address = "Data/uniques_interval_data.pickle"

# codes for creating .pickle files are transferred into pickle_creator.py


def plot_mfd(group_dict, start_time, end_time, data_adr=address, separated=False, normalized=True):
    with open(data_adr, "rb") as f:
        edge_stats = pickle.load(f)
        f.close()

    if separated:
        r = (len(group_dict.keys())+1) // 2
        if normalized:
            fig = plt.figure()
            gs = fig.add_gridspec(r, 2, hspace=0, wspace=0)
            axs = gs.subplots(sharex=True, sharey=True)
        else:
            fig, axs = plt.subplots(r, 2)
        fig.suptitle('Separated MFD plots')
    else:
        fig, ax = plt.subplots()

    # Define markers and colors for each group
    markers = ["o", "s", "^", "D", "P", "X"]
    sizes = [8, 8, 8, 8, 8, 8]
    colors = ["blue", "orange", "green", "red", "purple", "brown", "pink", "gray", "olive", "cyan"]

    for i, (group_id, edge_list) in enumerate(group_dict.items()):
        tnvehs_group = []
        tvkpm_group = []
        for interval_id, edges_data in edge_stats.items():
            if float(interval_id) <= start_time or float(interval_id) > end_time:
                continue
            total_nvehs = 0
            total_vkpm = 0
            for edge_id in edge_list:
                if edge_id in edges_data:
                    edge_data = edges_data[edge_id]
                    speed = edge_data["speed"]
                    sampled_seconds = edge_data["sampledSeconds"]
                    if speed is not None and float(speed) > 0:
                        total_nvehs += float(sampled_seconds) / 60
                        total_vkpm += float(speed) * float(sampled_seconds) / 1000
            tnvehs_group.append(total_nvehs)
            tvkpm_group.append(total_vkpm)

        # Use different marker and size for each group
        marker = markers[i % len(markers)]
        size = sizes[i % len(sizes)]
        color = colors[i % len(colors)]
        if separated:
            ax = axs[i//2, i % 2]
        ax.scatter(tnvehs_group, tvkpm_group, label=f"Region {group_id}", marker=marker, s=size, c=color)

    if separated:
        _modify_appearance(axs, separated, normalized)
    else:
        _modify_appearance(ax, separated, normalized)
    plt.show()


def _modify_appearance(axs, separated, normalized):
    if separated:
        for ax in axs.flat:
            ax.legend()
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)
            ax.set(xlabel='Total Number of Vehicles', ylabel='total veh-km/min')
            if normalized:
                ax.label_outer()
    else:
        ax = axs
        # Set x and y axis label font size and weight
        ax.set_xlabel("Total Number of Vehicles", fontsize=14, fontweight="bold")
        ax.set_ylabel("Total Vehicle Kilometers per Minute", fontsize=14, fontweight="bold")
        # Set x and y axis tick font size and weight
        ax.tick_params(axis="x", labelsize=12, which="both", direction="in", bottom=True, top=True, left=True,
                       right=True)
        ax.tick_params(axis="y", labelsize=12, which="both", direction="in", bottom=True, top=True, left=True,
                       right=True)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        ax.legend()