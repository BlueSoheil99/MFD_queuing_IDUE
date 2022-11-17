import matplotlib
import matplotlib.pyplot as plt


def init_plot():
    plt.close("all")
    fig = plt.figure()
    ax = fig.add_subplot(111)
    return fig, ax


def init_colors(colormap_name, vmin, vmax):
    colormap = plt.cm.get_cmap(colormap_name)
    cNorm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    scalarMap = matplotlib.cm.ScalarMappable(norm=cNorm, cmap=colormap)
    return scalarMap


def get_color(colormap, i, volume=None):
    if volume is None:
        return "gray"
    else:
        return colormap.to_rgba(i)
