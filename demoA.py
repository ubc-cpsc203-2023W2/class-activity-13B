
import osmnx as ox
import networkx as nx  # python's standard graph module needed by osmnx
import folium  # needed by osmnx
import pandas as pd
from collections import defaultdict
import itertools

# Decide with the class where you would like your tour to take place. Once decided, students working on the assembly
# of stops will choose specific locations.

# The skeleton below will require you to complete the following tasks:
# 1. Create a graph of all the relevant streets in your project. This can be done in many different ways.
#       See https://github.com/gboeing/osmnx-examples/blob/master/notebooks/01-overview-osmnx.ipynb


# 2. Make a dataframe containing the names of the stops on your tour, and to it, add columns for lat/long
#       and for nodes in the graph. All locations must be within the graph from part 1. Use openstreetmap.org
#       to validate your choice of placename. Lat/long can be attained using osmnx function "geocode". It is
#       up to you to figure out how to find a node in the graph, given a lat/long.

df = pd.DataFrame(columns=['Name','latlon','node'])
List = ["parc jean Drapeau", "Parc de fontaine","McGill","UQAM"] # This list can be edited
for place in List:
    latlon = ox.utils.geocode(place) # return a tuple (lat,lon)
    node = ox.get_nearest_node(G,latlon) # need G from part 1 to make the code works
    newrow = {'Name':place, 'latlon':latlon,'node':node}
    #newrow = {'Name':place, 'latlon':latlon}
    df = df.append(newrow, ignore_index=True)
print(df)
# 3. Given a dataframe of nodes in a graph, build a 2D structure that records the shortest distance between every
#       pair of nodes. You will use this as a lookup table for finding distances as you evaluate tours.
# 4. Write a function that takes a list of nodes representing a tour, and a distance table (from part 3) as input,
#       and which returns the total length of the tour. The distance should "wrap around" the end, and back to the
#       start.
# 5. Write a function that, given the location dataframe, makes a list of all possible tours, and from that list
#       selects the one with least total distance. the "itertools" module has a function called "permutations"
#       which you will certainly want to use. Use the function defined in part 4) to determine the length of a
#       tour.
# 6. Now that you know the best tour, you need to assemble the actual routes between the stops. The nx.shortest_path
#       function returns a list of nodes. There are some gotchas with this task, but you'll learn a lot if you
#       have to figure them out. :)

# 7. Finally, make a folium map with the route and all the stops laid out.


#DOING NUMBER 3
# a node is a coordinate location

#df.loc[row_indexer,column_indexer]


def give_me_an_array_pls(grid, df):
    nodes = list(df.iloc[:,-1])
    size = len(nodes)

    the_array = np.zeros((size, size))
    for i in range(size):  # row
        for j in range(size):  # column
             the_array[i, j] = nx.shortest_path(grid, nodes[i], nodes[j], weight='length')
    return(the_array)


# 1. ASSEMBLE THE GRAPH ============================================================
city = ox.gdf_from_place('Montreal, Quebec, Canada')
ox.save_gdf_shapefile(city)
city = ox.project_gdf(city)
# fig, ax = ox.plot_shape(city, figsize=(6,6))

places = ['Le Plateau-Mont Royal, Montreal, Quebec, Canada',
          'Outremont, Montreal, Quebec, Canada',
          'Ville-Marie, Montreal, Quebec, Canada']
G = ox.graph_from_place(places)
G_projected = ox.project_graph(G)
fig, ax = ox.plot_graph(G_projected, fig_height=10)
ox.save_graph_shapefile(G, filename='false')


# 2. assemble the list of stops =============================================================
# check locations with the openstreetmaps.com website, to make sure the titles return a valid place



# 3. create table of distances =============================================================


# 4. write a function that uses the table from part 3 to find the total length of a tour========
def totalLength(arr, lon) -> float:
    length = 0
    for i in range(len(lon) - 1):
        p1 = lon[i]
        p2 = lon[i + 1]
        length = length + arr[p1, p2]
    length = length + arr[lon[0], lon[-1]]
    return length

# 5. find the best tour! ===============================================================



# 6. best is found, now assemble the route ============================================================
G = nx.path_graph(10)
tour = [1, 3, 5]

tour.append(tour[0])
acc = []

for index,node in enumerate(tour):
    if index + 1 <= (len(tour) - 1):
        acc += nx.shortest_path(G, source = node, target = tour[index+1])
        acc.pop(-1)
acc.append(tour[0])
print(acc)

# 7. make a folium map =============================================================
