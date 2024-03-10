"""Based on https://github.com/Timothysit/sciplotlib/blob/5dcf8ff3e1cf0123b8f45c025c8d4d69271d1e99/module/misc.py#L5
and the Economist style guide https://design-system.economist.com/documents/CHARTstyleguide_20170505.pdf

Figure size are in inches (default)
"""
import matplotlib.pyplot as plt
import math

def color_palette(style='economist'):
    # Note that color orders depend on the chart type
    # work in progress
    if style == 'economist':
        colors = [
            "#3EBCD2",
            "#006BA2",
            "#DB444B",
            "#EBB434",
            "#379A8B",
            "#B4BA39",
            "#9A607F",
            "#D1B07C",
        ]
    elif style in ['thermoneter', 'scatter'] :
        colors = [
            "#3EBCD2",
            "#DB444B",
            "#ffcd19",
            "#006BA2",
            "#379A8B",
            "#9A607F",
            "#963c4c",
        ]
        
    return colors

def add_titles(
    fig, 
    title_label=None, 
    subtitle_label=None, 
    subsubtitle_label=None,
    datasource_label=None,
    title_size=15, 
    subtitle_size=10, 
    subsubtitle_size=9,
    base_ypos = 0.94,
    datasource_ypos=0,
    base_xpos = -0.08
    ):
    """
    Dynamically adds a title, subtitle, and sub-subtitle to a matplotlib figure.
    
    Parameters:
    - fig: The figure object to which the titles will be added.
    - title_label: The main title text.
    - subtitle_label: The subtitle text.
    - subsubtitle_label: The sub-subtitle text.
    - datasource_label: The datasource text.
    - title_size: Font size for the title.
    - subtitle_size: Font size for the subtitle.
    - subsubtitle_size: Font size for the sub-subtitle.
    """
    fig_size = fig.get_size_inches()*fig.dpi

    y_spacing = 4
    
    
    subsubtitle_y_offset = 0
    if subsubtitle_label is not None:
        subsubtitle_y_offset = rround((subsubtitle_size+y_spacing)/fig_size[1])
        
    subtitle_y_offset = 0
    if subtitle_label is not None:
        subtitle_y_offset = rround((subtitle_size+y_spacing)/fig_size[1])
    
    subsubtitle_ypos = base_ypos
    subtitle_ypos = base_ypos + subsubtitle_y_offset
    title_ypos = base_ypos + subsubtitle_y_offset + subtitle_y_offset + 0.01
    
    if title is not None:
        title(fig=fig, label=title_label, size=title_size, xpos=base_xpos, ypos=title_ypos)
    if subtitle is not None:
        subtitle(fig=fig, label=subtitle_label, size=subtitle_size, xpos=base_xpos, ypos=subtitle_ypos)
    if subsubtitle is not None:
        subsubtitle(fig=fig, label=subsubtitle_label, size=subsubtitle_size, xpos=base_xpos, ypos=subsubtitle_ypos)
    if datasource_label is not None:
        datasource(
            label=datasource_label,
            xpos=base_xpos,
            ypos=datasource_ypos,
            fig=fig,
        )

def rround(number):
    number *= 100
    rounded_number = math.ceil(number)
    return rounded_number / 100

def title(
    label: str = 'Main title',
    weight: str = 'bold',
    size:float = 15,
    xpos:float = 0,
    ypos:float = 0.9,
    fig = plt.gcf(),
    **kwargs):
    """Main title should describe the key takeaway.
    
    e.g., "A wide ideaology gap is opening up between young men and women 
    in countries across the world.", or,
        "Japan leads U.S. in bond yields"

    
    """
    
    fig.text(xpos, ypos, s=label, weight=weight, size=size, **kwargs)
    
def subtitle(
    label: str = 'This is a subtitle',
    size:float = 10,
    xpos:float = 0,
    ypos:float = 1.01,
    fig = plt.gcf(), 
    **kwargs):
    """Subtitle gives the technical description.
    
    e.g., "Political idealogy of 19-28s (% liberal - % conservative), by sex", or
        "Ten-year government bold yields, %", or,
        "India, bank credit to the commercial sector"
    
    """
    
    fig.text(xpos, ypos, s=label, size=size, **kwargs)
    
def subsubtitle(
    label: str = 'This is a sub-subtitle',
    size:float = 9,
    xpos:float = 0,
    ypos:float = 1.0,
    fig = plt.gcf(), 
    **kwargs):
    """Continuation of the subtitle, usually units and date information.
    
    Where possible, put units and date information on a second line at smaller font size
    
    e.g., % increase on a year earlier
    """
    
    fig.text(xpos, ypos, s=label, size=size, **kwargs)



def add_economist_rectangle(fig, ax, xpos=0.1, ypos=1.04, width=0.05, height=0.04):
    """


    References
    ---------
    economist color scheme: http://pattern-library.economist.com/color.html
    """

    economist_red = '#e3120b'

    fig.patches.extend([plt.Rectangle(
        (xpos, ypos), width=width, height=height,
        fill=True, color=economist_red, alpha=1, zorder=1000,
        transform=fig.transFigure, figure=fig)
    ])

    return fig, ax

def datasource(
    label='Source: data source', 
    xpos=0.1, 
    ypos=-0.1, 
    fontsize=10, 
    weight='light', 
    alpha=0.8,
    fig=plt.gcf(),
    **kwargs
    ):
    """
    Add datasource text to plots imitating the style of The Economist.
    
    Args:
    ---
    fig
    ax
    s
    xpos
    ypos
    fontsize
    weight
    alpha

    Returns
    -------

    """
    fig.text(
        xpos, ypos, s=label, fontsize=fontsize, alpha=alpha, weight=weight, **kwargs
        )

def display_examples():
    # Ensure a figure size that allows for the title to be visible
    plt.figure(figsize=(10, 6))  # Example figure size, adjust as needed

    # Example plotting code
    plt.plot([0, 1], [0, 1], label='Line')

    add_titles(
        fig=plt.gcf(),
        title_label='title',
        subtitle_label='subtitle',
        subsubtitle_label='subsubtitle',
        base_ypos = 0.9,
        base_xpos = 0.13
    )
    plt.show()
    
    return None

if __name__=='__main__':
    pass