import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import sumolib


# Parse the XML file
tree = ET.parse('Data/edge_data_output._1min_interval.xml')
root = tree.getroot()
net = sumolib.net.readNet('data/Seattle_road_network.net.xml')


# function to retrieve length for edges (input in function) from network file
# def getlength(edge_net):
#     edges = net.getEdges()
#     for edge_net in edges:
#         length = edge_net.getLength()
#     return length


# # function to get list of edge id from network input file for all of network with density and removing those without density
# def private_getedgeids(root):
#     # initialize a dictionary to store edge ids
#     edgeid = {}
#     # iterate through all edges in the file
#     for edge in root.iter("edge"):
#         # extract the edge ID and length
#         edge_id = edge.attrib["id"]
#         # condition check if density exists
#         # add the edge id to the dictionary
#         edgeid[edge_id] = edge_id
#     return edgeid



def private_plot_mfd(edge_id, start_time, end_time):
    # Select the edge of interest
    # edge_id = ['-171739214#4', '-105493444#4']
    #### enter here the list of selected edges for each region ## have to ask Soheil for list

    # Initialize empty lists to store density and speed data for the edge
    global density, speed, flow, length, no_veh, veh_km_per_min, veh_km_per_hr, time, tnvehs, total_vkpm, total_nvehs
    densities = []
    speeds = []
    flows = []
    lengths = []
    nvehs = []
    vkpm = []

    ##check number of edges less than 0 for speed alone...plot network .. to see if connected-- connectivity chevk function
    ### list of edges sith speed less than 0 or 0

    # Iterate through the timestep elements
    # for interval in edge_stats:
    #     if interval_begin * 3600 <= float(interval.begin) < interval_end * 3600:
    # for interval in root:
    #     # Find the edge element for the selected edge
    tnvehs = []
    tvkpm = []

    for interval in root.findall('interval'):
        begin = float(interval.get('begin'))
        end = float(interval.get('end'))
        step = 60
        total_nvehs = 0
        total_vkpm = 0

        # for time in range(begin, end, step):
        if begin >= start_time and end <= end_time:

            for edge in edge_id:
                edge_elem = interval.find(".//edge[@id='" + edge + "']")
                # edge_elem = edge
                if edge_elem is not None:
                    # length = getlength(edge_elem)
                    # Extract the density and speed data for the edge
                    speed_raw = edge_elem.get('speed')  # m/sec
                    density_raw = edge_elem.get('laneDensity')  # veh/km
                    sample_sec_raw = edge_elem.get('sampledSeconds')  # sec

                    # begin and end time --  num of veh---- # check with Yiran calculate flow
                    # send Yiran the edges with higher flow and then higher flow and higher density
                    # no of vehicles
                    # total_nvehs = total_nvehs+int(edge_elem.get("entered"))
                    # total_vkpm =  total_vkpm+ (float(edge_elem.get("speed"))*float(edge_elem.get("sampledSeconds")))

                    if speed_raw is not None and float(
                            speed_raw) > 0:
                        total_nvehs = total_nvehs + (float(sample_sec_raw)/60)
                        total_vkpm = total_vkpm + (float(speed_raw) * float(sample_sec_raw)/1000)
                        # density = float(density_raw)
                        # speed = float(speed_raw)
                        # ss = float(sample_sec_raw)
                        # period = float(end - begin)  # sec
                        # length = float(((ss / period) * 1000) / density)  # in metre  #veh sec / sec *veh/km
                        # flow = float(
                        #     density * speed * 3.6)  # not sure if we need to multiply length as well (length*0.001)
                        # no_veh = float(ss / period)  # no of veh
                        # veh_km_per_min = float(
                        #     speed * ss / period) * 0.06  # veh/km *  m/se * m *1/1000 * 60/1000 veh km per min
                        # veh_km_per_hr = float(speed * ss / period) *3.6  # veh-km/hr
                        # print(period)
                        # if float(flow) > 1000:
                        #     print(f"{edge} have flow {flow}")
                        # if flow >4000:
                        #     print(f"{edge} have flow {flow} ")
                        # else:
                        #     #     if density_raw is None or float(density_raw) <= 0:
                        #     #         print(f"Invalid density value {density_raw} for edge {edge_id}")
                        #     # if speed_raw is None or float(speed_raw) <= 0:
                        #     #     print(f"Invalid speed value {speed_raw} for edge {edge}")
                        #     if density_raw is not None and float(density_raw) > 750:
                        #         print(f"{edge_elem} have density {density_raw}")

                        # Append the density and speed data to the appropriate lists
                        # densities.append(density)
                        # speeds.append(speed)
                        # flows.append(flow)
                        # nvehs.append(no_veh)
                        # vkpm.append(veh_km_per_min)
                        # total_nvehs = total_nvehs + no_veh
                        # total_vkpm = total_vkpm + veh_km_per_min
                if edge_elem is None:
                    print(f"edge {edge} does not exist in the edgetest file")

            ##speed as m/sec
            # lanedensity as veh/km/la
            #
            tnvehs.append(total_nvehs)
            tvkpm.append(total_vkpm)
            # total_densities = sum(densities)
            # total_speed = sum(speeds)
            # total_flows = sum(flows)
            # total_nvehs = sum(nvehs)
            # total_vkpm = sum(vkpm)

    # Plot the MFD

    # markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd']
    # # plt.scatter(total_vehicles, total_vehicle_km, marker=markers[i % len(markers)], s=100)
    # plt.scatter(tnvehs, tvkpm, s=8, c='b', alpha=0.5)
    # plt.xlim(left=0)
    # plt.ylim(bottom=0)
    # plt.xlabel('No. of vehicles')
    # plt.ylabel('veh-km/min')
    # plt.title("Macroscopic Fundamental Diagram")
    #
    # plt.show()
    return tnvehs, tvkpm

def plot_mfd(segment_IDs, start_time, end_time):
    markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd']
    for i in range(len(segment_IDs)):
        edge_list = segment_IDs[i]
        print(f"plot for the edges in {i} group ")
        start_time = 21600
        end_time = 36000
        print(edge_list)
        tnvehs, tvkpm = private_plot_mfd(edge_list, start_time, end_time)
        plt.scatter(tnvehs, tvkpm, marker=markers[i % len(markers)], s=15)
        # plt.scatter(tnvehs, tvkpm, s=8, c='b', alpha=0.5)
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.xlabel('No. of vehicles')
    plt.ylabel('veh-km/min')
    plt.title("Macroscopic Fundamental Diagram")
    plt.show()

