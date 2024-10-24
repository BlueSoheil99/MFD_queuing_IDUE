import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
import numpy as np
import pickle
import io_handler as io

# codes for creating .pickle files are transferred into pickle_creator.py

address_edge_data = "data/edge_data_output_min_congested.pickle"
# address_edge_data = "data/edge_data_output_min.pickle"

address_over4priorities = 'data/over4priority.txt'

input_addresses = "config files/config.yaml"
net, _, _, _, _ = io.get_network(input_addresses)

edge_stats = None  # it contains edge_data output
edge_vehicle_stats = None  # it contains my traci output. shows the vehicles included in each link in each minute
vehicle_arrival_stats = None

over4priorities = None

# Define markers and colors for each group
markers = ["*", "s", "^", "D", "x", "+", "o", "^"]
sizes = [3, 3, 3, 3, 3, 3]
cmap = plt.cm.tab10  # Define the colormap
# cmap = plt.cm.tab20  # Define the colormap


def open_pickle(address: str):
    with open(address, "rb") as f:
        file = pickle.load(f)
        f.close()
    return file


def open_over4_priorities(address: str):
    over4_priorities = []
    with open(address, "r") as f:
        for line in f.readlines():
            edge = line.strip().split(':')[1]
            over4_priorities.append(edge)
    return over4_priorities


def MFD_plotter(group_dict, start_time, end_time, separated=False, normalized=True,
                mfd=False, mfd1=False, speed_vs_den=False, flow_vs_den=False,
                num_vs_prod=False, num_vs_speed=False, time_vs_num=False, den_vs_prod=False):
    if separated:
        if num_vs_prod: r = (len(group_dict[0].keys())+1) // 2
        else: r = (len(group_dict.keys())+1) // 2
        if normalized:
            fig = plt.figure()
            gs = fig.add_gridspec(r, 2, hspace=0, wspace=0)
            axs = gs.subplots(sharex=True, sharey=True)
        else:
            fig, axs = plt.subplots(r, 2)
    else:
        fig, axs = plt.subplots()

    fit_lines = None
    #we define number of plots needed
    if mfd:
        _plot_mfd(group_dict, start_time, end_time, axs=axs, separated=separated, normalized=normalized)
        fig.suptitle('Number of vehicles vs Total veh-km traveled per minute')
    if mfd1:
        fig.suptitle('Aggregated Flow Rate (q) vs. Number of vehicles(n)')
        _plot_mfd_type1(group_dict, start_time, end_time, axs=axs, separated=separated, normalized=normalized)
    if speed_vs_den:
        fig.suptitle('Aggregated Space Mean Speed (v) vs. Aggregated Density (k)')
        _plot_speed_density_curve(group_dict, start_time, end_time, axs=axs, separated=separated, normalized=normalized)
    if flow_vs_den:
        fig.suptitle("Aggregated Flow Rate (q) vs. Aggregated Density (k)")
        _plot_flow_density_curve(group_dict, start_time, end_time, axs=axs, separated=separated, normalized=normalized)
    if num_vs_prod:
        fig.suptitle("production rate vs. number of vehicles")
        # _plot_number_production_curve(group_dict, start_time, end_time, axs=axs, separated=separated, normalized=normalized)
        fit_lines = _plot_number_production_theoretical_curve(group_dict, start_time, end_time, axs=axs, separated=separated, normalized=normalized)
    if den_vs_prod:
        fig.suptitle("production rate vs. Aggregated Density (k)")
        _plot_density_production_curve(group_dict, start_time, end_time, axs=axs, separated=separated, normalized=normalized)
    if num_vs_speed:
        fig.suptitle("weighted speed vs. number of vehicles")
        _plot_number_speed_curve(group_dict, start_time, end_time, axs=axs, separated=separated, normalized=normalized)
    if time_vs_num:
        fig.suptitle("number of vehicles vs. simulation time")
        _plot_time_number_curve(group_dict, start_time, end_time, axs=axs, separated=separated, normalized=normalized)
    plt.show()
    return fit_lines


def _fit_line(x, y, deg: int, with_intercept:True):
    if with_intercept:
        int_on = np.polyfit(x, y, deg)
        return int_on
    else:
        x = np.array(x)
        y = np.array(y)
        int_off = np.zeros(deg+1)
        X = np.vstack([x ** i for i in range(deg, 0, -1)]).T  # X matrix without the constant term
        # Solve for the coefficients using least squares, forcing intercept to 0
        int_off[:deg] = np.linalg.lstsq(X, y, rcond=None)[0]
        return int_off


def _modify_appearance(axs, number_of_plots, separated, normalized, xlabel, ylabel):
    if separated:
        if number_of_plots % 2 == 1:
            axs[number_of_plots//2, 1].remove()
        for i, ax in enumerate(axs.flat):
            ax.legend()
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)
            if i%2 == 0:
                ax.set(ylabel=ylabel)
            if i in [number_of_plots-1, number_of_plots-2]:
                ax.set(xlabel=xlabel)
            if normalized:
                ax.label_outer()
    else:
        ax = axs
        # Set x and y axis label font size and weight
        ax.set_xlabel(xlabel, fontsize=14, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=14, fontweight="bold")
        # Set x and y axis tick font size and weight
        ax.tick_params(axis="x", labelsize=12, which="both", direction="in", bottom=True, top=True, left=True,
                       right=True)
        ax.tick_params(axis="y", labelsize=12, which="both", direction="in", bottom=True, top=True, left=True,
                       right=True)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        ax.legend()


def _draw_plot(xvalues, yvalues, polyfit_s_d, extrapolation, show_deviation, ax, label, marker, size, color):

    ax.scatter(xvalues, yvalues, label=label, marker=marker, s=size, color=color)

    x_curve = np.linspace(min(xvalues), max(xvalues) + extrapolation, 1000)
    y_curve = np.polyval(polyfit_s_d, x_curve)
    ax.plot(x_curve, y_curve, color=color, linewidth=0.6)

    if show_deviation:
        yhat = np.polyval(polyfit_s_d, xvalues)
        deviation = np.abs(yhat - yvalues)
        std_dev = np.std(deviation)
        std_dev = np.sqrt(np.sum(deviation**2)/len(deviation))  # todo is it correctly working?
        ax.plot(xvalues, yhat + std_dev, '--', linewidth=0.5, alpha=0.75, color=color)
        ax.plot(xvalues, yhat - std_dev, '--', linewidth=0.5, alpha=0.75, color=color)

        ax.plot(xvalues, yhat + 2*std_dev, '-.', linewidth=0.5, alpha=0.75, color=color)
        ax.plot(xvalues, yhat - 2*std_dev, '-.', linewidth=0.5, alpha=0.75, color=color)


def _get_figure_config(idx, axs, separated):
    marker = markers[idx % len(markers)]
    size = sizes[idx % len(sizes)]
    color = cmap(idx)
    if separated:
        if len(axs) >= 2:
            ax = axs[idx // 2, idx % 2]
        else:
            ax = axs[idx % 2]
    else:
        ax = axs
    return ax, marker, size, color


def _plot_mfd(group_dict, start_time, end_time, axs, separated=False, normalized=True):
    global edge_stats
    if edge_stats is None: edge_stats = open_pickle(address_edge_data)

    for i, (group_id, edge_list) in enumerate(group_dict.items()):
        tnvehs_group = []
        tvkpm_group = []
        for interval_id, edges_data in edge_stats.items():
            if float(interval_id) <= start_time or float(interval_id) > end_time:
                continue
            total_nvehs = 0
            total_vkpm = 0
            no_of_edges = 0

            for edge_id in edge_list:
                if edge_id in edges_data:
                    edge_data = edges_data[edge_id]
                    edge_length_new = net.getEdge(edge_id).getLength()
                    speed = edge_data["speed"]
                    density = edge_data["laneDensity"]
                    sampled_seconds = edge_data["sampledSeconds"]
                    # weighted speed = speed*Edgelength
                    # Sum the weighted speed values for all the edges in the region.Sum the lengths of all the edges in the region.
                    # Divide the sum of the weighted speed values by the sum of the lengths of all the edges in the region to obtain the region's
                    if speed is not None and density is not None:
                        total_nvehs += float(sampled_seconds) / 60
                        total_vkpm += float(speed) * float(sampled_seconds) / 1000
                        # Edgelength = ((float(sampled_seconds) / 60) * 1000) / float(density)  # in m
                        # total_weighteddensity = total_weighteddensity + float(density)  # in veh/km/lane
                        # total_weightedspeed = total_weightedspeed + (
                        #         (float(speed) * 3600 / 1000) * (float(Edgelength) / 1000))  # in km/hr
                        # total_edge_length = total_edge_length + (float(Edgelength) / 1000)  # in km
                        no_of_edges += 1

            tnvehs_group.append(total_nvehs)
            tvkpm_group.append(total_vkpm)

        # Use different marker and size for each group
        marker = markers[i % len(markers)]
        size = sizes[i % len(sizes)]
        if separated:
            if len(axs)>=2:
                ax = axs[i // 2, i % 2]
            else:
                ax = axs[i % 2]
        else:
            ax = axs

        # fit a second oredr ploynomial -density vs speed
        polyfit_s_d = np.polyfit(tnvehs_group, tvkpm_group, 3)
        polyline_s_d = np.polyval(polyfit_s_d, tnvehs_group)
        deviation_s_d = np.abs(polyline_s_d - tvkpm_group)
        std_dev_s_d = np.std(deviation_s_d)

        x_curve = np.linspace(min(tnvehs_group), max(tnvehs_group)+10, 1000)
        y_curve = np.polyval(polyfit_s_d, x_curve)

        # for no of veh vs veh per km ---per min
        ax.scatter(tnvehs_group, tvkpm_group, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        # for density vs speed ---per min
        # ax.scatter(tdensity, tspeed, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        ax.plot(x_curve, y_curve, color=cmap(i), linewidth=0.8)
        # ax.plot(tnvehs_group, polyline_s_d, color=cmap(i), linewidth=0.8)
        # ax.plot(tnvehs_group, polyline_s_d + std_dev_s_d, '--', color='lightgray')
        # ax.plot(tnvehs_group, polyline_s_d - std_dev_s_d, '--', color='lightgray')

    _modify_appearance(axs, len(group_dict), separated, normalized, xlabel='Number of Vehicles', ylabel='veh-km/min')


def _plot_number_speed_curve(group_dict, start_time, end_time, axs, separated=False, normalized=True):
    global edge_stats
    if edge_stats is None: edge_stats = open_pickle(address_edge_data)

    for i, (group_id, edge_list) in enumerate(group_dict.items()):
        tnvehs_group = []
        tvkpm_group = []
        tspeed = []
        tdensity = []

        for interval_id, edges_data in edge_stats.items():
            if float(interval_id) <= start_time or float(interval_id) > end_time:
                continue
            total_nvehs = 0
            total_vkpm = 0
            total_weightedspeed = 0
            total_edge_length = 0
            total_weighteddensity = 0
            no_of_edges = 0

            for edge_id in edge_list:
                if edge_id in edges_data:
                    edge_data = edges_data[edge_id]
                    Edgelength = net.getEdge(edge_id).getLength() #this is new edge length
                    speed = edge_data["speed"]
                    density = edge_data["laneDensity"]
                    sampled_seconds = edge_data["sampledSeconds"]
                    # weighted speed = speed*Edgelength
                    # Sum the weighted speed values for all the edges in the region.Sum the lengths of all the edges in the region.
                    # Divide the sum of the weighted speed values by the sum of the lengths of all the edges in the region to obtain the region's
                    if speed is not None and density is not None:
                        if float(density) > 0:
                            total_nvehs += float(sampled_seconds) / 60
                            # total_vkpm += float(speed) * float(sampled_seconds) / 1000
                            # Edgelength_previous = ((float(sampled_seconds) / 60) * 1000) / float(density)  # in m  #we were using this edge length before
                            total_weighteddensity = total_weighteddensity + (float(density)*(float(Edgelength) / 1000)) # in veh
                            total_weightedspeed = total_weightedspeed + (
                                    (float(speed) * 3600 / 1000) * (float(Edgelength) / 1000))  # in km/hr
                            total_edge_length = total_edge_length + (float(Edgelength) / 1000)  # in km
                            no_of_edges += 1
                        else:
                            Edgelength = 0  # in m
                            total_weighteddensity = total_weighteddensity  # in veh
                            total_weightedspeed = total_weightedspeed
                            total_edge_length = total_edge_length  # in km
                            no_of_edges += 1

            avg_speed = total_weightedspeed / total_edge_length  # km/hr
            avg_density = total_weighteddensity / total_edge_length  # veh/km
            tnvehs_group.append(total_nvehs)
            tvkpm_group.append(total_vkpm)
            tdensity.append(avg_density)
            tspeed.append(avg_speed)

        # Use different marker and size for each group
        marker = markers[i % len(markers)]
        size = sizes[i % len(sizes)]
        # color = colors[i % len(colors)]
        # size = sizes[i]
        if separated:
            if len(axs) >= 2:
                ax = axs[i // 2, i % 2]
            else:
                ax = axs[i % 2]
        else:
            ax = axs

        # fit a second oredr ploynomial -number vs speed
        polyfit_s_d = np.polyfit(tnvehs_group, tspeed, 3)
        polyline_s_d = np.polyval(polyfit_s_d, tnvehs_group)
        deviation_s_d = np.abs(polyline_s_d - tspeed)
        std_dev_s_d = np.std(deviation_s_d)

        # for no of veh vs veh per km ---per min
        # ax.scatter(tnvehs_group, tvkpm_group, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        # for density vs speed ---per min
        # ax.scatter(tdensity, tspeed, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        ax.scatter(tnvehs_group, tspeed, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        ax.plot(tnvehs_group, polyline_s_d, color=cmap(i), linewidth=0.6)
        # ax.plot(tdensity, polyline_s_d + std_dev_s_d, '--', color='k')
        # ax.plot(tdensity, polyline_s_d - std_dev_s_d, '--', color='k')

    _modify_appearance(axs, len(group_dict), separated, normalized,
                       xlabel='#vehs', ylabel='km/hr')


def _plot_time_number_curve(group_dict, start_time, end_time, axs, separated=False, normalized=True):
    global edge_stats
    if edge_stats is None: edge_stats = open_pickle(address_edge_data)


    for i, (group_id, edge_list) in enumerate(group_dict.items()):
        tnvehs_group = []
        tvkpm_group = []
        tspeed = []
        tdensity = []

        for interval_id, edges_data in edge_stats.items():
            if float(interval_id) <= start_time or float(interval_id) > end_time:
                continue
            total_nvehs = 0
            total_vkpm = 0
            total_weightedspeed = 0
            total_edge_length = 0
            total_weighteddensity = 0
            no_of_edges = 0

            for edge_id in edge_list:
                if edge_id in edges_data:
                    edge_data = edges_data[edge_id]
                    Edgelength = net.getEdge(edge_id).getLength() #this is new edge length
                    speed = edge_data["speed"]
                    density = edge_data["laneDensity"]
                    sampled_seconds = edge_data["sampledSeconds"]
                    # weighted speed = speed*Edgelength
                    # Sum the weighted speed values for all the edges in the region.Sum the lengths of all the edges in the region.
                    # Divide the sum of the weighted speed values by the sum of the lengths of all the edges in the region to obtain the region's
                    if speed is not None and density is not None:
                        if float(density) > 0:
                            total_nvehs += float(sampled_seconds) / 60
                            # total_vkpm += float(speed) * float(sampled_seconds) / 1000
                            # Edgelength_previous = ((float(sampled_seconds) / 60) * 1000) / float(density)  # in m  #we were using this edge length before
                            total_weighteddensity = total_weighteddensity + (float(density)*(float(Edgelength) / 1000)) # in veh
                            total_weightedspeed = total_weightedspeed + (
                                    (float(speed) * 3600 / 1000) * (float(Edgelength) / 1000))  # in km/hr
                            total_edge_length = total_edge_length + (float(Edgelength) / 1000)  # in km
                            no_of_edges += 1
                        else:
                            Edgelength = 0  # in m
                            total_weighteddensity = total_weighteddensity  # in veh
                            total_weightedspeed = total_weightedspeed
                            total_edge_length = total_edge_length  # in km
                            no_of_edges += 1

            avg_speed = total_weightedspeed / total_edge_length  # km/hr
            avg_density = total_weighteddensity / total_edge_length  # veh/km
            tnvehs_group.append(total_nvehs)
            tvkpm_group.append(total_vkpm)
            tdensity.append(avg_density)
            tspeed.append(avg_speed)

        # Use different marker and size for each group
        marker = markers[i % len(markers)]
        size = sizes[i % len(sizes)]
        # color = colors[i % len(colors)]
        # size = sizes[i]
        if separated:
            if len(axs) >= 2:
                ax = axs[i // 2, i % 2]
            else:
                ax = axs[i % 2]
        else:
            ax = axs

        # fit a second oredr ploynomial -number vs speed
        # polyfit_s_d = np.polyfit(tnvehs_group, tspeed, 2)
        polyfit_s_d = np.polyfit(range(len(tnvehs_group)), tnvehs_group, 3)
        polyline_s_d = np.polyval(polyfit_s_d, range(len(tnvehs_group)))
        deviation_s_d = np.abs(polyline_s_d - tnvehs_group)
        std_dev_s_d = np.std(deviation_s_d)

        # for no of veh vs veh per km ---per min
        # ax.scatter(tnvehs_group, tvkpm_group, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        # for density vs speed ---per min
        # ax.scatter(tdensity, tspeed, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        ax.scatter(range(len(tnvehs_group)), tnvehs_group, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        ax.plot(range(len(tnvehs_group)), polyline_s_d, color=cmap(i), linewidth=0.6)
        # ax.plot(tdensity, polyline_s_d + std_dev_s_d, '--', color='k')
        # ax.plot(tdensity, polyline_s_d - std_dev_s_d, '--', color='k')

    _modify_appearance(axs, len(group_dict), separated, normalized,
                       xlabel='time [min]', ylabel='#vehs')


def _plot_flow_density_curve(group_dict, start_time, end_time, axs, separated=False, normalized=True):
    global edge_stats
    if edge_stats is None: edge_stats = open_pickle(address_edge_data)

    for i, (group_id, edge_list) in enumerate(group_dict.items()):
        tnvehs_group = []
        tvkpm_group = []
        tspeed = []
        tdensity = []
        tflux = []

        for interval_id, edges_data in edge_stats.items():
            if float(interval_id) <= start_time or float(interval_id) > end_time:
                continue
            total_nvehs = 0
            total_vkpm = 0
            total_weightedspeed = 0
            total_edge_length = 0
            total_weighteddensity = 0
            no_of_edges = 0
            # total_flux = 0

            for edge_id in edge_list:
                if edge_id in edges_data:
                    edge_data = edges_data[edge_id]
                    speed = edge_data["speed"]
                    density = edge_data["laneDensity"]
                    sampled_seconds = edge_data["sampledSeconds"]
                    Edgelength = net.getEdge(edge_id).getLength()  # this is new edge length

                    # weighted speed = speed*Edgelength
                    # Sum the weighted speed values for all the edges in the region.Sum the lengths of all the edges in the region.
                    # Divide the sum of the weighted speed values by the sum of the lengths of all the edges in the region to obtain the region's
                    if speed is not None and density is not None:
                        if float(density) > 0:
                            total_nvehs += float(sampled_seconds) / 60
                            total_vkpm += float(speed) * float(sampled_seconds) / 1000
                            # Edgelength = ((float(sampled_seconds) / 60) * 1000) / float(density)  # in m # previous edge length
                            total_weighteddensity = total_weighteddensity + (float(density)*(float(Edgelength) / 1000)) # in veh
                            total_weightedspeed = total_weightedspeed + (
                                    (float(speed) * 3600 / 1000) * (float(Edgelength) / 1000))  # in km/hr
                            total_edge_length = total_edge_length + (float(Edgelength) / 1000)  # in km
                            # total_weightedspeed = total_weightedspeed + (float(speed) * float(Edgelength))  # in m/s
                            # total_edge_length = total_edge_length + (float(Edgelength))  # in m
                            no_of_edges += 1
                        else:
                            Edgelength = 0  # in m
                            total_weighteddensity = total_weighteddensity  # in veh/km/lane
                            total_weightedspeed = total_weightedspeed
                            total_edge_length = total_edge_length  # in km
                            no_of_edges += 1

            avg_speed = total_weightedspeed / total_edge_length  # km/hr
            # todo sometimes: ZeroDivisionError: division by zero
            avg_density = total_weighteddensity / total_edge_length  # veh/km/lane
            total_flux = avg_speed * avg_density  # veh/hr
            tnvehs_group.append(total_nvehs)
            tvkpm_group.append(total_vkpm)
            tdensity.append(avg_density)
            tspeed.append(avg_speed)
            # tflow.append(total_flow)
            tflux.append(total_flux)

        # Use different marker and size for each group
        marker = markers[i % len(markers)]
        size = sizes[i % len(sizes)]
        # color = colors[i % len(colors)]
        # size = sizes[i]
        if separated:
            if len(axs) >= 2:
                ax = axs[i // 2, i % 2]
            else:
                ax = axs[i % 2]
        else:
            ax = axs

        # fit a second oredr ploynomial -density vs flow rate
        polyfit_s_d = np.polyfit(tdensity, tflux, 2)
        polyline_s_d = np.polyval(polyfit_s_d, tdensity)
        deviation_s_d = np.abs(polyline_s_d - tflux)
        std_dev_s_d = np.std(deviation_s_d)

        x_curve = np.linspace(min(tdensity), max(tdensity)+10, 1000)
        y_curve = np.polyval(polyfit_s_d, x_curve)

        # for no of veh vs veh per km ---per min
        # ax.scatter(tnvehs_group, tvkpm_group, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        # for density vs speed ---per min
        ax.scatter(tdensity, tflux, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        ax.plot(x_curve, y_curve, color=cmap(i), linewidth=0.6)
        # ax.plot(tdensity, polyline_s_d + std_dev_s_d, '--', color='k')
        # ax.plot(tdensity, polyline_s_d - std_dev_s_d, '--', color='k')
    _modify_appearance(axs, len(group_dict), separated, normalized,
                           xlabel='veh/km/lane', ylabel='veh/hr')


def get_top_links(region_edges, edges_data, percent=85):
    global over4priorities
    if over4priorities is None: over4priorities = open_over4_priorities(address_over4priorities)
    candidates = {}
    for edge_id in region_edges:
        # if (edge_id in edges_data) and (edge_id in over4priorities):
        if (edge_id in edges_data):
            edge_data = edges_data[edge_id]
            speed = edge_data["speed"]
            density = edge_data["laneDensity"]
            sampled_seconds = edge_data["sampledSeconds"]
            if speed is not None and density is not None:
                if float(density) > 0:
                    candidates[edge_id] = float(density)
    sorted_candidates = sorted(candidates.items(), key=lambda x:x[1], reverse=True)
    return list(dict(sorted_candidates[:int(percent/100 * len(sorted_candidates))]).keys())


def _plot_number_production_theoretical_curve(group_dict, start_time, end_time, axs,
                                              separated=False, normalized=True, show_deviation=False):
    global edge_stats
    if edge_stats is None: edge_stats = open_pickle(address_edge_data)

    group_dict = group_dict[0]
    fit_lines = dict()
    for i, (group_id, edge_list) in enumerate(group_dict.items()):
        tnvehs_group = []
        productions = []

        for interval_id, edges_data in edge_stats.items():
            if float(interval_id) <= start_time or float(interval_id) > end_time:
                continue
            total_nvehs = 0
            total_weightedspeed = 0
            no_of_edges = 0

            for edge_id in get_top_links(edge_list, edges_data, percent=80):
                edge_data = edges_data[edge_id]
                speed = edge_data["speed"]
                sampled_seconds = edge_data["sampledSeconds"]
                nvehs = float(sampled_seconds) / 60
                s = (float(speed) * 3.6)
                # print(edge_id + "  speed: " + str(s))
                # if s == 0:
                # if s <0.5:
                #     # print(edge_id + "  speed: " + str(s))
                #     # s = 0.01
                #     continue
                total_nvehs += nvehs
                total_weightedspeed += s * nvehs
                no_of_edges += 1

            if total_nvehs == 0:
                print(f'No vehicles at f{interval_id} for region:{group_id}')
            else:
                avg_speed = total_weightedspeed/total_nvehs
                prod = avg_speed * total_nvehs
                tnvehs_group.append(total_nvehs)
                productions.append(prod)

        # Use different marker and size for each group
        ax, marker, size, color = _get_figure_config(i, axs, separated)

        # fit a 3rd order ploynomial -number vs. production
        # polyfit_s_d = np.polyfit(tnvehs_group, productions, 3)
        polyfit_s_d = _fit_line(tnvehs_group, productions, 3, with_intercept=False)
        fit_lines[group_id] = polyfit_s_d

        _draw_plot(tnvehs_group, productions, polyfit_s_d, extrapolation=50, show_deviation=show_deviation, ax=ax,
                   label=f"Region {group_id}", marker=marker, size=size, color=color)

    _modify_appearance(axs, len(group_dict), separated, normalized, xlabel='vehicles', ylabel='veh-km/hr')
    return fit_lines


def _plot_density_production_curve(group_dict, start_time, end_time, axs,
                              separated=False, normalized=True, show_deviation=False):
    global edge_stats
    if edge_stats is None: edge_stats = open_pickle(address_edge_data)

    for i, (group_id, edge_list) in enumerate(group_dict.items()):
        tdensity = []
        productions = []

        for interval_id, edges_data in edge_stats.items():
            if float(interval_id) <= start_time or float(interval_id) > end_time:
                continue
            total_nvehs = 0
            total_weightedspeed = 0
            no_of_edges = 0
            total_lane_kms = 0

            valid_links = get_top_links(edge_list, edges_data, percent=100)  # all links with real speed and density
            for edge_id in valid_links:
                edge_data = edges_data[edge_id]
                sampled_seconds = edge_data["sampledSeconds"]
                nvehs = float(sampled_seconds) / 60
                total_nvehs += nvehs

                speed = edge_data["speed"]
                s = (float(speed) * 3.6)
                total_weightedspeed += s * nvehs

                laneDensity = float(edge_data["laneDensity"])
                # try:
                density = float(edge_data["density"])
                # except KeyError as e:
                #     print(e)
                #     density = laneDensity
                nlanes = round(density/laneDensity)   # TODO it also includes pedestrian lanes
                Edgelength = float(net.getEdge(edge_id).getLength()/1000)
                total_lane_kms += nlanes * Edgelength

                no_of_edges += 1

            if total_nvehs == 0:
                print(f'No vehicles at f{interval_id} for region:{group_id}')
            else:
                avg_density = total_nvehs / total_lane_kms  # veh/km
                tdensity.append(avg_density)
                avg_speed = total_weightedspeed / total_nvehs
                prod = avg_speed * total_nvehs
                productions.append(prod)

        # Use different marker and size for each group
        ax, marker, size, color = _get_figure_config(i, axs, separated)

        # fit a second oredr ploynomial -density vs speed
        polyfit_s_d = np.polyfit(tdensity, productions, 3)
        _draw_plot(tdensity, productions, polyfit_s_d, extrapolation=15, show_deviation=show_deviation, ax=ax,
                   label=f"Region {group_id}", marker=marker, size=size, color=color)
    _modify_appearance(axs, len(group_dict), separated, normalized, xlabel='veh/km/lane', ylabel='veh-km/hr')


def _plot_speed_density_curve(group_dict, start_time, end_time, axs,
                              separated=False, normalized=True, show_deviation=True):
    global edge_stats
    if edge_stats is None: edge_stats = open_pickle(address_edge_data)

    for i, (group_id, edge_list) in enumerate(group_dict.items()):
        tspeed = []
        tdensity = []

        for interval_id, edges_data in edge_stats.items():
            if float(interval_id) <= start_time or float(interval_id) > end_time:
                continue
            total_nvehs = 0
            total_weightedspeed = 0
            no_of_edges = 0
            total_lane_kms = 0

            valid_links = get_top_links(edge_list, edges_data, percent=100)  # all links with real speed and density
            for edge_id in valid_links:
                edge_data = edges_data[edge_id]
                sampled_seconds = edge_data["sampledSeconds"]
                nvehs = float(sampled_seconds) / 60
                total_nvehs += nvehs

                speed = edge_data["speed"]
                s = (float(speed) * 3.6)
                total_weightedspeed += s * nvehs

                laneDensity = float(edge_data["laneDensity"])
                # try:
                density = float(edge_data["density"])
                # except KeyError as e:
                #     print(e)
                #     density = laneDensity
                nlanes = round(density/laneDensity)   # TODO it also includes pedestrian lanes
                Edgelength = float(net.getEdge(edge_id).getLength()/1000)
                total_lane_kms += nlanes * Edgelength

                no_of_edges += 1

            if total_nvehs == 0:
                print(f'No vehicles at f{interval_id} for region:{group_id}')
            else:
                avg_speed = total_weightedspeed / total_nvehs
                avg_density = total_nvehs / total_lane_kms  # veh/km
                tdensity.append(avg_density)
                tspeed.append(avg_speed)

        # Use different marker and size for each group
        ax, marker, size, color = _get_figure_config(i, axs, separated)

        # fit a second oredr ploynomial -density vs speed
        polyfit_s_d = np.polyfit(tdensity, tspeed, 3)

        _draw_plot(tdensity, tspeed, polyfit_s_d, extrapolation=10, show_deviation=show_deviation, ax=ax,
                   label=f"Region {group_id}", marker=marker, size=size, color=color)

    _modify_appearance(axs, len(group_dict), separated, normalized, xlabel='veh/km/lane', ylabel='km/hr')



def _plot_mfd_type1(group_dict, start_time, end_time, axs, separated=False, normalized=True):
    global edge_stats
    if edge_stats is None: edge_stats = open_pickle(address_edge_data)

    for i, (group_id, edge_list) in enumerate(group_dict.items()):
        tnvehs_group = []
        tvkpm_group = []
        tspeed = []
        tdensity = []
        tflux = []

        for interval_id, edges_data in edge_stats.items():
            if float(interval_id) <= start_time or float(interval_id) > end_time:
                continue
            total_nvehs = 0
            total_vkpm = 0
            total_weightedspeed = 0
            total_edge_length = 0
            total_weighteddensity = 0
            no_of_edges = 0
            # total_flux = 0

            for edge_id in edge_list:
                if edge_id in edges_data:
                    edge_data = edges_data[edge_id]
                    speed = edge_data["speed"]
                    density = edge_data["laneDensity"]
                    sampled_seconds = edge_data["sampledSeconds"]
                    Edgelength = net.getEdge(edge_id).getLength()  # this is new edge length
                    # weighted speed = speed*Edgelength
                    # Sum the weighted speed values for all the edges in the region.Sum the lengths of all the edges in the region.
                    # Divide the sum of the weighted speed values by the sum of the lengths of all the edges in the region to obtain the region's
                    if speed is not None and density is not None:
                        if float(density) > 0:
                            total_nvehs += float(sampled_seconds) / 60
                            total_vkpm += float(speed) * float(sampled_seconds) / 1000
                            # Edgelength = ((float(sampled_seconds) / 60) * 1000) / float(density)  # in m # previous edge length
                            total_weighteddensity = total_weighteddensity + (float(density)*(float(Edgelength) / 1000)) # in veh
                            total_weightedspeed = total_weightedspeed + (
                                    (float(speed) * 3600 / 1000) * (float(Edgelength) / 1000))  # in km/hr
                            total_edge_length = total_edge_length + (float(Edgelength)/1000)  # in km
                            # total_weightedspeed = total_weightedspeed + (float(speed) * float(Edgelength))  # in m/s
                            # total_edge_length = total_edge_length + (float(Edgelength))  # in m
                            no_of_edges += 1
                        else:
                            Edgelength = 0  # in m
                            total_weighteddensity = total_weighteddensity  # in veh/km/lane
                            total_weightedspeed = total_weightedspeed
                            total_edge_length = total_edge_length  # in km
                            no_of_edges += 1

            avg_speed = total_weightedspeed / total_edge_length  # km/hr
            avg_density = total_weighteddensity / total_edge_length  # veh/km
            total_flux = avg_speed * avg_density  # veh/hr #flow rate
            tnvehs_group.append(total_nvehs) # no of vehs
            tvkpm_group.append(total_vkpm)
            tdensity.append(avg_density)
            tspeed.append(avg_speed)
            # tflow.append(total_flow)
            tflux.append(total_flux)

        # Use different marker and size for each group
        marker = markers[i % len(markers)]
        size = sizes[i % len(sizes)]
        # color = colors[i % len(colors)]
        # size = sizes[i]
        if separated:
            if len(axs) >= 2:
                ax = axs[i // 2, i % 2]
            else:
                ax = axs[i % 2]
        else:
            ax = axs

        # fit a second oredr ploynomial -density vs flow rate
        polyfit_s_d = np.polyfit(tnvehs_group, tflux, 2)
        polyline_s_d = np.polyval(polyfit_s_d, tnvehs_group)
        deviation_s_d = np.abs(polyline_s_d - tflux)
        std_dev_s_d = np.std(deviation_s_d)

        # for no of veh vs veh per km ---per min
        # ax.scatter(tnvehs_group, tvkpm_group, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        # for density vs speed ---per min
        ax.scatter(tnvehs_group, tflux, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        ax.plot(tnvehs_group, polyline_s_d, color=cmap(i), linewidth=0.6)
        # ax.plot(tnvehs_group, polyline_s_d + std_dev_s_d, '--', color=cmap(i))
        # ax.plot(tnvehs_group, polyline_s_d - std_dev_s_d, '--', color=cmap(i))

    _modify_appearance(axs, len(group_dict), separated, normalized,
                       xlabel='No of vehicles (n)', ylabel='Aggregated Flow Rate (q) - veh/hr')


def _plot_number_production_curve(data, start_time, end_time, axs, separated=False, normalized=True):
    """
    :param data: it's (group_dict, seg_boundary_dict)
    seg_dict = {segment_id: edge_IDs included}
    seg_boundary_dict = {seg id: {boundary edge id: {neighbors of that edge: seg_id for each neighbor}}

    :param start_time:
    :param end_time:
    :param axs:
    :param separated:
    :param normalized:
    :return:

    OBJECTIVES:
        for each region:
            for each minute:
                find number of all vehicles inside
                find production rate (number of vehicles going out of the region)
            draw a (number,production) point

    PROCEDURE:
        for each region
            for minute, edge_vehicle_dict in edge_vehicle_stats:
                production = set()
                total_vehicles = set()
                for edge in region:
                    total vehicles.add(unseen edge_vehicle_dict[edge])
                    if edge in boundaries_of_region:
                        production.add(trips/vehicle IDs going from segment TO its neighbor)
    """

    global edge_vehicle_stats, vehicle_arrival_stats
    if edge_vehicle_stats is None: edge_vehicle_stats = open_pickle(address_edge_vehicles)
    if vehicle_arrival_stats is None: vehicle_arrival_stats = open_pickle(address_vehicle_arrival_data)

    seg_dict = data[0]
    seg_boundary_dict = data[1]

    for i, (group_id, segment_edges) in enumerate(seg_dict.items()):  # for each region
        tnvehs_segment = []
        tproduction_segment = []
        arrived = 0  # debug

        for interval_id, edges_data in edge_vehicle_stats.items():  # for each minute
            if float(interval_id)*60-60+18000 < start_time or float(interval_id)*60+18000 > end_time:
                continue
            total_production = list()

            # # finding out the production of the edge
            for edge_id in segment_edges:
                if edge_id in edges_data.keys():  # if vehicles have been existed on this edge in this time interval
                    edge_vehicles = edges_data[edge_id]  # vehicles that traveled in this edge in this time interval
                    edge_production = list()  # edge_outgoing_vehicles

                    # # adding the trips being ended here in this edge in this minute
                    if vehicle_arrival_stats.get(edge_id) is not None:
                        for veh in vehicle_arrival_stats[edge_id]:
                            if veh in edge_vehicles:
                                # print(f'{veh} is arrived and included in production')
                                edge_production.append(veh)
                                arrived += 1

                    # can we have duplicates between here and vehicles going out of region?

                    if edge_id in seg_boundary_dict[group_id].keys():  # if this edge is a boundary link
                        neighbors = seg_boundary_dict[group_id].get(edge_id)  # contains dict of neighbors and seg_IDs
                        outgoing_neighbors = [e.getID() for e in net.getEdge(edge_id).getOutgoing().keys()]

                        # finding the outgoing neighbors into other regions and save the trips they were involved in
                        outgoing_trips = list()
                        for neighbor in outgoing_neighbors:
                            if neighbors.get(neighbor) is not None:  # if the neighbor is not a minor/deleted street
                                neighbor_seg = neighbors[neighbor]
                                if neighbor_seg != group_id:  # if the neighbor is in another region
                                    if edges_data.get(neighbor) is not None:
                                        outgoing_trips.extend(edges_data[neighbor])
                        outgoing_trips = set(outgoing_trips)

                        # finding the trips that involved both our boundary link and a link in a neighbor region
                        for trip in edge_vehicles:
                            if trip in outgoing_trips:
                                edge_production.append(trip)
                        total_production.extend(edge_production)
            ###########################
            tnvehs_segment.append(_get_continuous_tnvehs(interval_id, segment_edges))
            # tproduction_segment.append(len(total_production)/60.0)
            tproduction_segment.append(len(total_production))
            # todo double check the units - production should be veh/s right?

        # print(f'arrived vehicles in segment {group_id} = {arrived}')

        # Use different marker and size for each group
        marker = markers[i % len(markers)]
        size = sizes[i % len(sizes)]
        if separated:
            if len(axs) >= 2:
                ax = axs[i // 2, i % 2]
            else:
                ax = axs[i % 2]
        else:
            ax = axs

        # fit a polynomial -number of vehicles vs. production rate
        polyfit_s_d = np.polyfit(tnvehs_segment, tproduction_segment, 3)  # third order
        x_curve = np.linspace(min(tnvehs_segment), max(tnvehs_segment)+10, 1000)
        y_curve = np.polyval(polyfit_s_d, x_curve)
        ax.scatter(tnvehs_segment, tproduction_segment, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        ax.plot(x_curve, y_curve, color=cmap(i), linewidth=0.6)
        # ax.plot(tdensity, polyline_s_d + std_dev_s_d, '--', color='k')
        # ax.plot(tdensity, polyline_s_d - std_dev_s_d, '--', color='k')

    _modify_appearance(axs, len(seg_dict), separated, normalized,
                       xlabel='# of vehicles', ylabel='production rate - veh/min')


def _get_continuous_tnvehs(interval, edge_list):
    global edge_stats
    if edge_stats is None: edge_stats = open_pickle(address_edge_data)
    # import pdb
    # pdb.set_trace()
    interval = (int(interval)-1)*60+18000
    edges_data = edge_stats[str(interval)+'.00']
    total_nvehs = 0

    for edge_id in edge_list:
        if edge_id in edges_data:
            edge_data = edges_data[edge_id]
            speed = edge_data["speed"]
            density = edge_data["laneDensity"]
            sampled_seconds = edge_data["sampledSeconds"]
            if speed is not None and density is not None:
                edge_nvehs = float(sampled_seconds) / 60
                total_nvehs += edge_nvehs
    return total_nvehs






