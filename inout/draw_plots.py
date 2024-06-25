import matplotlib.pyplot as plt
import numpy as np


def _aggregate(observations, window_size=10):
    aggregated_list = []
    window_start_indices = range(0, len(observations), window_size)
    for i in range(0, len(observations), window_size):
        window_end_index = min(i + window_size, len(observations))
        window_sum = sum(observations[i:window_end_index])
        aggregated_list.append(window_sum)
    return list(window_start_indices), aggregated_list


def _get_hour(indices, start=18000):
    indices = [int(start+i) for i in indices]
    indices = [f'{i // 3600}:{(i%3600)//60}' for i in indices]
    return indices

def show_vehicle_accumulation(accumulation:dict, labels, sim_start):
    cmap = plt.cm.tab10
    for label in labels:
        plt.plot(accumulation[label], label=f'region {label+1}', color=cmap(label))
    plt.legend()
    plt.title('Vehicle accumulations')
    plt.xlabel('Time')
    plt.ylabel('#Vehicles')
    x = np.linspace(0,len(accumulation[0]), len(accumulation[0]))
    plt.xticks(x[::15*60], _get_hour(x, start=sim_start)[::15*60], rotation=45)
    plt.show()


def draw_aggregated_data(mat, window_size, n_lines, sim_start, label):
    cmap = plt.cm.tab20
    for i in range(n_lines):
        x, data = _aggregate(mat[i, :], window_size=window_size)
        plt.plot(x, data, label=f'region {i}', color=cmap(i))
    plt.legend()
    plt.title(label)
    plt.xticks(x[::10], _get_hour(x, start=sim_start)[::10], rotation=45)
    plt.show()