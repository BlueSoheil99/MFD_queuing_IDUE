import pandas as pd
import pdb

def _get_green_allocation_ratio(link_obj, lane_id, signal_df):
    TLS = link_obj.getTLS()
    if TLS is None:
        return 1

    DEFAULT_g_over_C = 0.7 # Assumption

    link_id = link_obj.getID()
    tls_id = TLS.getID()
    signal_info = signal_df[signal_df.id == tls_id]
    if signal_info['hasProblem'].item() == False:
        cycle = signal_info['avgCycle'].item()
        lanes = eval(signal_info['lanes'].item())
        times = eval(signal_info['avgTimes'].item())
        try:
            lane_idx = lanes.index(lane_id)
            time = times[lane_idx]
            return round(time/cycle, 2)
        except:
            return DEFAULT_g_over_C
    else:
        return DEFAULT_g_over_C


def generate_region_connections(network, labels, boundary_ids, signal_report, vehicle_l=4, minGap=1.4, tau=1):

    """
    Generates dataframe for region_connection.csv
    boundary_ids = {region id: {boundary: {b_neighbor1:regionID, ...}, ...}, ...}
    """
    # vehicle_l = 4
    # minGap = 1.4
    # tau = 1
    direction_factor_table = {'t':0.5, 'l':0.5, 'L':0.5, 'R':0.75, 'r':0.75, 's':1}
    # direction_factor_table = {'t':1, 'l':1, 'L':1, 'R':1, 'r':1, 's':1}
    data = {'start_region':[], 'end_region':[], 'max_outflow':[], 'initial_n_vehs':[]}

    for current_region, boundaries in boundary_ids.items():
        neighbors_outflows = {i: 0 for i in labels if i != current_region}
        for boundary, b_neighbors in boundaries.items():
            current_boundary = network.getEdge(boundary)
            current_speed = current_boundary.getSpeed()
            laneCapacity = 3600/(tau+(vehicle_l+minGap)/current_speed)

            out_of_reg_neighbors = [b_neighbor for b_neighbor, neighbor_reg in b_neighbors.items()
                                    if neighbor_reg != current_region]
            outgoing = current_boundary.getOutgoing()
            outgoing = {edge.getID(): val for edge, val in outgoing.items() if edge.getID() in out_of_reg_neighbors}
            if len(outgoing) == 0:
                continue
            # now we know what are the neighbors that are in another regions and this boundary goes to. Also we know
            # the lanes and connections by which the boundary is connected to its neighbor links.
            # for calculation of maxflow, we need to know the lanes that go to a neighbor region not just the links
            # since some lanes of a boundary link might turn into a link in the same region.

            for link in outgoing.keys():
                connections = outgoing[link]
                fromLanes = {connection.getFromLane().getID():direction_factor_table[connection.getDirection()]
                             for connection in connections}
                # there should be a difference between the capacity of left, right, and through lanes
                fromLanes = {lane:factor*_get_green_allocation_ratio(current_boundary, lane, signal_report)
                             for lane, factor in fromLanes.items()}
                # we also need to consider traffic lights at boundaries
                fromLanes = {lane: finalfactor * laneCapacity for lane, finalfactor in fromLanes.items()}
                # what is the capacity for each connection between current link and selected neighbor link

                simple_capacity = len(fromLanes.keys()) * int(laneCapacity)
                calculated_capacity = int(sum(fromLanes.values()))
                neighbors_outflows[b_neighbors[link]] += calculated_capacity
                # we add the calculated capacity to outflow between current region to adjacent region


        for neighbor_reg, max_outflow in neighbors_outflows.items():
            if max_outflow != 0:
                data['start_region'].append(current_region)
                data['end_region'].append(neighbor_reg)
                data['max_outflow'].append(round(max_outflow/3600, 2))  # use veh/sec for max_outflow
                data['initial_n_vehs'].append(0)

    return pd.DataFrame(data=data)