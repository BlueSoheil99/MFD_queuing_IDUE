import matplotlib.pyplot as plt
import numpy as np


cmap = plt.cm.tab10


def set_colormap(colorMap):
    global cmap
    cmap = colorMap


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
    for i in range(n_lines):
        x, data = _aggregate(mat[i, :], window_size=window_size)
        plt.plot(x, data, label=f'region {i}', color=cmap(i))
    plt.legend()
    plt.title(label)
    plt.xticks(x[::10], _get_hour(x, start=sim_start)[::10], rotation=45)
    plt.show()


def draw_empirical_completion_rates(vehicle_accumulation, vehicle_completion, window_size, label,
                                    with_scatter=False, with_intercept=True, scale_after_peak=None):
    num_labels = vehicle_accumulation.shape[0]
    completion_lines = dict()
    for i in range(num_labels):
        # making window_size-level aggregations
        x1, N = _aggregate(vehicle_accumulation[i, :5 * 3600], window_size=window_size)
        x2, C = _aggregate(vehicle_completion[i, :5 * 3600], window_size=window_size)
        N, C = np.array(N) / window_size, np.array(C) / window_size
        x_curve = np.linspace(min(N), int(max(N) * 0.95), 1000)

        if with_scatter:
            plt.scatter(N, C, s=2, color=cmap(i))

        # fitting a 3rd degree line
        polyfit_c = _get_polyfit_deg3(N, C, with_intercept)
        y_curve = np.polyval(polyfit_c, x_curve)
        plt.plot(x_curve, y_curve, color=cmap(i), label=f'region {i + 1}')

        # scaling the points after peak so that jam n goes higher (scaling N, not C)
        if scale_after_peak is not None:
            scale = scale_after_peak.get(i)
            if scale!= None:
                # find peak
                peakx, jamx = _get_max_and_jam_x(polyfit_c)
                # scale the N's after peak
                N_new = [scale * i if i > peakx else i for i in N]
                x_curve = np.linspace(min(N_new), int(max(N_new) * 0.95), 1000)
                polyfit_c = _get_polyfit_deg3(N_new, C, with_intercept)
                y_curve = np.polyval(polyfit_c, x_curve)
                plt.plot(x_curve, y_curve, color=cmap(i), label=f'region {i + 1} scaled after peak', linestyle='--')

                # # scale the N's after 2*peak
                # N_new = [scale * i if i > 2*peak else i for i in N]
                # x_curve = np.linspace(min(N_new), int(max(N_new) * 0.95), 1000)
                # polyfit_c = _get_polyfit_deg3(N_new, C, with_intercept)
                # y_curve = np.polyval(polyfit_c, x_curve)
                # plt.plot(x_curve, y_curve, color=cmap(i), label=f'region {i + 1} scaled after 2peak', linestyle='dotted')

                # scale the N's after peak with linear ratio
                N_new = [i + jamx*(scale-1)*((i-peakx)/(jamx-peakx)) if i > peakx
                         else i
                         for i in N]
                x_curve = np.linspace(min(N_new), int(max(N_new) * 0.95), 1000)
                polyfit_c = _get_polyfit_deg3(N_new, C, with_intercept)
                y_curve = np.polyval(polyfit_c, x_curve)
                plt.plot(x_curve, y_curve, color=cmap(i), label=f'region {i + 1} scaled linearly', linestyle='dotted')

                # plt.scatter(N, C, s=2, color=cmap(i), alpha=0.5)
                # plt.scatter(N_new, C, s=2, color=cmap(i))
        completion_lines[i] = polyfit_c

    plt.legend()
    plt.title(label)
    plt.xlabel('Number of vehicles')
    plt.ylabel('veh/sec')
    plt.show()
    return completion_lines


def draw_calculated_completion_rates(vehicle_accumulation, window_size, mfd_fit_lines, params_df, label):
    num_labels = vehicle_accumulation.shape[0]
    for i in range(num_labels):
        # making minute level aggregations
        x1, N = _aggregate(vehicle_accumulation[i, :5*3600], window_size=window_size)
        N = np.array(N) / window_size
        x_curve = np.linspace(min(N), int(max(N)*0.95), 1000)

        y_curve = np.polyval(mfd_fit_lines[i], x_curve)
        y_curve =y_curve/float(params_df[params_df['Region']==i+1]['avg_trip_length (m)'])
        # plt.plot(x_curve, y_curve, color=cmap(i), linewidth=0.6)
        plt.plot(x_curve, y_curve, color=cmap(i), label=f'region {i+1}')
    plt.legend()
    plt.title(label)
    plt.xlabel('Number of vehicles')
    plt.ylabel('veh/second')
    plt.show()


def _get_polyfit_deg3(x_values, y_values, with_intercept):
    if with_intercept:
        polyfit_c = np.polyfit(x_values, y_values, 3)
    else:
        x = np.array(x_values)
        y = np.array(y_values)
        polyfit_c = np.zeros(4)
        X = np.vstack([x ** i for i in range(3, 0, -1)]).T
        polyfit_c[:3] = np.linalg.lstsq(X, y, rcond=None)[0]
    return polyfit_c


def _get_max_and_jam_x(polyfit):
    poly_function = np.poly1d(polyfit)
    poly_derivative = poly_function.deriv()
    critical_points = np.roots(poly_derivative)
    return min(critical_points), max(critical_points)
