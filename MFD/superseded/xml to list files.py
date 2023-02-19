import xml.etree.ElementTree as ET

# parse the XML file
tree = ET.parse('../../Data/edge_data_output._1min_interval.xml')
root = tree.getroot()

# loop through each interval in the XML and store the edge ids and densities in a list of tuples

for interval in root.findall('interval'):
    begin = float(interval.get('begin'))
    end = float(interval.get('end'))
    if begin >= 18000.00 and end <= 36000.00:
        interval_data = []
        for edge in interval.iter('edge'):
            edge_id = edge.get('id')
            if edge_id is not None:
                sampled_seconds = edge.get('sampledSeconds')
                laneDensity = edge.get('laneDensity')
                speed = edge.get('speed')
                interval_data.append((edge_id, sampled_seconds, laneDensity, speed))
        # write the interval data to a file with the name "interval_<id>.txt"
        with open(f"interval_{interval.get('begin')}.txt", "w") as f:
            for edge_data in interval_data:
                f.write(f"{edge_data[0]},{edge_data[1]},{edge_data[2]},{edge_data[3]}\n")
