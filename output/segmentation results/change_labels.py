input_folder = 'may27step3'
total_labels = 12

map_foler = 'boundaryadjustment for may27 from step3 to step4'
output_folder = 'may27step4'

# from_label = 4
# to_label = 11


if __name__ == '__main__':



    inputs = dict()
    for i in range(total_labels):
        with open(f'{input_folder}/{i}.txt', 'r') as f:
            inputs[i] = f.read().splitlines()

    for from_label,to_label in [(4,11),(10,4),(11,4), (1,9), (1,7), (5,7), (1,5), (5,6), (6,5), (8,5), (5,8), (8,6)]:
        edge_list = []
        with open(f'{map_foler}/{from_label}to{to_label}.txt', 'r') as f:
            edge_list = f.read().splitlines()
        for edge in edge_list:
            inputs[from_label].remove(edge)
            inputs[to_label].append(edge)

    for i in range(total_labels):
        with open(f'{output_folder}/{i}.txt', 'w') as f:
            f.write('\n'.join(inputs[i]))
