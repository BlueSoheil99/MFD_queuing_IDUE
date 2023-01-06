import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt


# Parse the XML file
tree = ET.parse('../Data/Edgetest_6_0411_2_0.xml')
root = tree.getroot()

def plot_mfd(edge_id):

    # Select the edge of interest
    # edge_id = ['-171739214#4', '-105493444#4']
    #### enter here the list of selected edges for each region ## have to ask Soheil for list

    # Initialize empty lists to store density and speed data for the edge
    densities = []
    speeds = []

    # Iterate through the timestep elements
    for interval in root:
        # Find the edge element for the selected edge
        for edge in edge_id:
            edge_elem = interval.find("./edge[@id='" + edge+ "']")
            if edge_elem is not None:
                # Extract the density and speed data for the edge
                density = float(edge_elem.get('density'))
                speed = float(edge_elem.get('speed'))
                # Append the density and speed data to the appropriate lists
                densities.append(density)
                speeds.append(speed)
            ##speed as k for unit km/hr or mph from Yiran

    # Plot the MFD
    plt.scatter(densities,speeds)
    plt.xlabel('Density')
    plt.ylabel('Speed')
    plt.show()

# flow v/s speed --check
# edge_id = ['-171739214#4', '-105493444#4']
# plot_mfd(edge_id)