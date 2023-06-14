import numpy as np
from Graph import Graph
from logic import var_metrics, merging, initial_segmentation
import io_handler as io
import logic_handler as logic
import matplotlib.pyplot as plt
from MFD import Plot_MFD as MFD


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


input_addresses = "config files/config.yaml"
ncut_times = 8
merge_times = 8
NS_boundary_limit = 8
Merge_boundary_limit = 8
MERGING_alpha = 0  # DO NOT change it. it's not useful anymore. I should remove it later.
MFD_start_time = 18000.00
MFD_end_time = 36000.00
# priority_metric = 'TV_n'   # todo work with different metrics
priority_metric = 'average new NS'
min_num_of_links = 150
summary_output_address = f'output/{ncut_times-1}-{merge_times-1}-min_size {min_num_of_links}-results-{priority_metric}.xlsx'
# summary_output_address = None


net, edges, densities, adj_mat = io.get_network(input_addresses)
#todo net, edges, densities, adj_mat, predetermined_labels = io.get_network(input_addresses)
graph = Graph(adj_mat, densities)

## APPLYING MEDIAN FILTER TO EXTREME VALUES AND GAUSSIAN FILTER TO ALL OF LINKS
# graph.smooth_densities(median=True, gaussian=True)
densities = graph.densities
# note that in the second smoothing function (Graph._smooth()) we make a new list for densities

## SHOW DISTRIBUTION(HISTOGRAM) OF DENSITIES
# show_density_hist(densities, title=f'density after deleting marginal links (8-9)')

## SHOW FEATURE(e.g., density) MAP
# io.show_network(net, edges, np.abs(graph.densities - densities), colormap_name="binary")
# io.show_network(net, edges, densities, colormap_name="binary")

## SHOW ZERO DENSITY MAP
zeros = np.ones(len(densities)).astype(int)*2
zeros[densities < 5] = 1
zeros[densities == 0] = 3  # zero or None values
# # zeros[densities > 150] = 3
io.show_network(net, edges, zeros)

## SHOW DISTRIBUTION OF <5 DENSITIES
plt.hist(densities[densities < 5], edgecolor='white', bins=20)
plt.title(f'with handling 0s and >q95 values + smoothing, total = {len(densities[densities < 5])}')
# plt.show()

#####
# running NCut
####
print('\n## INITIAL PARTITIONING\nTV for 1 big segment:', str(round(var_metrics.TV(graph))), '\n', 'mean density:', str(round(var_metrics.segment_mean(graph, 0), 2)), '\n')
for i in range(ncut_times-1):
    ## traditional method
    # initial_segmentation.get_segments(graph)

    # ##new method
    from copy import deepcopy
    decision_criteria = list()
    valid_parents = list()
    labels = np.unique(graph.labels)
    for id in labels:
        copy = deepcopy(graph)
        initial_segmentation._get_segments(copy, id)
        metrics = logic.get_metrics(copy, NS_boundary_limit=NS_boundary_limit)
        if all(number > min_num_of_links for number in metrics['# of links']):
            decision_criteria.append(metrics[priority_metric])
            valid_parents.append(id)
    id = valid_parents[np.argmin(np.array(decision_criteria))]
    print(f'segment {id} is being cut')
    initial_segmentation._get_segments(graph, id)
    #####

    print(np.unique(graph.labels))
    print('members of the new segment:', sum(graph.labels == i+1))
    # io.show_network(net, edges, graph.labels, save_adr=f'output/ncut4/ncut4-{i+2}.jpg')
    logic.print_metrics(graph, new_NS=True, NS_boundary_limit=NS_boundary_limit)
    logic.update_result_dict(graph, NS_boundary_limit)
    # io.show_network(net, edges, graph.labels)

io.show_network(net, edges, graph.labels)

#####
# running Merging
####
print('## MERGING')
for i in range(merge_times-1):
    if i == merge_times-2:
    ## traditional method
        merging.merge(graph, alpha=MERGING_alpha, min_boundary=Merge_boundary_limit)
    # merging.merge(graph, alpha=MERGING_alpha, min_boundary=Merge_boundary_limit)
    # alpha accounts for the degree we consider number of boundaries into merging algo
    # min_boundary drops neighbors with fewer boundaries from consideration
    else:
    ## new method
        from copy import deepcopy
        decision_criteria = []
        labels = np.unique(graph.labels)  # todo change to valid combinations
        valid_combinations = []
        RAG = (merging._clean_rag(np.copy(graph.rag), Merge_boundary_limit))[:, :, 1]
            # we still shouldn't merge regions with tiny boundary links
            # rag[0] and rag[1] shouldn't make a difference
        for i in labels[:-1]:
            for j in labels[i+1:]:
                id1, id2 = labels[i], labels[j]
                if RAG[id1, id2]>0:
                    valid_combinations.append((id1, id2))
                    copy = deepcopy(graph)
                    merging._merge_segments(copy, id1, id2)
                    metrics = logic.get_metrics(copy, NS_boundary_limit=NS_boundary_limit)
                    decision_criteria.append(metrics[priority_metric])
        selected_comb = valid_combinations[np.argmin(np.array(decision_criteria))]
        id1 = selected_comb[0]
        id2 = selected_comb[1]
        print(f'--segments {id1} and {id2} are merging---')
        merging._merge_segments(graph, id1, id2)
    #####
    print(np.unique(graph.labels))
    # io.show_network(net, edges, graph.labels, save_adr=f'output/ncut4/merge-{max_number_of_clusters-i-1}.jpg')
    logic.print_metrics(graph, new_NS=True, NS_boundary_limit=NS_boundary_limit)
    logic.update_result_dict(graph, NS_boundary_limit)
    io.show_network(net, edges, graph.labels)

    segment_ids = logic.get_segment_IDs(graph, list(edges))
    MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=False, normalized=False, flow_vs_den=True)
    # MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=True, normalized=True, flow_vs_den=True)

io.show_network(net, edges, graph.labels)


#####
# finding MFDs and saving results
#####
results = logic.report_results_summary(summary_output_address)
print(results)

segment_ids = logic.get_segment_IDs(graph, list(edges))
MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=False, normalized=False, mfd=True)
MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=False, normalized=False, flow_vs_den=True)
if len(np.unique(graph.labels))>1:
    MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=True, normalized=False, mfd=True)
    MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=True, normalized=True, mfd=True)

    MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=True, normalized=False, flow_vs_den=True)
    MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=True, normalized=True, flow_vs_den=True)


#todo
# show predetermined clusters and show all MFDs
# export output

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
#     f.close()
