import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import sumolib


# Parse the XML file
tree = ET.parse('Data/Edgetest_6_0411_2_0.xml')
root = tree.getroot()
net = sumolib.net.readNet('data/Seattle_road_network.net.xml')


# function to retrieve length for edges (input in function) from network file
# def getlength(edge_net):
#     edges = net.getEdges()
#     for edge_net in edges:
#         length = edge_net.getLength()
#     return length


# function to get list of edge id from network input file for all of network with density and removing those without density
def private_getedgeids(root):
    # initialize a dictionary to store edge ids
    edgeid = {}
    # iterate through all edges in the file
    for edge in root.iter("edge"):
        # extract the edge ID and length
        edge_id = edge.attrib["id"]
        # condition check if density exists
        # add the edge id to the dictionary
        edgeid[edge_id] = edge_id
    return edgeid


def private_plot_mfd(edge_id, start_time, end_time):
   # Initialize empty lists to store density and speed data for the edge
    global density, speed, flow
    densities = []
    speeds = []
    flows = []

    ##check number of edges less than 0 for speed alone...plot network .. to see if connected-- connectivity chevk function
    ### list of edges sith speed less than 0 or 0

    # Iterate through the timestep elements
    # for interval in edge_stats:
    #     if interval_begin * 3600 <= float(interval.begin) < interval_end * 3600:
    # for interval in root:
    #     # Find the edge element for the selected edge

    for interval in root.findall('interval'):
        begin = float(interval.get('begin'))
        end = float(interval.get('end'))

        if begin >= start_time and end <= end_time:
            for edge in edge_id:
                edge_elem = interval.find(".//edge[@id='" + edge + "']")
                # edge_elem = edge
                if edge_elem is not None:
                    # length = getlength(edge_elem)
                    # Extract the density and speed data for the edge
                    speed_raw = edge_elem.get('speed')
                    density_raw = edge_elem.get('laneDensity')
                    # begin and end time --  num of veh---- # check with Yiran calculate flow
                    # send Yiran the edges with higher flow and then higher flow and higher density
                    # no of vehicles

                    if density_raw is not None and float(density_raw) > 0 and speed_raw is not None and float(
                            speed_raw) > 0:
                        density = float(density_raw)
                        speed = float(speed_raw)
                        flow = float(
                            density * speed * 3.6)  # not sure if we need to multiply length as well (length*0.001)
                        if float(flow) > 1000:
                            print(f"{edge} have flow {flow}")
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
                        densities.append(density)
                        speeds.append(speed)
                        flows.append(flow)
                if edge_elem is None:
                    print(f"edge {edge} does not exist in the edgetest file")
        # speed as m/sec

    # Plot the MFD
    plt.scatter(densities, flows, s=8, c='b', alpha=0.5)
    plt.xlabel('Density')
    plt.ylabel('Flow')
    plt.title("Macroscopic Fundamental Diagram")
    plt.show()


def plot_mfd(segment_IDs, start_time, end_time):
    for i in range(len(segment_IDs)):
        edge_list = segment_IDs[i]
        print(f"plot for the edges in {i} group ")
        # print(edge_list) debug
        private_plot_mfd(edge_list, start_time*3600, end_time*3600)
