import xml.etree.ElementTree as ET
from matplotlib import pyplot as plt
import numpy as np
import pickle
import io_handler as io

# codes for creating .pickle files are transferred into pickle_creator.py
# address_edge_data = "Data/uniques_interval_data.pickle" this is the older simulation
# address_edge_data = "Data/uniques_interval_data_new.pickle"  this is the old simulation!
# address_edge_vehicles = "data/edge_vehicle_output_min_old.pickle" # for the old simulation
address_edge_data = "Data/edge_data_output_min.pickle"
address_vehicle_arrival_data = "Data/edge_arrived_vehicle_output_min.pickle"
address_edge_vehicles = "data/edge_vehicle_output_min.pickle"

input_addresses = "config files/config.yaml"
net, _, _, _, _ = io.get_network(input_addresses)

edge_stats = None  # it contains edge_data output
edge_vehicle_stats = None  # it contains my traci output. shows the vehicles included in each link in each minute
vehicle_arrival_stats = None

# Define markers and colors for each group
markers = ["*", "s", "^", "D", "x", "+", "o", "^"]
sizes = [3, 3, 3, 3, 3, 3]
cmap = plt.cm.tab10  # Define the colormap


def open_pickle(address: str):
    with open(address, "rb") as f:
        file = pickle.load(f)
        f.close()
    return file


def MFD_plotter(group_dict, start_time, end_time, separated=False, normalized=True,
                mfd=False, mfd1=False, speed_vs_den=False, flow_vs_den=False, num_vs_prod=False):
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
        _plot_number_production_curve(group_dict, start_time, end_time, axs=axs, separated=separated, normalized=normalized)
    plt.show()


def MFD_plotter_combined(segment_ids, MFD_start_time, MFD_end_time):
    # todo it's not complete and not working

    # fig, axs = plt.subplots(2, 3, figsize=(24, 4))
    # fig.subplots_adjust(left=0.05, right=0.955, wspace=0.4, hspace=0.25, bottom=0.14, top=0.85)
    # fig, axs = plt.subplots(1, 4, figsize=(28, 6))

    # MFD.plot_speed_density_curve(segment_ids, MFD_start_time, MFD_end_time, ax=axs[1, 0])

    fig, axs = plt.subplots(2, 2, figsize=(12, 9))

    fig.subplots_adjust(left=0.05, right=0.955, wspace=0.4, hspace=0.3, bottom=0.14, top=0.85)
    # plt.subplots_adjust(wspace=0.4)


    _plot_mfd_type1(segment_ids, MFD_start_time, MFD_end_time, ax=axs[0, 1])
    axs[0, 0].set_title('MFD type 1', fontsize=14, color="blue", fontweight='bold')

    _plot_mfd(segment_ids, MFD_start_time, MFD_end_time, ax=axs[0, 2])
    axs[0, 1].set_title('MFD type 2', fontsize=14, color="blue", fontweight='bold')

    _plot_speed_density_curve(segment_ids, MFD_start_time, MFD_end_time, ax=axs[1, 0])
    axs[1, 0].set_title('Density - Speed', fontsize=14, color="blue", fontweight='bold')

    _plot_flow_density_curve(segment_ids, MFD_start_time, MFD_end_time, ax=axs[1, 1])
    axs[1, 1].set_title('Density - Flow', fontsize=14, color="blue", fontweight='bold')

    plt.show()


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


def _get_total_nvehs(minute: int, edge_list: list):
    '''
    Not used. number of vehicles should be continuous and not discrete. Should be removed actually
    :param minute:
    :param edge_list:
    :return:
    '''
    global edge_vehicle_stats
    if edge_vehicle_stats is None: edge_vehicle_stats = open_pickle(address_edge_vehicles)

    data = edge_vehicle_stats[(str(minute))]

    vehicles = set()
    for edge in edge_list:
        if data.get(edge) is not None:
            edge_vehicles = data[edge]
            vehicles.update(edge_vehicles)

    return len(vehicles)


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


def _plot_speed_density_curve(group_dict, start_time, end_time, axs, separated=False, normalized=True):
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
                            # total_nvehs += float(sampled_seconds) / 60
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

        # fit a second oredr ploynomial -density vs speed
        polyfit_s_d = np.polyfit(tdensity, tspeed, 2)
        polyline_s_d = np.polyval(polyfit_s_d, tdensity)
        deviation_s_d = np.abs(polyline_s_d - tspeed)
        std_dev_s_d = np.std(deviation_s_d)

        # for no of veh vs veh per km ---per min
        # ax.scatter(tnvehs_group, tvkpm_group, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        # for density vs speed ---per min
        ax.scatter(tdensity, tspeed, label=f"Region {group_id}", marker=marker, s=size, color=cmap(i))
        ax.plot(tdensity, polyline_s_d, color=cmap(i),linewidth=0.6)
        # ax.plot(tdensity, polyline_s_d + std_dev_s_d, '--', color='k')
        # ax.plot(tdensity, polyline_s_d - std_dev_s_d, '--', color='k')

    _modify_appearance(axs, len(group_dict), separated, normalized,
                       xlabel='veh/km/lane', ylabel='km/hr')


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






