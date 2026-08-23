import math
import matplotlib.colors as mcolors
from . import PlotConfig as pc

'''
Contains plots or plot element functions utilized in relation to plotting rotation measure data.
'''
# -------- FUNCTION DEFINITION --------
def p2RGB(values, size_cap = math.inf, scale_factor = 1.0, alpha = 1.0):
    '''
    Takes values and assigns them a marker colour and size for use in plotting.
    Colors are configurable via PlotConfig (default: red for negative, blue for positive).
    :param values: The rotation measure, or list of rotation measures
    :param size_cap: The maximum size of value that should be plotted. Beyond this, all larger values (in magnitude) will be plotted only at this size. Set to math.inf to disable.
    :param scale_factor: The scaling factor of the plotted points. Default is set to 1.0
    :param alpha: The transparency of the plotted points. Default is set to 1.0
    :return:
        c: A list of tuples of the (R, G, B, Alpha) values for the points.
        s: A list of float values of the size of the points.
    '''
    # Convert configured color names to RGB tuples
    neg_rgb = mcolors.to_rgb(pc.RMMAP_NEGATIVE_COLOR)
    pos_rgb = mcolors.to_rgb(pc.RMMAP_POSITIVE_COLOR)
    zero_rgb = (0, 1, 0)  # Green for zero

    c = [neg_rgb + (alpha,) if item < 0 # Negative rotation measures
            else pos_rgb + (alpha,) if item > 0 # Positive rotation measures
            else zero_rgb + (alpha,) # Zero-value rotation measures
            for item in values]  # Marker colour
    s = [abs(item)*scale_factor if abs(item) < size_cap
         else abs(size_cap)*scale_factor
         for item in values]

    return c, s
# -------- FUNCTION DEFINITION. --------

# -------- FUNCTION DEFINITION --------
def p2C(values, colour = (0, 0, 0), size_cap = math.inf, scale_factor = 1.0, alpha = 1.0):
    '''
    Takes values and assigns them the colour and a size for use in plotting.
    :param values: The rotation measure, or list of rotation measures
    :param colour: The colour of the plotted points. A tuple of (R, G, B). Default is black.
    :param size_cap: The maximum size of value that should be plotted. Beyond this, all larger values (in magnitude) will be plotted only at this size. Set to math.inf to disable.
    :param scale_factor: The scaling factor of the plotted points. Default is set to 1.0
    :param alpha: The transparency of the plotted points. Default is set to 1.0
    :return:
        c: A list of tuples of the (R, G, B, Alpha) values for the points.
        s: A list of float values of the size of the points.
    '''

    c = [(colour[0], colour[1], colour[2], alpha) for _ in range(len(values))]
    s = [abs(item)*scale_factor if abs(item) < size_cap
         else abs(size_cap)*scale_factor
         for item in values]

    # return the list of RGBA tuples and sizes
    return c, s
# -------- FUNCTION DEFINITION. --------