import numpy as np
from Graph import Graph
from logic import var_metrics, merging, initial_segmentation
import io_handler as io
import logic_handler as logic
import matplotlib.pyplot as plt
# from MFD import updated_final_mfd
from MFD import Plot_MFD as MFD


def print_metrics(graph):
    labels = np.unique(graph.labels)
    print('mean densities:', str([round(var_metrics.segment_mean(graph, i), 3) for i in labels]))
    print('mean variance:', str([round(var_metrics.segment_var(graph, i), 3) for i in labels]))
    print('"b"s: ', str([var_metrics.find_b(graph, i) for i in labels]))
    print('NSs:', str([round(var_metrics.NS(graph, i), 4) for i in labels]))
    print('average NS:', str(round(var_metrics.average_NS(graph), 4)))
    print('new NSs:', str([round(var_metrics.NS(graph, i, NS_boundary_limit), 4) for i in labels]))
    print('average new NS:', str(round(var_metrics.average_NS(graph, NS_boundary_limit), 4)))
    print('new "b"s: ', str([var_metrics.find_b(graph, i,NS_boundary_limit) for i in labels]))
    print('TV:', str(round(var_metrics.TV(graph))))
    print('#of links: ', str([sum(graph.labels == i) for i in labels]))
    print(graph.rag[:, :, 0])
    print('')


def show_density_hist(density_list, title='density after deleting marginal links ()'):
    Min = int(min(density_list))
    Max = int(max(density_list))
    q75 = int(np.percentile(density_list, 75))
    q90 = int(np.percentile(density_list, 90))
    q95 = int(np.percentile(density_list, 95))
    print(f'density distribution: min: {Min}, q75: {q75}, q95: {q95}, max: {Max}')
    # range1 = range(Min, q75, int((q75-Min)/20))
    # range2 = range(q75, q90, int((q90-q75)/10))[1:]
    # range3 = range(q90, Max, int((Max-q90)/10))[1:]
    # Range = [*range1, *range2, *range3]
    range1 = range(Min, q95, 5)
    range2 = range(q95, Max, 30)
    Range = [*range1, *range2]
    print('bins:' + str(Range))
    fig, ax = plt.subplots()
    # ax.axvspan(q75, q90, color='grey')
    # ax.hist(density_list, bins=int((max(density_list) - min(density_list)) / 10))
    # y, x, _ = ax.hist(density_list, edgecolor='white')
    y, x, _ = ax.hist(density_list, edgecolor='white', bins=Range)
    # ax.set_xscale("log", nonpositive='clip')
    for value in [(q75, '75%'), (q95, '95%')]:
        ax.axvline(x=value[0], color='red', linestyle="--")
        ax.text(value[0], 0.9*y.max(), value[1])
    plt.title(title+f'\nmin: {Min}, q75: {q75}, q95: {q95}, max: {Max}')
    plt.show()


input_addresses = "config.yaml"
ncut_times = 10
merge_times = 7
NS_boundary_limit = 8
Merge_boundary_limit = 8
MERGING_alpha = 0  # DO NOT change it. it's not useful anymore. I should remove it later.
MFD_start_time = 18000.00
MFD_end_time = 36000.00

net, edges, densities, adj_mat = io.get_network(input_addresses)
graph = Graph(adj_mat, densities)

## APPLYING MEDIAN FILTER TO EXTREME VALUES AND GAUSSIAN FILTER TO ALL OF LINKS
graph.smooth_densities(median=False, gaussian=False)
densities = graph.densities
# note that in the second smoothing function (Graph._smooth()) we make a new list for densities

# todo highways should be somehow implemented separately

## SHOW DISTRIBUTION(HISTOGRAM) OF DENSITIES
# show_density_hist(densities, title=f'density after deleting marginal links ({start_time} - {end_time})')

## SHOW DENSITY MAP
# io.show_network(net, edges, np.abs(graph.densities - densities), colormap_name="binary")
# io.show_network(net, edges, densities, colormap_name="binary")

## SHOW ZERO DENSITY MAP
# zeros = np.zeros(len(densities)).astype(int)
# zeros[densities < 1] = 1
# zeros[densities < 0.5] = 2
# zeros[densities == 0] = 3
# # zeros[densities > 150] = 3
# io.show_network(net, edges, zeros, colormap_name="tab10")

## SHOW DISTRIBUTION OF <5 DENSITIES
# plt.hist(densities[densities < 5], edgecolor='white', bins=20)
# plt.title(f'with handling 0s and >q95 values + smoothing, total = {len(densities[densities < 5])}')
# plt.show()

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
    print_metrics(graph)
    # io.show_network(net, edges, graph.labels, colormap_name="tab10")
# io.show_network(net, edges, graph.labels, colormap_name="tab10")
io.show_network(net, edges, graph.labels, colormap_name="tab10")

#####
# running Merging
####
print('## MERGING')
for i in range(merge_times-1):
    merging.merge(graph, alpha=MERGING_alpha, min_boundary=Merge_boundary_limit)
    # alpha accounts for the degree we consider number of boundaries into merging algo
    # min_boundary drops neighbors with fewer boundaries from consideration
    print(np.unique(graph.labels))  # Do we have right number of segments?
    # io.show_network(net, edges, graph.labels, colormap="tab10",
    #                 save_adr=f'output/ncut4/merge-{max_number_of_clusters-i-1}.jpg')
    print_metrics(graph)
    io.show_network(net, edges, graph.labels, colormap_name="tab10")
io.show_network(net, edges, graph.labels, colormap_name="tab10")


#####
# finding MFDs
#####
segment_ids = logic.get_segment_IDs(graph, list(edges))
MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time)


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
