import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt

# Parse the XML file
tree = ET.parse('../Data/Edgetest_6_0411_2_0.xml')
root = tree.getroot()

# Select the edge of interest
edge_id = '-105821359#3' #### enter here the list of selected edges for each region ## have to ask Soheil for list

# Initialize empty lists to store density and speed data for the edge
densities = []
speeds = []

# Iterate through the timestep elements
for interval in root:
    # Find the edge element for the selected edge
    edge_elem = interval.find("./edge[@id='" + edge_id + "']")
    if edge_elem is not None:
        # Extract the density and speed data for the edge
        density = float(edge_elem.get('density'))
        speed = float(edge_elem.get('speed'))
        # Append the density and speed data to the appropriate lists
        densities.append(density)
        speeds.append(speed)

# Plot the MFD
plt.scatter(densities,speeds)
plt.xlabel('Density')
plt.ylabel('Speed')
plt.show()