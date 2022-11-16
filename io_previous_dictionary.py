
#Hey Pranati!

# I suggest that you make a new directory (name can be io) and make other .py files related to this file.
# Also you can have a .txt file in that folder to save the address of input files. You can hardcode the addresses or
# input file names for now but we'll have to make it cleaner later
import csv
import xmltodict
import pandas as pd


def get_network(network_file, density_file):
    # your code here
    x=0

    ### retrieving density from sumo output here :
    with open(density_file, 'r') as file:
        filedata = file.read()
    # Converting xml to python dictionary (ordered dict)
    data_dict = xmltodict.parse(filedata)
    column_head = ['@id', '@sampledSeconds', '@traveltime', '@overlapTraveltime', '@density', '@laneDensity',
                   '@occupancy', '@waitingTime', '@speed', '@departed', '@arrived', '@entered', '@left',
                   '@laneChangedFrom', '@laneChangedTo', '@vaporized']

    for i in range(len(data_dict['meandata']['interval'])):
        data = data_dict['meandata']['interval'][i]
        df = pd.DataFrame(data)
        print(df.head())
        col = df.iloc[:, 3]
        a = pd.DataFrame(col)
        print(a)
        time_from = df.iloc[1, 0]
        time_to = df.iloc[1, 1]
        filename = 'Result_Network/density_interval from %s to %s.csv' % (time_from, time_to)
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=column_head)
            writer.writeheader()
            writer.writerows(col)

    #retrieving network data from sumo here:
    with open(network_file, 'r') as file:
        filedata = file.read()
    # Converting xml to python dictionary (ordered dict)
    data_dict = xmltodict.parse(filedata)
    key_list = list(data_dict.keys())
    val_list = list(data_dict.values())
    # print(key_list)
    # print(val_list)

    # print(data_dict['net']['edge'])
    column_head_edge = ['@id', '@function', 'lane']
    column_head_lane_config = ['@id', '@index', '@disallow', '@speed', '@length', '@shape']
    d = data_dict['net']['edge']
    a = pd.DataFrame(d)
    print(a.head())
    a.to_csv("Result_Network/network.csv", index=False)

    # #access to each edge
    for i in range(len(data_dict['net']['edge'])):
        data = data_dict['net']['edge'][i] ## each edge
        # df_lane = pd.DataFrame(data)
        # print(df_lane.head())
        # df_lane.to_csv("Result_Network/for edge %s.csv" % (i), index=False) # donot use




    # return list_of_densities, adjacency_matrix
    # return matrix with numpy array. That should be more efficient


# def show_network(list_of_segment):
    # plot the network with each segment defined with a color
    # the input is list with len=|V| each element shows the seg# for each link
    # ex: we have 4 segments, the list would be like: [1, 1, 1, 2, 2, 3, 4, 4, 3, 1 ,...]

address_to_density = "Data/Edge_veh_od_psrc_convert20per.xml"
address_to_network = "Data/Seattle_road_network_net.xml"
# get_network(filename=address_to_density_data)
get_network(network_file=address_to_network, density_file=address_to_density)