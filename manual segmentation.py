import os
import numpy as np
from Graph import Graph
from logic import var_metrics, merging, initial_segmentation
import io_handler as io
import logic_handler as logic
# from MFD import updated_final_mfd
from MFD import Plot_MFD as MFD


def files_to_dict(dir_path):
    if not os.path.exists(dir_path):
        raise ValueError(f"Directory {dir_path} does not exist.")

    result = {}
    i = 0
    for filename in os.listdir(dir_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'r') as f:
                values = f.read().splitlines()
            result[i] = values
            i += 1

    return result


path_to_file = 'Data/manual detected edges in regions'

segment_ids = files_to_dict(path_to_file)

# function to plot manual segmentimport os

import os
import random
import sumolib
import matplotlib.pyplot as plt
from inout import utility as util
import io_handler as io

input_addresses = "config.yaml"
net, edges, densities, adj_mat, start_time, end_time = io.get_network(input_addresses)
graph = Graph(adj_mat, densities)
print(graph.labels)


def visualize_edges_with_key(net, segment_ids):
    # Create a dictionary that maps edge IDs to their corresponding segment IDs
    edge_segment_ids = {}
    for segment_id, segment_edges in segment_ids.items():
        for edge_id in segment_edges:
            edge_segment_ids[edge_id] = segment_id


    # Assign labels to each edge in the graph based on the segment IDs
    num_edges = len(net.getEdges())
    labels = [0] * num_edges
    for i, edge in enumerate(net.getEdges()):
        edge_id = edge.getID()
        if edge_id in edge_segment_ids:
            segment_id = edge_segment_ids[edge_id]
            labels[i] = segment_id
    return labels



    # # Color edges by segment ID
    # node_colors = {}
    # edge_colors = []
    # segment_colors = {}
    # for edge in net.getEdges():
    #     if edge.getID() in edge_segment_ids:
    #         segment_id = edge_segment_ids[edge.getID()]
    #         if segment_id not in segment_colors:
    #             segment_colors[segment_id] = '#' + ''.join(random.choices('0123456789abcdef', k=6))
    #         edge_color = segment_colors[segment_id]
    #         edge_colors.append(edge_color)
    #         node_colors[edge.getFromNode().getID()] = edge_color
    #         node_colors[edge.getToNode().getID()] = edge_color
    #
    #         # Get the shape of the edge
    #         shape = edge.getShape()
    #         x_vec = [pos[0] for pos in shape]
    #         y_vec = [pos[1] for pos in shape]
    #         plt.plot(x_vec, y_vec, color=edge_color)

    # Draw the nodes
    # for node in net.getNodes():
    #     node_id = node.getID()
    #     if node_id in node_colors:
    #         plt.plot(node.getCoord()[0], node.getCoord()[1], 'o', color=node_colors[node_id])

    # plt.axis('off')
    # plt.show()


net_file = 'Data/Seattle_road_network.net.xml'
graph.labels = visualize_edges_with_key(net, segment_ids)
print(segment_ids)
# visualize_edges_with_key(net,segment_ids)
io.show_network(net, edges, graph.labels)

start_time = 18000.00
end_time = 36000.00
MFD.plot_mfd(segment_ids, start_time, end_time)
print(segment_ids)
