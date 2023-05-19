import numpy as np
from Graph import Graph
from logic import initial_segmentation, merging
import io_handler as io
import logic_handler as logic
from MFD import Plot_MFD as MFD
from logic.merging import _merge_segments
from logic.initial_segmentation import _get_segments


input_addresses = "config files/config.yaml"
NS_boundary_limit = 8
Merge_boundary_limit = 8
MERGING_alpha = 0  # DO NOT change it. it's not useful anymore. I should remove it later.
MFD_start_time = 18000.00
MFD_end_time = 36000.00

net, edges, densities, adj_mat = io.get_network(input_addresses)
graph = Graph(adj_mat, densities)
# graph.smooth_densities(median=True, gaussian=True)
# densities = graph.densities

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
        io.show_network(net, edges, graph.labels)

    elif command == 'mfd':
        segment_ids = logic.get_segment_IDs(graph, list(edges))
        MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=sep, normalized=norm, mfd=True)

    elif command == 'density_speed':
        segment_ids = logic.get_segment_IDs(graph, list(edges))
        MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=sep, normalized=norm, speed_vs_den=True)

    elif command == 'density_flow':
        segment_ids = logic.get_segment_IDs(graph, list(edges))
        MFD.MFD_plotter(segment_ids, MFD_start_time, MFD_end_time, separated=sep, normalized=norm, flow_vs_den=True)

    elif command == 'cut':
        command2 = IN[1]
        if command2[-1] == 'x':
            times = int(command2[:-1])
            for i in range(times):
                initial_segmentation.get_segments(graph)
                print(np.unique(graph.labels))
                print('members of the new segment:', sum(graph.labels == i + 1))
                logic.print_metrics(graph, new_NS=True, NS_boundary_limit=NS_boundary_limit)
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

