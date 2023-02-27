import numpy as np
from Graph import Graph
from logic import var_metrics, initial_segmentation, merging
import io_handler as io
import logic_handler as logic
from MFD import Plot_MFD as MFD
from logic.merging import _merge_segments
from logic.initial_segmentation import _get_segments


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


input_addresses = "config.yaml"
NS_boundary_limit = 8
Merge_boundary_limit = 8
MERGING_alpha = 0  # DO NOT change it. it's not useful anymore. I should remove it later.
MFD_start_time = 18000.00
MFD_end_time = 36000.00

net, edges, densities, adj_mat = io.get_network(input_addresses)
graph = Graph(adj_mat, densities)
graph.smooth_densities(median=False, gaussian=False)
densities = graph.densities

io.show_network(net, edges, graph.labels)
while True:
    IN = input('\nWhat is your command?(examples: cut 0, cut 5x, merge 2,3, merge 4x, mfd(   , separated, separated normalized), show, exit)\n').lower()
    command = IN.split()[0]

    if command == 'exit':
        break

    elif command == 'show':
        io.show_network(net, edges, graph.labels)

    elif command == 'mfd':
        segment_ids = logic.get_segment_IDs(graph, list(edges))
        IN = IN.split()
        if len(IN) > 1:
            if len(IN) == 2 or len(IN) == 3:
                if IN[1] == 'separated':
                    if IN[-1] == 'normalized':
                        MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time, separated=True, normalized=True)
                    else:
                        MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time, separated=True, normalized=False)
        else:
            MFD.plot_mfd(segment_ids, MFD_start_time, MFD_end_time)

    elif command == 'cut':
        command2 = IN.split()[1]
        if command2[-1] == 'x':
            times = int(command2[:-1])
            for i in range(times):
                initial_segmentation.get_segments(graph)
                print(np.unique(graph.labels))
                print('members of the new segment:', sum(graph.labels == i + 1))
                print_metrics(graph)
        else:
            parent = int(command2)
            _get_segments(graph, parent)
            print_metrics(graph)
        io.show_network(net, edges, graph.labels)

    elif command == 'merge':
        command2 = IN.split()[1]
        if command2[-1] == 'x':
            times = int(command2[:-1])
            for i in range(times):
                merging.merge(graph, alpha=MERGING_alpha, min_boundary=Merge_boundary_limit)
                print(np.unique(graph.labels))
                print_metrics(graph)
        else:
            indices = IN.split()[1]
            indices = indices.split(',')
            if len(indices) < 2:
                print('INPUT ERROR')
                continue
            _merge_segments(graph, int(indices[0]), int(indices[1]))
            print_metrics(graph)
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

