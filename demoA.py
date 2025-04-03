import osmnx as ox
import networkx as nx  # python's standard graph module needed by osmnx
import folium  # needed by osmnx
import pandas as pd
from collections import defaultdict
import itertools

# Choose whether to run a short or a longer list.
# Execution time for a longer list may be significant.
USE_SHORT_ERRAND_LIST = True

# Should we print intermediate results and maps?
SHOW_EXTRA_DETAIL = True

# Wouldn't it be nice to have some slides to explain some elements of this code?

#----------------------------------------------------------------------
# Assemble the graph.  Same as we did in class activity 13A.
# Get the region of interest.
place_names = ['UBC', 'Pacific Spirit Regional Park, BC', 'Vancouver, BC']
local = ox.geocode_to_gdf(place_names)
print(local.head())  # Note especially the column labeled geometry the value is a Polygon which is a map region

# Combine regions explicitly so we capture the roads that go between them.
unified = local.union_all().convex_hull

# Grab the parts of the GRAPH that fall within the region.
G = ox.graph_from_polygon(unified, network_type='drive', truncate_by_edge=True,
                            simplify=True)
if SHOW_EXTRA_DETAIL:
    print('Close map window to continue...')
    # Show the region (project to avoid skew, but leave data in latlong for computation).
    toshow = ox.projection.project_gdf(local)
    #ax = toshow.plot(fc='gray', ec='none')
    # Check to see if this is the graph we want.
    ox.plot_graph(ox.projection.project_graph(G))

#----------------------------------------------------------------------
# Assemble the errands list
# check locations with the openstreetmaps.com website, to make sure the titles return a valid place

if USE_SHORT_ERRAND_LIST:
    errands = [ '2366 Main Mall, Vancouver, BC',
                'Cecil Green Park House, Vancouver, BC', 
                'War Memorial Gym, Vancouver, BC'
                ]
else:
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

# Change the list into a dataframe so we can use it with osmnx.
dferrands = pd.DataFrame({'errand': errands})

# slide to explain these two lambda maps.
# Add lat/long to the df.
dferrands['latlong'] = dferrands.apply(lambda row: ox.geocode(row['errand']), axis=1)

# Find nearest node in the map to each errand site.
dferrands['node'] = dferrands.apply(lambda row: ox.nearest_nodes(G, X = row['latlong'][1], Y = row['latlong'][0]), axis=1)  # add node ID to df

if SHOW_EXTRA_DETAIL:
    print('Errand list plus lat/long and nodes:')
    print(dferrands)
    print()

#----------------------------------------------------------------------
# Determine pairwise distances between errand locations.
# I wanted to do this only with dataframes (no iteration) but it crashed if there was no path between two nodes.
# There may be a better way...

# slide for table of distances
# TODO

# Can now say something like dfdict[node1][node2] and get the shortest path from node1 to node2 dfdist gives path len


#----------------------------------------------------------------------
# Find the best route!
#
# slide to help people realize that we don't need to think about starting point yet.
# slide to help understand the wrapping around

# Function to compute tour length for a particular tour (permutation of errands).
# TODO

# slide for permutations
# TODO

# Classic "find min" loop.
# TODO

if SHOW_EXTRA_DETAIL:
    # This list will be *very* long if you have more than just a few errands.
    print('All tours')
    print(tours)
    print('\nBest tour:')
    print(besttour)
    print()

#----------------------------------------------------------------------
# Best is found, now assemble the route.
#
# We know the order, but we need the turn-by-turn info so it can be plotted on the map.
# TODO

if SHOW_EXTRA_DETAIL:
    print('Best route:')
    print(bestroute)
    print()

#----------------------------------------------------------------------
# Create the map.
m = ox.routing.route_to_gdf(G, bestroute).explore(color='blue', style_kwds=dict(weight=5))

# Function to create a marker for each errand, and add it to the map.
def buildMarker(row):
    folium.CircleMarker((row['latlong'][0], row['latlong'][1]), popup_attribute=row['errand'],
                        color='green', radius=10, fill=True).add_to(m)

# Now add markers to each errand location.
dferrands.apply(buildMarker, axis=1)

# Add a different colour marker for the start location.
home = dferrands.iloc[0]
folium.CircleMarker((home['latlong'][0], home['latlong'][1]), popup_attribute=home['errand'],
                    color='blue', radius=10, fill=True, fill_opacity=1.0).add_to(m)

# Save the result.
m.save('map.html')
