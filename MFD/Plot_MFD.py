import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
import pickle


# uncomment these when need to create another list of dictionary with data

#
# def edge_return_dict():
#     tree = ET.parse('../edge_data_output._1min_interval.xml')
#     root = tree.getroot()
#
#     unique_intervals = {}
#
#     for interval in root.findall('./interval'):
#         interval_id = interval.get("begin")
#         unique_edges = {}
#
#         for edge in interval.iter("edge"):
#             edge_id = edge.get("id")
#
#             if edge_id in unique_edges:
#                 unique_edges[edge_id] = {
#                     "sampledSeconds": edge.get("sampledSeconds"),
#                     "laneDensity": edge.get("laneDensity"),
#                     "speed": edge.get("speed")
#                 }
#             else:
#                 unique_edges[edge_id] = {
#                     "sampledSeconds": edge.get("sampledSeconds"),
#                     "laneDensity": edge.get("laneDensity"),
#                     "speed": edge.get("speed")
#                 }
#
#         unique_intervals[interval_id] = unique_edges
#
#     return unique_intervals


#
# #
# #
# # ##saving above created dictionary
# # Dictionary to be stored
# uniq_intervals = edge_return_dict()
# print(uniq_intervals)
#
# # Write dictionary to file
# with open("../uniques_interval_data.pickle", "wb") as f:
#     pickle.dump(uniq_intervals, f)


def plot_mfd(group_dict, start_time, end_time):
    with open("Data/uniques_interval_data.pickle", "rb") as f:
        edge_stats = pickle.load(f)

    fig, ax = plt.subplots()

    # Define markers and colors for each group
    markers = ["o", "s", "^", "D", "P", "X"]
    sizes = [8, 8, 8, 8, 8, 8]
    colors = ["blue", "orange", "green", "purple", "brown", "pink", "gray", "olive", "cyan"]

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

        ax.scatter(tnvehs_group, tvkpm_group, label=f"Region {group_id}", marker=marker, s=size, c=color)

    # Set x and y axis label font size and weight
    ax.set_xlabel("Total Number of Vehicles", fontsize=14, fontweight="bold")
    ax.set_ylabel("Total Vehicle Kilometers per Minute", fontsize=14, fontweight="bold")

    # Set x and y axis tick font size and weight
    ax.tick_params(axis="x", labelsize=12, which="both", direction="in", bottom=True, top=True, left=True, right=True)
    ax.tick_params(axis="y", labelsize=12, which="both", direction="in", bottom=True, top=True, left=True, right=True)

    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    ax.legend()
    plt.show()

