from PIL import Image
from inout import utility as util
import numpy as np
import pickle
import io_handler
import io
import os


def get_network(input_addresses="feature_plotter_config.yaml"):
    net_fname, info_fname, feature_name, net_edges_fname, interval_begin, interval_end, edges_to_remove, \
            minor_edges, highways = util.init_config(input_addresses)
    net, edges = util.read_network(net_fname, net_edges_fname, edges_to_remove, minor_edges, highways)
    list_of_edges = [edge.getID() for edge in edges]
    return net, list_of_edges, feature_name, interval_begin, interval_end, info_fname


def get_name(interval_id):
    hour = str(int(float(interval_id) // 3600))
    minute = str(int((float(interval_id) % 3600) / 60))
    if len(hour)==1:
        hour = '0'+hour
    if len(minute) == 1:
        minute = '0'+minute
    return f'{hour}{minute}'


def get_features(edge_list, start_time, end_time, feature_name, data_adr):
    with open(data_adr, "rb") as f:
        edge_stats = pickle.load(f)
        f.close()
    feature_matrix = np.zeros(((end_time-start_time)//60, len(edge_list)))
    time_intervals = []
    edge_stats2 = {interval_id: edges_data for interval_id, edges_data in edge_stats.items()
                   if start_time <= float(interval_id) < end_time}

    for i, (interval_id, edges_data) in enumerate(edge_stats2.items()):
        feature_list = []
        # if float(interval_id) < start_time or float(interval_id) >= end_time:
        #     continue
        for edge_id in edge_list:
            if edge_id in edges_data:
                edge_data = edges_data[edge_id]
                feature = edge_data[feature_name]
                feature_list.append(feature)

        feature_list = np.array(feature_list)
        interval = get_name(interval_id)
        print(f'{i}: interval {interval} has {sum(np.array(feature_list)==None)} None {feature_name} values out of {len(feature_list)} edges')
        feature_list[feature_list==None] = 0
        feature_matrix[i, :] = feature_list
        time_intervals.append(interval)

    return feature_matrix, time_intervals


def buffer_plots(feature_matrix, time_titles, feature_name):
    buffers = []
    for i in range(len(feature_matrix)):
        img_buf = io.BytesIO()
        io_handler.show_network(net, edges, feature_matrix[i], colormap_name='binary',
                                title=f'{feature_name} distribution of:{time_titles[i]}',
                                save_adr=img_buf)
        buffers.append(img_buf)
        print(f'image done:{time_titles[i]}')
    return buffers


def generate_images(feature_matrix, time_titles, output_address, feature_name):
    for i in range(len(feature_matrix)):
        io_handler.show_network(net, edges, feature_matrix[i], colormap_name='binary',
                                 alpha=0.5, mapscale=8.0,
                                title=f'{feature_name} distribution of:{time_titles[i]}',
                                save_adr=output_address+f'/{time_titles[i]}.JPG')
        print(f'image done:{time_titles[i]}')


def make_gif(frame_folder, output_path):
    frames = [Image.open(image) for image in frame_folder]
    frame_one = frames[0]
    frame_one.save(output_path, format="GIF", append_images=frames,
                   save_all=True, duration=100, loop=0)


if __name__ == "__main__":
    net, edges, feature_name, interval_begin, interval_end, data_adr = get_network()
    matrix, time_titles = get_features(edges, interval_begin, interval_end, feature_name, data_adr)
    output_path = f'output/{feature_name}_{interval_begin}_{interval_end}.gif'

    ## making a buffer of plots and NOT saving each plot
    # buffers = buffer_plots(matrix, time_titles, feature_name)
    # make_gif(buffers, output_path)

    ## making the gif using saved images and NOT using an io buffer
    source_folder = f'output/{feature_name}_gif_source'
    generate_images(matrix, time_titles, source_folder)
    l = [f'output/{feature_name}_gif_source/'+name for name in sorted(os.listdir(source_folder))]
    make_gif(l, output_path)
