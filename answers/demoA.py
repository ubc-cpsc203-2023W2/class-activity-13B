# brew install spatialindex
# pip install osmnx
# pip install folium
# need to make slides to guide people through the hard parts of this code.

import osmnx as ox
import networkx as nx  # python's standard graph module needed by osmnx
import folium  # needed by osmnx
import pandas as pd
from collections import defaultdict
import itertools

# ASSEMBLE THE GRAPH
# get the region of interest
place_names = ['UBC', 'Pacific Spirit Regional Park, BC', 'Vancouver, BC']
local = ox.geocode_to_gdf(place_names)
print(local.head())  # Note especially the column labeled geometry the value is a Polygon which is a map region

# show the region (project to avoid skew, but leave data in latlong for computation)
# toshow = ox.project_gdf(local) #move the coordinates to something that looks nice
# ax = toshow.plot(fc='gray', ec='none')

# combine regions explicitly so we capture the roads that go between them.
unified = local.unary_union.convex_hull

# grab the parts of the GRAPH that fall within the region
G = ox.graph_from_polygon(unified, network_type='drive', truncate_by_edge=True,
                          simplify=True)
# ox.plot_graph(ox.project_graph(G)) #check to see if this is the graph we want

# assemble the errands list =============================================================
# check locations with the openstreetmaps.com website, to make sure the titles return a valid place
errands = [
           'Nat Bailey Stadium, Vancouver, BC', 
           'PNE, Vancouver, BC',
           'Science World', 
           'Oakridge Park, Vancouver', 
           'Granville St & W King Edward Ave, Vancouver, BC',
           'Cambie St & W 16th Ave, Vancouver, BC',
           'Granville Island', 
           'Pallet Coffee Roasters, Vancouver, BC', 
           'Jericho Beach, Vancouver, BC',
           'Point Grey Secondary, Vancouver, BC'
           ]

# errands = ['2366 Main Mall, Vancouver, BC','Chan Centre, Vancouver, BC', 'War Memorial Gym, Vancouver, BC']
dferrands = pd.DataFrame({'errand': errands})  # change the list into a dataframe so we can use it w osmnx
# print(dferrands)

# slide for lambdas
dferrands['latlong'] = dferrands.apply(lambda row: ox.geocode(row['errand']), axis=1)  # add lat/long to the df
# print(dferrands)
#
dferrands['node'] = dferrands.apply(lambda row: ox.nearest_nodes(G, X = row['latlong'][1], Y = row['latlong'][0]), axis=1)  # add node ID to df

#print(dferrands)


# create pairwise distances =============================================================
# I wanted to do this only with dataframes (no iteration) but it crashed if there was no path between two nodes.
# There may be a better way...
# slide for table of distances

dfdict = defaultdict(lambda: defaultdict())
dfdist = defaultdict(lambda: defaultdict())
for idx1, row1 in dferrands.iterrows():
    for idx2, row2 in dferrands.iterrows():
        if nx.has_path(G, row1['node'], row2['node']):
            dfdict[row1['node']][row2['node']] = nx.shortest_path(G, row1['node'], row2['node'], weight='length')
            dfdist[row1['node']][row2['node']] = nx.shortest_path_length(G, row1['node'], row2['node'], weight='length')
        else:
            print("we don't like " + str(row1['node']) + " and " + str(row2['node']))

# can now say something like dfdict[node1][node2] and get the shortest path from node1 to node2 dfdist gives path len
# # find the best route! ===============================================================
#
# slide to help people realize that we don't need to think about starting point yet.
# slide to help understand the wrapping around
def tourlength(tour):
    sum = 0
    for k, val in enumerate(tour):
        sum += dfdist[tour[k]][
            tour[(k + 1) % len(tour)]]  # need a bit of error handling, since some paths may not exist
    return sum

# slide for permutations
tours = list(itertools.permutations(list(dferrands['node'])))  # all possible tours, including reverses
# print(tours)

# classic "find min"
besttourdist = tourlength(tours[0])
besttour = tours[0]
#
for t in tours:
    if tourlength(t) < besttourdist:
        besttourdist = tourlength(t)
        besttour = t
#
# print(besttour)
#
# # best is found, now assemble the route ============================================================
#
# we know the order, and now we need the turn-by-turn info so it can be plotted on the map.
bestroute = [besttour[0]]
for index, place in enumerate(besttour):
    bestroute += (nx.shortest_path(G, besttour[index], 
                                   besttour[(index + 1) % len(besttour)], 
                                   weight='length'))[1:]

# print(bestroute)
#
# # make a folium map =============================================================
kwargs = {'color':'#AA1111','width':3}
m = ox.plot_route_folium(G, bestroute, popup_attribute='name',**kwargs)


# function to create a marker for each errand, and add it to the map
def buildMarker(row):
    folium.CircleMarker((row['latlong'][0], row['latlong'][1]), popup_attribute=row['errand'],
                        color='green', radius=5, fill=True).add_to(m)


dferrands.apply(buildMarker, axis=1)
home = dferrands.iloc[0]
folium.CircleMarker((home['latlong'][0], home['latlong'][1]), popup_attribute=home['errand'],
                    color='blue', radius=10, fill=True, fill_opacity=1.0).add_to(m)

m.save('map.html')
