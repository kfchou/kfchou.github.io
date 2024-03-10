
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

geographical_mapping = {
    # Within USA
    'San Francisco Bay Area': ['bay area', 'berkeley', 'san francisco', 'oakland', 'palo alto', 'newark, ca', 'south san francisco', 'sacramento','hayward, ca'],
    'Los Angeles Metro': ['los angeles', 'thousand oaks', 'irvine', 'la', 'los ángeles', 'thousand oaks \(los angeles\)','santa barbara', 'irvine', 'socal','orange county','irvine, ca'],
    'San Diego Metro': ['san diego', 'carlsbad', 'san diego, ca'],
    'Boston Metro': ['boston', 'cambridge,? ma', 'worcester ma', 'waltham', 'devens', 'greater boston', 'near boston','boston/cambridge'],
    'New York Metro': ['nyc', 'new york', 'ny,? ny', 'nyc metro', 'new york metro', 'new york city', 'central/north jersey', 'new jersey, usa'],
    'Chicago Metro': ['chicago', 'chicagoland', 'illinois'],
    'Baltimore/Washington DC Metro': ['washington dc', 'dc area', 'gaithersburg, maryland', 'baltimore', 'rockville, md', 'dc','baltimore', 'baltimore, md', 'baltimore/washington dc'],
    'Texas': ['college station tx','houston', 'waco', 'houston, tx', 'houston,tx', 'waco, tx','dallas', 'fort worth', 'remote, tx, us','austin, tx'],
    'Seattle Metro': ['seattle', 'seattle area', 'seattle wa', 'seattle, wa', 'seattle but i work remotely from fl'],
    'Raleigh-Durham Metro': ['raleigh', 'durham, nc', 'rtp', 'research triangle','rtp nc', 'rtp north carolina', 'rtp, nc', 'rtp, north carolina','raleigh-durham','North Carolina'],
    'New Jersy-Philadelphia Metro': ['philadelphia', 'philadelphia metro', 'philadelphia, pa','new jersey','nj-philadelphia', 'nj-philly-de','nj'],
    'Great Lakes': ['usa, albany'],
    'Phoenix Metro': ['phoenix'],
    'Denver Metro': ['denver', 'boulder', 'colorado', 'boulder \(remote, company in bay\)', 'boulder, co'],
    'Pittsburgh Metro': ['pittsburgh'],
    'Portland Metro': ['portland, or'],
    'Salt Lake City Metro': ['salt lake city', 'salt lake city, ut'],
    'Kansas City Metro': ['kansas city', 'kansas city, mo','kansas city, missouri, united states'],
    'Indianapolis Metro': ['indianapolis', 'indianapolis, in'],
    'St. Louis Metro': ['saint louis', 'st\. louis'],
    'Florida': ['miami','orlando','tampa'],
    'Atlanta Metro': ['atlanta'],
    'Ohio': ['cincinnati, ohio','cleveland'],
    'Madison Metro': ['madison, wisconsin'],
    'Central Maine Metro': ['central maine'],
    'Bloomington Metro': ['bloomington, in, usa'],
    'Tennessee': ['Knoxville, TN'],
    # outside of USA:
    'Canada': ['calgary','montreal','toronto','vancouver, canada','halifax, nova scotia','canada'],
    'United Kingdom': ['brighton, uk', 'cambridge uk', 'cambridge, uk', 'u\.k', 'u\.k\.', 'uk', 'macclesfield, uk','dublin','dundee'],
    'Israel': ['rehovot','israel'],
    'Germany': ['munich','germany'],
    'Netherlands': ['netherlands'],
    'Belgium': ['belgium'],
    'Austria': ['austria'],
    'Switzerland': ['switzerland'],
    'Brazil': ['brazil'],
    'France': ['france'],
}

economic_region_mapping = {
    # USA regions
    'New England': [
        'boston', 'cambridge,? ma', 'worcester ma', 'waltham', 'devens', 'cambridge',
        'greater boston', 'near boston','boston/cambridge', 'central maine', 
        'new england, not boston',r'\bma\b','new haven','ridgefield, ct','Providence',
        'Boston / Remote','Hartford, CT'
    ],
    'U.S. Mideast': [
        r'\bny\b','nyc', 'new york', 'ny,? ny', 'nyc metro', 'new york metro', 
        'new york city', 'philadelphia', 'philadelphia metro', 'philadelphia, pa', 'philadelphia',
        'new jersey','nj-philadelphia', 'nj-philly-de','nj', 'baltimore', 
        'washington dc', 'dc area','Washington D.C. Metro','gaithersburg, maryland', 'baltimore','rockfille', 
        'rockville, md', 'dc','baltimore', 'baltimore, md', 'baltimore/washington dc',
        'newark, de','pa','nj','dc','maryland','triangle','pennsylvania','central/north jersey',
        'syracuse','buffalo','Albany'
    ],
    'U.S. Southeast': [
        'charlotte','raleigh', 'durham, nc', 'rtp', 'research triangle', 'rtp nc', 
        'rtp north carolina', 'rtp, nc', 'rtp, north carolina', 'raleigh-durham', 
        'north carolina', 'florida', 'miami', 'orlando', 'tampa','boca raton', 'atlanta', 
        'georgia', 'nashville', 'knoxville, tn','Southeast'
    ],
    'Great Lakes': [
        'chicago', 'chicagoland', 'chicago, il','illinois', 'madison, wisconsin', 'cincinnati, ohio', 
        'cleveland', 'pittsburgh', 'usa, albany', 'michigan, usa', 'indianapolis', 
        'indianapolis, in', 'saint louis', 'st\. louis', 'St Louis','minnesota','Ohio',
        'bloomington, in, usa',
        'minneapolis','minneapolis, mn','Columbus','Columbus, OH','Ann Arbor','madison'
    ],
    'U.S. Plains': [
        'kansas city', 'kansas city, mo', 'kansas city, missouri, united states', 
        'dallas', 'college station tx', 'houston', 'waco', 'houston, tx', 'houston,tx', 
        'waco, tx', 'remote, tx, us', 'austin, tx', 'oklahoma city', 'nebraska', 
        'south dakota','Midwest'
    ],
    'U.S. Rocky Mountains': [
        'denver', 'boulder', 'colorado', 'boulder \(remote, company in bay\)', 
        'boulder, co', 'salt lake city', 'salt lake city, ut', 'idaho', 'montana'
    ],
    'U.S. Southwest': [
        'phoenix', 'las vegas', 'albuquerque', 'tucson, az.', 'new mexico', 
        'san antonio, texas','San Antonio'
    ],
    'U.S. West Coast': [
        'bay area', 'berkeley', 'san francisco', 'oakland', 'palo alto', 'newark, ca', 
        'south san francisco', 'sacramento', 'hayward, ca', 'san diego', 'carlsbad', 
        'san diego, ca', 'los angeles', 'thousand oaks', 'irvine', r'\bla\b', 
        'los ángeles', 'thousand oaks \(los angeles\)', 'santa barbara', 'irvine', 
        'socal', 'orange county', 'irvine, ca', 'seattle', 'seattle area', 
        'seattle wa', 'seattle, wa', 'seattle but i work remotely from fl', 
        'portland, or', 'alaska', 'hawaii',r'\bca\b',r'\bwa\b','california','portland',
        'redwood city'
    ],
    # Outside USA
    'Canada': [
        'calgary', 'montreal', 'toronto', 'vancouver, canada', 'halifax, nova scotia', 
        'canada','vancouver'
    ],
    'United Kingdom': [
        'brighton, uk', 'cambridge uk', 'cambridge, uk', 'u\.k', 'u\.k\.', 'uk', 
        'macclesfield, uk', 'dublin', 'dundee','ireland','Edinburgh'
    ],
    'Israel': ['rehovot', 'israel'],
    'EU':[
        'munich', 'germany','netherlands','belgium','austria','switzerland','france',
        'athens','vienna','london','oxford','amsterdam','Copenhagen','hamburg'
        ],
    'Brazil': ['brazil'],
    'n/a': ['remote'],
}

colors = [
"#000000",
"#ffcd19",
"#ff3943",
"#ff8239",
"#006BA2",
"#3EBCD2",
"#379A8B",
"#9A607F",
"#963c4c",
"#D1B07C",
]

def make_multi_dumbbell(
    df, 
    x_column, 
    y_column, 
    group_column, 
    groups, 
    colors, 
    y_order,
    marker = 'o'):
    """
    df: contains x_column, group_column, y_column
        df has been grouped using `groupby([y_column,group_column])[[x_column]].aggregate()`
    groups (list-like): unique values in group_column, but rearranged in the desired order.
    y_order (list-like): unique values of y_column, but rearranged in the desired order.
    marker (str, list[str]): Defaults to 'o'. Can be any value accepted by 
        seaborn.scatterplot. See https://matplotlib.org/stable/api/markers_api.html.
        and https://matplotlib.org/stable/gallery/lines_bars_and_markers/marker_reference.html#sphx-glr-gallery-lines-bars-and-markers-marker-reference-py.
        If a list is given, different markers may be used for different subgroups displayed.
    """
    assert len(colors) >= len(groups), "There must be more color options than unique group values."
    
    # Initialize the matplotlib figure
    f, ax = plt.subplots(figsize=(8, 5))

    # colors = ['skyblue','orange','magenta','red','green','blue']
    # colors = sm.color_palette('thermoneter')
    if isinstance(marker, str):
        marker = [marker] * len(groups)
        
    for group, color, mark in zip(groups, colors, marker):
        if mark == '|':
            linewidth=3
            zorder = 10
        else:
            linewidth=1
            zorder = 2
            
        # Plot the two values
        sns.scatterplot(
            data=df[df[group_column]==group], 
            x=x_column, 
            y=y_column , 
            color=color,
            # alpha=0.75,
            s=100, 
            # edgewidth=1,
            # edgecolor=None,
            label=group,
            marker=mark,
            linewidth=linewidth,
            zorder = zorder,
            )

    # Draw horizontal lines
    for y_row, y_pos in zip(y_order, np.arange(len(y_order))):
        leftmost = np.min(df[df[y_column]==y_row][x_column])
        rightmost = np.max(df[df[y_column]==y_row][x_column])
        ax.plot([leftmost, rightmost], [y_pos, y_pos], color='#777777', zorder=1)

    return f, ax

def make_dumbbell(df, y_column, x_cols, colors, labels):
    """Modified dumbbell chart. Kinds of like string lights?
    
    df is expected to be sorted in the desired order, with index reset.
    
    This function will simply place each value in the df[x_cols] on the plot as a point.
    
    Example usage:
    
    f, ax = make_dumbbell(
        df=median_values_df, 
        y_column='Seniorty Level',
        x_cols=['Annual Base Salary','Annual Total Salary'],
        colors=['skyblue','orange'],
        labels=['Base Annual Compensation','Total Annual Compensation']
        )
    """
    f, ax = plt.subplots(figsize=(8, 5))

    # Plot the "points"
    for x_col, color, label in zip(x_cols, colors, labels):
        sns.scatterplot(
            data=df, x=x_col, y=y_column , color=color, s=100, label=label, zorder=10)

    # Draw lines
    for i in range(df.shape[0]):
        left_point = min(df[x_cols].iloc[i])
        right_point = max(df[x_cols].iloc[i])
        ax.plot(
            [left_point, right_point], 
            [df[y_column][i], df[y_column][i]], 
            color='gray',
            zorder=1)

    return f, ax
        
