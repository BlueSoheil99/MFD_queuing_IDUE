import numpy as np
from Graph import Graph
from logic import var_metrics, merging, initial_segmentation, boundary_adjustment
import io_handler as io
import logic_handler as logic
import matplotlib.pyplot as plt
import random
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import sumolib


def print_metrics(graph):
    labels = np.unique(graph.labels)
    print('mean densities:', str([round(var_metrics.segment_mean(graph, i), 3) for i in labels]))
    print('mean variance:', str([round(var_metrics.segment_var(graph, i), 3) for i in labels]))
    print('NSs:', str([round(var_metrics.NS(graph, i), 4) for i in labels]))
    print('average NS:', str(round(var_metrics.average_NS(graph), 4)))
    print('TV:', str(round(var_metrics.TV(graph))))
    print('')


def show_density_hist(density_list, title='density after deleting marginal links (6-8)'):
    Min = int(min(density_list))
    Max = int(max(density_list))
    q75 = int(np.percentile(density_list, 75))
    q90 = int(np.percentile(density_list, 90))
    print(f'density distribution: min: {Min}, q75: {q75}, q90: {q90}, max: {Max}')
    range1 = range(Min, q75, int((q75-Min)/20))
    range2 = range(q75, q90, int((q90-q75)/10))[1:]
    range3 = range(q90, Max, int((Max-q90)/10))[1:]
    Range = [*range1, *range2, *range3]
    print('bins:'+ str(Range))
    # plt.hist(density_list, bins=int((max(density_list) - min(density_list)) / 10))
    # plt.hist(density_list, bins=Range)
    # plt.xticks(Range)
    fig, ax = plt.subplots()
    # ax.axvspan(q75, q90, color='grey')
    # ax.hist(density_list, bins=int((max(density_list) - min(density_list)) / 10))
    y, x, _ = ax.hist(density_list, edgecolor='white', bins=Range)
    ax.set_xscale("log", nonpositive='clip')
    for value in [(q75, '75%'), (q90, '90%')]:
        ax.axvline(x=value[0], color='red', linestyle="--")
        ax.text(value[0], 0.9*y.max(), value[1])

    plt.title(title+f'\nmin: {Min}, q75: {q75}, q90: {q90}, max: {Max}')
    plt.show()


input_addresses = "config.yaml"
ncut_times =5
merge_times =3
net, edges, densities, adj_mat = io.get_network(input_addresses)
# densities[:] = np.random.normal(10, 5)
# for i in range(len(densities)):
#     densities[i] = np.random.normal(10, 5)

# show_density_hist(densities)
# io.show_network(net, edges, densities, colormap_name="binary")  # density map
graph = Graph(adj_mat, densities)

#####
# running NCut
####
print('\n## INITIAL PARTITIONING\nTV for 1 big segment:', str(round(var_metrics.TV(graph))), '\n', 'mean density:', str(round(var_metrics.segment_mean(graph, 0), 2)), '\n')
for i in range(ncut_times-1):
    initial_segmentation.get_segments(graph)
    print(np.unique(graph.labels))
    print('members of the new segment:', sum(graph.labels == i+1))
    # print(np.argwhere(graph.labels == i+1).flatten())  # what are the new segment's members?
    # io.show_network(net, edges, graph.labels, colormap="tab10", save_adr=f'output/ncut4/ncut4-{i+2}.jpg')
    io.show_network(net, edges, graph.labels, colormap_name="tab10")
    print_metrics(graph)
io.show_network(net, edges, graph.labels, colormap_name="tab10")


#####
# running Merging
####
print('## MERGING')
for i in range(merge_times-1):
    merging.merge(graph)
    print(np.unique(graph.labels))  # Do we have right number of segments?
    # io.show_network(net, edges, graph.labels, colormap="tab10",
    #                 save_adr=f'output/ncut4/merge-{max_number_of_clusters-i-1}.jpg')
    io.show_network(net, edges, graph.labels, colormap_name="tab10")
    print_metrics(graph)


#####
# below is for helping detect marginal edges,
# useless while doing NCut
####
# edges_tmp = list(edges)
# for i in range(ncut_times - 1):
#     members_id = np.argwhere(graph.labels == i+1)
#     with open("./output/seattle_cut1.txt", 'a') as f:
#         for k in range(len(members_id)):
#             f.write('{}\t{}\n'.format(str(i+1), edges_tmp[members_id[k][0]]))




#####
# finding MFDs
# todo @Parnati
###code from Pranati begin here -- including all as could not read from other file###########
# Parse the XML file
tree = ET.parse('Data/Edgetest_6_0411_2_0.xml')
root = tree.getroot()
net = sumolib.net.readNet('Data/Seattle_road_network_edit_1.net.xml')


# function to retrieve length for edges (input in function) from network file
# def getlength(edge_net):
#     edges = net.getEdges()
#     for edge_net in edges:
#         length = edge_net.getLength()
#     return length


# function to get list of edge id from network input file for all of network with density and removing those without density
def getedgeids(root):
    # initialize a dictionary to store edge ids
    edgeid = {}

    # iterate through all edges in the file
    for edge in root.iter("edge"):
        # extract the edge ID and length
        edge_id = edge.attrib["id"]
        # condition check if density exists
        # add the edge id to the dictionary
        edgeid[edge_id] = edge_id
    return edgeid


def plot_mfd(edge_id, start_time, end_time):
    # Select the edge of interest
    # edge_id = ['-171739214#4', '-105493444#4']
    #### enter here the list of selected edges for each region ## have to ask Soheil for list

    # Initialize empty lists to store density and speed data for the edge
    global density, speed, flow
    densities = []
    speeds = []
    flows = []


    ##check number of edges less than 0 for speed alone...plot network .. to see if connected-- connectivity chevk function
    ### list of edges sith speed less than 0 or 0


    # Iterate through the timestep elements
    # for interval in edge_stats:
    #     if interval_begin * 3600 <= float(interval.begin) < interval_end * 3600:
    # for interval in root:
    #     # Find the edge element for the selected edge

    for interval in root.findall('interval'):
        begin = float(interval.get('begin'))
        end = float(interval.get('end'))

        if begin >=start_time and end <= end_time:
            for edge in edge_id:
                edge_elem = interval.find(".//edge[@id='" + edge + "']")
                # edge_elem = edge
                if edge_elem is not None:
                    # length = getlength(edge_elem)
                    # Extract the density and speed data for the edge
                    speed_raw = edge_elem.get('speed')
                    density_raw = edge_elem.get('laneDensity')
                    #begin and end time --  num of veh---- # check with Yiran calculate flow
                    #send Yiran the edges with higher flow and then higher flow and higher density
                    #no of vehicles

                    if density_raw is not None and float(density_raw) > 0 and speed_raw is not None and float(
                            speed_raw) > 0:
                        density = float(density_raw)
                        speed = float(speed_raw)
                        flow = float(density * speed * 3.6)  # not sure if we need to multiply length as well (length*0.001)
                        if float(flow) > 1000:
                            print(f"{edge} have flow {flow}")
                # if flow >4000:
                #     print(f"{edge} have flow {flow} ")
                # else:
                #     #     if density_raw is None or float(density_raw) <= 0:
                #     #         print(f"Invalid density value {density_raw} for edge {edge_id}")
                #     # if speed_raw is None or float(speed_raw) <= 0:
                #     #     print(f"Invalid speed value {speed_raw} for edge {edge}")
                #     if density_raw is not None and float(density_raw) > 750:
                #         print(f"{edge_elem} have density {density_raw}")

                # Append the density and speed data to the appropriate lists
                        densities.append(density)
                        speeds.append(speed)
                        flows.append(flow)
                if edge_elem is None:
                    print(f"edge {edge} does not exist in the edgetest file")

        ##speed as m/sec

    # Plot the MFD
    plt.scatter(densities, flows, s=8, c='b', alpha=0.5)
    plt.xlabel('Density')
    plt.ylabel('Flow')
    plt.title("Macroscopic Fundamental Diagram")

    plt.show()

# from MFD.Plot_MFD import plot_mfd
segment_ids = logic.get_segment_IDs(graph, list(edges))
for i in range(len(segment_ids)):
    edge_list = segment_ids[i]
    print(f"plot for the edges in {i} group ")
    start_time = 28800
    end_time = 32400
    print(edge_list)
    plot_mfd(edge_list, start_time, end_time)
    # plot_mfd(edge_list)
#### code from Pranati ends here###############
