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
    print(f'TV_n: {round(var_metrics.TVn(graph),3)}')
    average_cov, covs = var_metrics.average_cov(graph)
    # print(f'list of coefficients of variation: {covs}')
    print(f'average COV: {round(average_cov, 3)}')
    print('#of links: ', str([sum(graph.labels == i) for i in labels]))
    if len(labels) > 1:
        print('"b"s: ', str([var_metrics.find_b(graph, i) for i in labels]))
        # print('NSs:', str([round(var_metrics.NS(graph, i), 4) for i in labels]))
        print('average NS:', str(round(var_metrics.average_NS(graph), 4)))
        if new_NS:
            # print('new NSs:', str([round(var_metrics.NS(graph, i, NS_boundary_limit), 4) for i in labels]))
            print('average new NS:', str(round(var_metrics.average_NS(graph, NS_boundary_limit), 4)))
            print('new "b"s: ', str([var_metrics.find_b(graph, i, NS_boundary_limit) for i in labels]))
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
    if len(labels) > 1:
        metric_dict['"b"s'] = [var_metrics.find_b(graph, i) for i in labels]
        metric_dict['NSs'] = [round(var_metrics.NS(graph, i), 4) for i in labels]
        metric_dict['average NS'] = round(var_metrics.average_NS(graph), 4)
        metric_dict['new NSs'] = [round(var_metrics.NS(graph, i, NS_boundary_limit), 4) for i in labels]
        metric_dict['average new NS'] = round(var_metrics.average_NS(graph, NS_boundary_limit), 4)
        metric_dict['new "b"s'] = [var_metrics.find_b(graph, i, NS_boundary_limit) for i in labels]
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
    result_dict[str(n+1)] = l


def report_results_summary(address=None):
    # converting the result dictionary into a pd.Dataframe for saving into excel and investigation
    df = pd.DataFrame(result_dict, index=RESULT_CRITERIA)
    # save into excel file
    if address is not None:
        df.to_excel(address)
    return df


def make_partitions(graph, max_clusters):
    for i in range(max_clusters-1):
        initial_segmentation.get_segments(graph)
    graphs = list()
    graphs.append(copy.deepcopy(graph))
    while len(graphs) != max_clusters:
        merging.merge(graph)
        graphs.append(copy.deepcopy(graph))
    answers = dict()
    for i in range(len(graphs)):
        NS, TV = get_metrics(graphs[i])
        answers[max_clusters-i] = graphs[i].labels, NS, TV
    # todo use NSs to find the optimal number of clusters
    # todo include boundary_adjustment
    return answers


def get_segment_IDs(graph, edgeID_list):
    edgeID_list = np.array(edgeID_list)
    labels = np.unique(graph.labels)
    lookup = dict()
    for i in labels:
        args = np.argwhere(graph.labels==i)
        args = args.flatten()
        lookup[i] = list(edgeID_list[args])
    return lookup


