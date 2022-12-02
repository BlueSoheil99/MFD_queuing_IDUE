import utility as util
import sumolib.xml as sumoxml


def getWeakly_connected(net, vclass="private"):
    components = []
    edgesLeft = set(net.getEdges())
    queue = list()
    while len(edgesLeft) != 0:
        component = set()
        queue.append(edgesLeft.pop())
        while not len(queue) == 0:
            edge = queue.pop(0)
            if vclass is None or edge.allows(vclass):
                component.add(edge.getID())
                for n in edge.getOutgoing():
                    if n in edgesLeft:
                        queue.append(n)
                        edgesLeft.remove(n)
                for n in edge.getIncoming():
                    if n in edgesLeft:
                        queue.append(n)
                        edgesLeft.remove(n)
        if component:
            components.append(sorted(component))
    return components


def connectivity(input_addresses, out_folder="./output/", out_name="seattle"):
    """This program is for checking connectivity (weakly connectivity) of a SUMO network
    :param input_addresses: path that save the config file
    :param out_folder: the output folder, default is "/output/"
    :param out_name: the name of the network
    :return: This program does not return anything, but save the summaries (listed below) in the output folder:
        (1) check_component_output.txt: specify how many subnetworks and each subnetwork's link ID and type
        (2) check_results_output.txt: summary of the checking
        (3) *out_name*comp#.txt: save all the link IDs in each subnetwork
    """
    net_fname, _, _, = util.init_config(input_addresses)
    net, nodes, edges = util.read_network(net_fname)
    components = getWeakly_connected(net)
    if len(components) != 1:
        print("Warning! Net is not connected.")

    total = 0
    max_cnt = 0
    max_idx = ""
    # stores the distribution of components by edge counts - key: edge
    # counts - value: number found
    edge_count_dist = {}
    output_str_list = []
    dist_str_list = []
    component_edge_count = []

    # iterate through components to output and summarise
    for idx, comp in enumerate(sorted(components, key=lambda c: next(iter(c)))):
        with open("{}comp{}.txt".format(out_folder + out_name, idx), 'w') as f:
            for e in comp:
                f.write("edge:{}\n".format(e))
        types = set()

        for e in comp:
            types.add(net.getEdge(e).getType())
            if len(types) > 10:
                break

        edge_count = len(comp)
        component_edge_count.append(edge_count)
        total += edge_count
        if edge_count > max_cnt:
            max_cnt = edge_count
            max_idx = idx

        if edge_count not in edge_count_dist:
            edge_count_dist[edge_count] = 0
        edge_count_dist[edge_count] += 1
        output_str = "Component: #{} Edge Count: {}\n {}\n".format(
            idx, edge_count, " ".join(comp))
        if types:
            output_str += "Type(s): {}\n".format(" ".join(sorted(types)))
        print(output_str)
        output_str_list.append(output_str)

    # output the summary of all edges checked and largest component
    # to avoid divide by zero error if total is 0 for some reason.
    coverage = 0.0
    if total > 0:
        coverage = round(max_cnt * 100.0 / total, 2)
    summary_str = "Total Edges: {}\nLargest Component: #{} Edge Count: {} Coverage: {}%\n".format(
        total, max_idx, max_cnt, coverage)
    print(summary_str)
    dist_str = "Edges\tIncidence"
    print(dist_str)
    dist_str_list.append(dist_str)

    # output the distribution of components by edge counts
    for key, value in sorted(edge_count_dist.items()):
        dist_str = "{}\t{}".format(key, value)
        print(dist_str)
        dist_str_list.append(dist_str)

    # check for output of components to file
    component_output = out_folder + "check_component_output.txt"
    print("Writing component output to: {}".format(component_output))
    with open(component_output, 'w') as f:
        f.write("\n".join(output_str_list))

    # Check for output of results summary to file
    results_output = out_folder + "check_results_output.txt"
    if results_output is not None:
        print(
            "Writing results output to: {}".format(results_output))
        with open(results_output, 'w') as r:
            r.write(summary_str)
            r.write("\n".join(dist_str_list))

    print('Please add the following to config.yaml: edges_name: "{}"'.format(
        out_folder + "{}comp{}.txt".format(out_name, str(component_edge_count.index(max_cnt)))))


def redundant_edges(edges, info_name, option):
    """
    Layout all the edges that never have density
    :param edges: list of all SUMO edges
    :param info_name:
    :param option: Feature that we would like to observe. e.g., density
    :return:
    """
    edge_diction = {edge.getID(): 0 for edge in edges}
    edge_stats = sumoxml.parse(info_name, "edge")
    i = 0
    for edge in edge_stats:
        try:
            edge_diction[edge.id] += float(edge.getAttribute(option))
        except:
            i += 1
            # print("{} has no attribute: {}".format(edge.id, option))
    print("Total number of edges without {} are {}".format(option, i))

    with open("./output/zero_{}_edgeID.txt".format(option), 'w') as f:
        keys = list(edge_diction.keys())
        for i, x in enumerate(edge_diction.values()):
            if x == 0:
                f.write("{}\n".format(keys[i]))