import matplotlib
import matplotlib.pyplot as plt


def init_plot():
    plt.close("all")
    fig = plt.figure()
    ax = fig.add_subplot(111)
    return fig, ax


def init_colors(colormap_name, vmin, vmax, normalized=False):
    colormap = plt.cm.get_cmap(colormap_name)
    if normalized:
        cNorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
        scalarMap = matplotlib.cm.ScalarMappable(norm=cNorm, cmap=colormap)
        return scalarMap
    return colormap


def get_color(colormap, i, volume=any):
    if volume is None:
        return "gray"
    else:
        return colormap.to_rgba(i)
