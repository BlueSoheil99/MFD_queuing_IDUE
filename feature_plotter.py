from PIL import Image
from inout import utility as util
import numpy as np
import pickle
import io_handler
import io
import os


def get_network(input_addresses="config files/feature_plotter_config.yaml"):
    network_name, info_name, feature, net_edges, interval_begin, interval_end, \
        edges_to_remove, minor_links, predetermined_regions = util.init_config(input_addresses)

    net, edges, _ = util.read_network(network_name, net_edges, edges_to_remove, minor_links, predetermined_regions)
    list_of_edges = [edge.getID() for edge in edges]
    return net, list_of_edges, feature, interval_begin, interval_end, info_name


def get_name(interval_id):
    hour = str(int(float(interval_id) // 3600))
    minute = str(int((float(interval_id) % 3600) / 60))
    if len(hour)==1:
        hour = '0'+hour
    if len(minute) == 1:
        minute = '0'+minute
    return f'{hour}:{minute}'


def get_features(edge_list, start_time, end_time, feature_name, data_adr, step_size=1):
    with open(data_adr, "rb") as f:
        edge_stats = pickle.load(f)
        f.close()
    feature_matrix = np.zeros(((end_time-start_time)//(60*step_size), len(edge_list)))
    time_intervals = []
    times = [i for i in range(start_time, end_time, step_size*60)]
    edge_stats2 = {interval_id: edges_data for interval_id, edges_data in edge_stats.items()
                   if float(interval_id) in times}

    for i, (interval_id, edges_data) in enumerate(edge_stats2.items()):
        feature_list = []
        # if float(interval_id) < start_time or float(interval_id) >= end_time:
        #     continue
        for edge_id in edge_list:
            if edge_id in edges_data:
                edge_data = edges_data[edge_id]
                if edge_data.get(feature_name) is None:
                    feature_list.append('0')
                else:
                    feature = edge_data[feature_name]
                    feature_list.append(feature)
            else:
                feature_list.append(None)

        feature_list = np.array(feature_list)
        interval = get_name(interval_id)
        print(f'{i}: interval {interval} has {sum(np.array(feature_list)==None)} None {feature_name} values out of {len(feature_list)} edges')
        # nones = (feature_list==None)
        # feature_list[feature_list==None] = 2
        # feature_list=feature_list.astype(np.float)
        #
        # feature_list[feature_list>=1] = 2  # including None values
        # feature_list[feature_list<0.2] = 3
        # feature_list[feature_list<1] = 1
        # feature_list[nones] = 0
        # feature_list = feature_list.astype(int)
        # # feature_list[feature_list==None] = 0

        feature_matrix[i, :] = feature_list
        time_intervals.append(interval)
    feature_matrix = feature_matrix.astype(int)
    return feature_matrix, time_intervals


def buffer_plots(feature_matrix, time_titles, feature_name, colormap='binary'):
    buffers = []
    for i in range(len(feature_matrix)):
        img_buf = io.BytesIO()
        io_handler.show_network(net, edges, feature_matrix[i], colormap_name=colormap,
                                title=f'{feature_name} distribution of:{time_titles[i]}',
                                save_adr=img_buf)
        buffers.append(img_buf)
        print(f'image done:{time_titles[i]}')
    return buffers


def generate_images(feature_matrix, time_titles, output_address, feature_name, colormap='binary', colormap_range=None):
    for i in range(len(feature_matrix)):
        io_handler.show_network(net, edges, feature_matrix[i], colormap_name=colormap,
                                 alpha=0.5, mapscale=8.0,
                                title=f'{feature_name} distribution of  {time_titles[i]}',
                                save_adr=output_address+f'/{time_titles[i]}.JPG', colorbar_range=colormap_range)
        print(f'image done:{time_titles[i]}')


def make_gif(frame_folder, output_path):
    frames = [Image.open(image) for image in frame_folder if image.split('.')[-1] == 'JPG']
    frame_one = frames[0]
    frame_one.save(output_path, format="GIF", append_images=frames,
                   save_all=True, duration=100, loop=0)


def show_statistics(mat, start_from):
    # Calculate statistics
    d = mat.copy()[start_from:]
    mean = np.mean(d)  # Mean
    std = np.std(d)  # Standard deviation
    min_val = np.min(d)  # Minimum value
    max_val = np.max(d)  # Maximum value
    median = np.median(d)  # Median
    quantiles = np.percentile(d, [25, 50, 75, 85, 95])  # Quartiles (25th, 50th, 75th percentiles)

    # Print statistics
    print(f"Mean: {mean}")
    print(f"Standard Deviation: {std}")
    print(f"Minimum: {min_val}")
    print(f"Maximum: {max_val}")
    print(f"Median: {median}")
    print(f"25th Percentile: {quantiles[0]}")
    print(f"50th Percentile (Median): {quantiles[1]}")
    print(f"75th Percentile: {quantiles[2]}")
    print(f"85th Percentile: {quantiles[3]}")
    print(f"95th Percentile: {quantiles[4]}")
    return quantiles


if __name__ == "__main__":
    '''
    This file uses 1-min outputs(for each 5 minute) to create .gif files and show changes 
    in the given feature (in feature_plotter_config file) 
    '''
    net, edges, feature_name, interval_begin, interval_end, data_adr = get_network()
    matrix, time_titles = get_features(edges, interval_begin, interval_end, feature_name, data_adr, step_size=5)
    output_path = f'output/{feature_name}_{interval_begin}_{interval_end}_5.gif'

    quantiles = show_statistics(matrix, int(len(matrix)/2))
    ## making a buffer of plots and NOT saving each plot
    # buffers = buffer_plots(matrix, time_titles, feature_name)
    # make_gif(buffers, output_path)

    ## making the gif using saved images and NOT using an io buffer
    source_folder = f'output/{feature_name}_5_gif_source'
    # source_folder = f'output/{feature_name}_just_minor_5_gif_source'
    # generate_images(matrix, time_titles, source_folder, feature_name,
    #                 colormap='Wistia', colormap_range=[0, 90]) #500 was used previously
    generate_images(matrix, time_titles, source_folder, feature_name,
                    colormap='Wistia', colormap_range=[0, 100]) #500 was used previously
    # source_folder = f'output/{feature_name}_wo_minor_5_gif_source'
    # generate_images(matrix, time_titles, source_folder, feature_name,
    #                 colormap='Wistia', colormap_range=[0, quantiles[3]])
    l = [source_folder+'/'+name for name in sorted(os.listdir(source_folder))]
    make_gif(l, output_path)
