import numpy as np
from Graph import Graph
from logic import var_metrics, merging, initial_segmentation
import io_handler as io
import logic_handler as logic
# from MFD import updated_final_mfd
from MFD import Plot_MFD as MFD


def print_metrics(graph):
    labels = np.unique(graph.labels)
    print('mean densities:', str([round(var_metrics.segment_mean(graph, i), 3) for i in labels]))
    print('mean variance:', str([round(var_metrics.segment_var(graph, i), 3) for i in labels]))
    print('NSs:', str([round(var_metrics.NS(graph, i), 4) for i in labels]))
    print('average NS:', str(round(var_metrics.average_NS(graph), 4)))
    print('TV:', str(round(var_metrics.TV(graph))))
    print('')

#
# def show_density_hist(density_list, title='density after deleting marginal links ()'):
#     Min = int(min(density_list))
#     Max = int(max(density_list))
#     q75 = int(np.percentile(density_list, 75))
#     q90 = int(np.percentile(density_list, 90))
#     print(f'density distribution: min: {Min}, q75: {q75}, q90: {q90}, max: {Max}')
#     range1 = range(Min, q75, int((q75-Min)/20))
#     range2 = range(q75, q90, int((q90-q75)/10))[1:]
#     range3 = range(q90, Max, int((Max-q90)/10))[1:]
#     Range = [*range1, *range2, *range3]
#     print('bins:'+ str(Range))
#     # plt.hist(density_list, bins=int((max(density_list) - min(density_list)) / 10))
#     # plt.hist(density_list, bins=Range)
#     # plt.xticks(Range)
#     fig, ax = plt.subplots()
#     # ax.axvspan(q75, q90, color='grey')
#     # ax.hist(density_list, bins=int((max(density_list) - min(density_list)) / 10))
#     y, x, _ = ax.hist(density_list, edgecolor='white', bins=Range)
#     ax.set_xscale("log", nonpositive='clip')
#     for value in [(q75, '75%'), (q90, '90%')]:
#         ax.axvline(x=value[0], color='red', linestyle="--")
#         ax.text(value[0], 0.9*y.max(), value[1])
#
#     plt.title(title+f'\nmin: {Min}, q75: {q75}, q90: {q90}, max: {Max}')
#     plt.show()


input_addresses = "config.yaml"
ncut_times = 10
merge_times = 8
net, edges, densities, adj_mat, start_time, end_time = io.get_network(input_addresses)

# show_density_hist(densities)
# io.show_network(net, edges, densities, colormap_name="binary")  # density map
graph = Graph(adj_mat, densities)  #todo highways should be somehow implemented separately


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
    # io.show_network(net, edges, graph.labels, colormap_name="tab10")
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
    print_metrics(graph)
    # io.show_network(net, edges, graph.labels, colormap_name="tab10")
io.show_network(net, edges, graph.labels, colormap_name="tab10")


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
#             print("running %i")


#####
# finding MFDs
segment_ids = logic.get_segment_IDs(graph, list(edges))
# for i in range(len(segment_ids)):
#     edge_list = segment_ids[i]
#     print(i)
#     print(edge_list)
start_time = 21600.00
end_time = 25200.00
# segment_ids = list(segment_ids.keys())
MFD.plot_mfd(segment_ids, start_time, end_time)
print(segment_ids)
