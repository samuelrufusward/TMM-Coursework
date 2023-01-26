import pandas as pd
import numpy as np
from geopy import distance
import geopandas as gpd
import matplotlib.pyplot as plt


def get_distance(p1, p2):
    """Returns euclidean distance"""
    return np.sqrt( (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 )


def get_dst_lat_lng(coord1, coord2):
    """Returns distance between two lat lng coords"""
    d = distance.distance(coord1, coord2).km

    return d


def get_data():
    """Fetch ward-level population data for Bristol and pre-process for radiation model"""
    path = 'data/population-estimates-time-series-ward.xlsx'

    df = pd.read_excel(path)

    df = df.drop(['geo_shape'], axis=1)

    # Keep only 2020 data
    df = df[df['Mid-Year']==2020]

    df['geo_point_2d']=df['geo_point_2d'].apply(lambda x: [float(value) for value in str(x).split(', ')])

    return df


def radiation_model(data, zone_i, zone_j, employment_rate=0.781):
    """Get predicted number of commutes originating from zone i, to zone j"""

    # Get data specific to each zone
    zone_a_data = data.loc[data['Ward 2016 name'] == zone_i]
    zone_b_data = data.loc[data['Ward 2016 name'] == zone_j]

    centre = data.loc[data['Ward 2016 name'] == zone_i]
    central_point = centre['geo_point_2d'].values[0]

    # Create column of pairwise distances
    data['dij'] = data['geo_point_2d'].apply(lambda x: get_distance(central_point, x))
    # Get distance from zone i to j
    Dij = float(data['dij'].loc[data['Ward 2016 name'] == zone_j])

    # Get zones within circle with radius Dij
    intervening_zones = data[data['dij'] <= Dij]

    Mi = int(zone_a_data['Population estimate'].values[0])
    Nj = int(zone_b_data['Population estimate'].values[0])

    # Population in circle of radius Dij excluding i & j
    Sij = intervening_zones['Population estimate'].sum() - Mi - Nj

    # Total number of journeys originating in i
    Ti = Mi * employment_rate

    x = Ti * (Mi * Nj) / ( (Mi + Sij) * (Mi + Nj + Sij) )

    return x


def plot_journey_heatmap(data, origin_ward, d_min):
    """Finds the which journey ij originating in ward i has the greatest predicted proportion of the total journeys
     from i.
     data: dataframe of ward population data
     origin_ward: string name of origin ward
     d_min: minimum distance between wards i and j to be considered"""

    df_places = gpd.read_file('data/ward-boundaries-may-1999-to-april-2016.geojson')

    ward_names = np.unique(df['Ward 2016 name'])

    journey_fluxes = {ward: radiation_model(data, zone_i=origin_ward, zone_j=ward) for ward in ward_names}

    journey_fluxes[origin_ward] = 0.0

    # Create df columns containing flux values for each ward
    df_places['flux'] = df_places.ward_name.map(lambda name: journey_fluxes[name] if name in list(journey_fluxes.keys()) else 0.0)

    # Plot wards with colour map by flux from origin ward
    fig = df_places.plot(column='flux', cmap='cividis')

    # Annotate ward names
    for ward in df_places.ward_name:
        ward_row = df_places.loc[df_places.ward_name==ward]
        loc = ward_row['geo_point_2d'].values[0]
        x = loc['lon']
        y = loc['lat']
        fig.annotate(ward, xy=(x, y), color='springgreen', xytext=(-10,0), textcoords='offset points', fontsize=5)
    # Alternate format
    # for ward in ward_names:
    #     ward_row = data.loc[data['Ward 2016 name']==ward]
    #     loc = ward_row['geo_point_2d'].values[0]
    #     x = loc[1]
    #     y = loc[0]
    #     if ward in list(journey_fluxes.keys()):
    #         fig.annotate(ward+"\n"+" "*int(0.5*len(ward)) + str(round(journey_fluxes[ward], 1)), xy=(x, y),
    #         color='springgreen', xytext=(-5, 0), textcoords='offset points', fontsize=5)

    plt.title("Ward journey fluxes originating in {}".format(origin_ward))
    plt.show()

    # Remove origin ward
    del journey_fluxes[origin_ward]
    print("Journey fluxes:")
    for w in sorted(journey_fluxes, key=journey_fluxes.get, reverse=True):
        print(w, round(journey_fluxes[w],1))

    centre = data.loc[data['Ward 2016 name'] == origin_ward]
    central_point = centre['geo_point_2d'].values[0]

    # Create column of pairwise distances
    data['dij'] = data['geo_point_2d'].apply(lambda x: get_dst_lat_lng(central_point, x))

    # Only consider wards where distance from origin is greater than d_min
    relevant_data = data.loc[data['dij'] >= d_min]
    relevant_wards = np.unique(relevant_data['Ward 2016 name'])

    # Get the commute proportions of the relevant wards
    relevant_proportions = {ward: journey_fluxes[ward] for ward in relevant_wards}

    # Locate destination ward with the greatest proportion of journeys from origin ward
    max_ward = max(relevant_proportions, key=relevant_proportions.get)
    print("\nWard with greatest flux over {} km from {}:".format(d_min, origin_ward))
    print(max_ward, round(relevant_proportions[max_ward], 1))


if __name__ == "__main__":
    df = get_data()
    print(df['Ward 2016 name'].values)
    while True:
        origin = input("\nInput origin ward:")
        min_distance = input("Input minimum distance to destination (km):")
        plot_journey_heatmap(data=df, origin_ward=origin, d_min=float(min_distance))
