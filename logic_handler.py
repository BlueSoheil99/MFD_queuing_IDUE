import logic
from logic import var_metrics, initial_segmentation, merging
import copy
import numpy as np
import pandas as pd

RESULT_CRITERIA = ['average new NS', 'TV', 'TV_n', 'average_cov']
result_dict = dict()


def print_metrics(graph, new_NS=True, NS_boundary_limit=0):
    labels = np.unique(graph.labels)
    print('means:', str([round(var_metrics.segment_mean(graph, i), 3) for i in labels]))
    # print('variances:', str([round(var_metrics.segment_var(graph, i), 3) for i in labels]))
    print('TV:', str(round(var_metrics.TV(graph))))
    print(f'TV_n: {round(var_metrics.TVn(graph), 3)}')
    average_cov, covs = var_metrics.average_cov(graph)
    # print(f'list of coefficients of variation: {covs}')
    print(f'average COV: {round(average_cov, 3)}')
    print('#of links: ', str([sum(graph.labels == i) for i in labels]))
    if len(labels) - graph.first_unfixed_region > 1:
        print('"b"s: ', str([var_metrics.find_b(graph, i - graph.first_unfixed_region) for i in labels if
                             i >= graph.first_unfixed_region]))
        # print('NSs:', str([round(var_metrics.NS(graph, i), 4) for i in labels]))
        print('average NS:', str(round(var_metrics.average_NS(graph), 4)))
        if new_NS:
            # print('new NSs:', str([round(var_metrics.NS(graph, i, NS_boundary_limit), 4) for i in labels]))
            print('average new NS:', str(round(var_metrics.average_NS(graph, NS_boundary_limit), 4)))
            print('new "b"s: ',
                  str([var_metrics.find_b(graph, i - graph.first_unfixed_region, NS_boundary_limit) for i in labels if
                       i >= graph.first_unfixed_region]))
    print(graph.rag[:, :, 0])
    print('')


def get_metrics(graph, NS_boundary_limit=0):
    labels = np.unique(graph.labels)
    metric_dict = dict()
    metric_dict['means'] = [round(var_metrics.segment_mean(graph, i), 3) for i in labels]
    metric_dict['variance'] = [round(var_metrics.segment_var(graph, i), 3) for i in labels]
    metric_dict['TV'] = round(var_metrics.TV(graph))
    metric_dict['TV_n'] = round(var_metrics.TVn(graph), 3)
    metric_dict['average_cov'], metric_dict['covs'] = var_metrics.average_cov(graph)
    metric_dict['# of links'] = [sum(graph.labels == i) for i in labels]
    if len(labels) - graph.first_unfixed_region > 1:
        metric_dict['"b"s'] = [var_metrics.find_b(graph, i - graph.first_unfixed_region) for i in labels if
                               i >= graph.first_unfixed_region]
        metric_dict['NSs'] = [round(var_metrics.NS(graph, i - graph.first_unfixed_region), 4) for i in labels if
                              i >= graph.first_unfixed_region]
        metric_dict['average NS'] = round(var_metrics.average_NS(graph), 4)
        metric_dict['new NSs'] = [round(var_metrics.NS(graph, i - graph.first_unfixed_region, NS_boundary_limit), 4) for
                                  i in labels if i >= graph.first_unfixed_region]
        metric_dict['average new NS'] = round(var_metrics.average_NS(graph, NS_boundary_limit), 4)
        metric_dict['new "b"s'] = [var_metrics.find_b(graph, i - graph.first_unfixed_region, NS_boundary_limit) for i in
                                   labels if i >= graph.first_unfixed_region]
    return metric_dict


def update_result_dict(graph, NS_boundary_limit=0):
    # we use this function for saving the results metrics for each step of the algorithm.
    # we don't want to put the numbers into excel manually every time we want to get results and interpret them
    n = len(result_dict)
    metrics = get_metrics(graph, NS_boundary_limit)
    l = list()
    for criterion in RESULT_CRITERIA:
        try:
            metric = metrics[criterion]
            l.append(round(metric, 3))
        except:
            l.append('-')
    result_dict[str(n + 1)] = l


def report_results_summary(address=None):
    # converting the result dictionary into a pd.Dataframe for saving into excel and investigation
    df = pd.DataFrame(result_dict, index=RESULT_CRITERIA)
    # save into excel file
    if address is not None:
        df.to_excel(address)
    return df


def make_partitions(graph, max_clusters):
    for i in range(max_clusters - 1):
        initial_segmentation.get_segments(graph)
    graphs = list()
    graphs.append(copy.deepcopy(graph))
    while len(graphs) != max_clusters:
        merging.merge(graph)
        graphs.append(copy.deepcopy(graph))
    answers = dict()
    for i in range(len(graphs)):
        NS, TV = get_metrics(graphs[i])
        answers[max_clusters - i] = graphs[i].labels, NS, TV
    # todo use NSs to find the optimal number of clusters
    # todo include boundary_adjustment
    return answers


def get_segment_IDs(graph, edgeID_list):
    edgeID_list = np.array(edgeID_list)
    labels = np.unique(graph.labels)
    lookup = dict()
    for i in labels:
        args = np.argwhere(graph.labels == i)
        args = args.flatten()
        lookup[i] = list(edgeID_list[args])
    return lookup


def get_boundary_IDs(graph, edgeID_array, get_neighbors=False):
    old_dict = graph.get_boundary_indices(get_neighbors=get_neighbors)
    new_dict = dict()
    for seg_id, seg_boundary_indices in old_dict.items():
        if get_neighbors:
            # seg_boundary_indices -> set of "boundary index: {its neighbors: their region ids}" pairs
            replacement = dict()
            for boundary_index, neighbors in seg_boundary_indices.items():
                replacement[edgeID_array[boundary_index]] = {edgeID_array[idx]:neighbors[idx] for idx in neighbors.keys()}
        else:
            # seg_boundary_indices -> just a list of  "boundary indices"
            replacement = [edgeID_array[idx] for idx in seg_boundary_indices]
        new_dict[seg_id] = replacement
    return new_dict


def cursor_update_segment_ID(graph, edge_list, edge_id, new_NS=True, NS_boundary_limit=0):
    index = list(edge_list).index(edge_id)
    labels_list = np.copy(graph.labels)
    label = labels_list[index]
    print(f'{"~.~."*5}\n id: {edge_id}, label : {label}')
    neighbors = graph.get_neighbor_indices_and_regions(index)  # contains neighbor_index: neighbor_region_id pairs
    neighbors = {edge_list[idx]: neighbors[idx] for idx in neighbors.keys()}
    # contains neighbor_edge_id: neighbor_region_id pairs
    print(f'neighbor edges and their region IDs: {neighbors}')

    valid_options = list(np.unique(list(neighbors.values())))  # our options are the neighbor_IDs of selected link
    # todo maybe we simply need this: valid_options = list(np.unique(graph.labels))
    if label in valid_options: valid_options.remove(label)  # current label is not an option
    valid_options.append(np.max(graph.labels) + 1)  # in case of building a new segment

    IN = input(f' -- Enter the new region number from {valid_options} or anything else to cancel: ')

    try:
        IN = int(IN)
        if IN in valid_options:
            labels_list[index] = IN
            graph.set_labels(labels_list)
            print(f'Change in the label of {edge_id}: {label} -> {IN} \n   ----- NEW METRICS----')
            print_metrics(graph, new_NS=new_NS, NS_boundary_limit=NS_boundary_limit)
        else:
            print(f'No action on edge: {edge_id}')
    except:
        print(f'No action on edge: {edge_id}')
    print(' -- Select a new edge or close the window -- ')

