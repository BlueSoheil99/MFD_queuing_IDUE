import numpy as np

import logic_handler
from Graph import Graph
from logic import initial_segmentation, merging
import io_handler as io
import logic_handler as logic
from MFD import Plot_MFD as MFD
from logic.merging import _merge_segments
from logic.initial_segmentation import _get_segments


input_addresses = "config files/config.yaml"
NS_boundary_limit = 0
Merge_boundary_limit = 0
MERGING_alpha = 0  # DO NOT change it. it's not useful anymore. I should remove it later.
MFD_start_time = 18000.00
MFD_end_time = 36000.00

summary_output_address = f'output/results-interactive.xlsx'


net, edges, densities, adj_mat, labels = io.get_network(input_addresses)
graph = Graph(adj_mat, densities, labels)
# graph.smooth_densities(median=True, gaussian=True)
# densities = graph.densities

# labels = []
# for i in range(len(edges)):
#     edge = edges[i]
#     neighbors = graph.get_neighbor_indices_and_regions(i)
#     if len(neighbors)>1:
#         labels.append(0)
#     if len(neighbors) == 1:
#         labels.append(1)
#     if len(neighbors) == 0:
#         labels.append(2)
# graph.labels = labels

# import datetime
# date_time = str(datetime.datetime.now())
# with open(f'data/config data/valid_edges_{date_time}.txt', 'w') as f:
#     for edge in edges:
#         f.write(edge+'\n')

io.show_network(net, edges, graph.labels)

while True:
    IN = input('\nWhat is your command?(examples: cut 0, cut 5x, merge 2,3, merge 4x, '
               'mfd(   , separated, separated normalized), density_speed, density_flow, show, exp, exit)\n').lower()
    IN = IN.split()
    command = IN[0]

    sep, norm = False, False
    if len(IN) > 1:
        if len(IN) == 2 or len(IN) == 3:
            if IN[1] == 'separated':
                sep = True
                if IN[-1] == 'normalized':
                    norm = True

    if command == 'exit':
        break

    elif command == 'show':
        func = None
        # if IN[-1] == 'interactive': func = lambda x: logic_handler.cursor_sdhow_segment_ID(x)
        if IN[-1] == 'interactive': func = (lambda x: print(x))
        io.show_network(net, edges, graph.labels, interactive_func=func)

    elif command == 'adjustment':
        io.show_network(net, edges, graph.labels,
                        interactive_func=lambda x:
                        logic_handler.cursor_update_segment_ID(graph, edges, x,
                                                               new_NS=True, NS_boundary_limit=NS_boundary_limit))

    elif command == 'mfd':
        segment_ids = logic.get_segment_IDs(graph, list(edges))
        MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=sep, normalized=norm, mfd=True)

    elif command == 'density_speed':
        segment_ids = logic.get_segment_IDs(graph, list(edges))
        MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=sep, normalized=norm, speed_vs_den=True)

    elif command == 'density_flow':
        segment_ids = logic.get_segment_IDs(graph, list(edges))
        MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=sep, normalized=norm, flow_vs_den=True)

    elif command == 'number_production':
        boundary_ids = logic.get_boundary_IDs(graph, edges, get_neighbors=True)
        segment_ids = logic.get_segment_IDs(graph, list(edges))
        MFD.MFD_plotter((segment_ids, boundary_ids), MFD_start_time, MFD_end_time, separated=sep, normalized=norm, num_vs_prod=True)

    elif command == 'cut':
        command2 = IN[1]
        if command2[-1] == 'x':
            times = int(command2[:-1])
            for i in range(times):
                initial_segmentation.get_segments(graph)
                print(np.unique(graph.labels))
                print('members of the new segment:', sum(graph.labels == max(graph.labels)))
                logic.print_metrics(graph, new_NS=True, NS_boundary_limit=NS_boundary_limit)
                logic.update_result_dict(graph, NS_boundary_limit)

        else:
            parent = int(command2)
            _get_segments(graph, parent)
            logic.print_metrics(graph, new_NS=True, NS_boundary_limit=NS_boundary_limit)
        io.show_network(net, edges, graph.labels)

    elif command == 'merge':
        command2 = IN[1]
        if command2[-1] == 'x':
            times = int(command2[:-1])
            for i in range(times):
                merging.merge(graph, alpha=MERGING_alpha, min_boundary=Merge_boundary_limit)
                print(np.unique(graph.labels))
                logic.print_metrics(graph, new_NS=True, NS_boundary_limit=NS_boundary_limit)
                logic.update_result_dict(graph, NS_boundary_limit)

        else:
            indices = IN[1]
            indices = indices.split(',')
            if len(indices) < 2:
                print('INPUT ERROR')
                continue
            _merge_segments(graph, int(indices[0]), int(indices[1]))
            logic.print_metrics(graph, new_NS=True, NS_boundary_limit=NS_boundary_limit)
        io.show_network(net, edges, graph.labels)

    elif command == 'marginal':
        edges_tmp = list(edges)
        ncut_times = len(np.unique(graph.labels))
        for i in range(ncut_times):
            members_id = np.argwhere(graph.labels == i)
            with open("./output/seattle_cut1.txt", 'a') as f:
                for k in range(len(members_id)):
                    f.write('{}\t{}\n'.format(str(i), edges_tmp[members_id[k][0]]))
                    print("running %i")
        f.close()

    elif command == 'results':
        if len(IN) ==2:
            if IN[1] == 'update':
                logic.update_result_dict(graph, NS_boundary_limit)
                print('results updated')
            elif IN[1] == 'write':
                results = logic.report_results_summary(summary_output_address)
                print('results written')

