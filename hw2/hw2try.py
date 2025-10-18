# adding libraries 
import osmnx as ox
import random
import matplotlib.pyplot as plt
import networkx as nx
import folium

def get_graph(seed,node_count):

    # get data from open street map as a graph thanks to osmnx
    # place_name = "Görükle Mahallesi ,Nilüfer, Bursa"
    place_name = "Nilüfer, Bursa"
    G = ox.graph_from_place(place_name, network_type='drive')
    # seed based randomization
    random.seed(seed)
    random_nodes = random.sample(list(G.nodes()), node_count)
    # if you want to check random seed unccomment below
    # print(f"chosed node ID's: {random_nodes}")
    return G,random_nodes
def get_weights_betwen_nodes(G,random_nodes):
    #empty wight dictionary
    weights = {}
    #fill weights and routes using node tupples with networkx library function
    #this function help us to get distance betwen chosen nodes
    for i in range(len(random_nodes)):
        for j in range(i+1,len(random_nodes)):
            # in the comment line below is for the check everything is work properly
            # print(f'i = {i}   j = {j}')        
            w =nx.shortest_path_length(G,random_nodes[i],random_nodes[j]) 
            weights[(random_nodes[i],random_nodes[j])] = {'w':w,'r': nx.shortest_path(G, random_nodes[i], random_nodes[j], weight='length')}
            weights[(random_nodes[j],random_nodes[i])] =  {'w':w,'r': nx.shortest_path(G, random_nodes[j], random_nodes[i], weight='length')}
            # in the comment line below is for the check everything is work properly
            # print(f'i = {random_nodes[i]}   j = {random_nodes[j]}')
    # in the comment line below is for the check everything is work properly
    #print(weights)
    return weights
def solve_tsp_heuristic(random_nodes):
    #create empty path and path weights
    walked_nodes=[]
    walked_weights=[]
    #append first node
    walked_nodes.append(random_nodes[0])
    #the following code block runs the Heuristic approach (always chose nearest node)
    while len(walked_nodes) < len(random_nodes):
        nearest_weight = float('inf')
        current_node = walked_nodes[-1]
        unvisited_nodes = [node for node in random_nodes if node not in walked_nodes]
        nearest_node = None
        for node in unvisited_nodes:
            # print("weights[(current_node,node)]['w']")
            # print(weights[(current_node,node)]['w'])
            if weights[(current_node,node)]['w'] < nearest_weight:
                nearest_node = node;
                nearest_weight = weights[(current_node,node)]['w']            
        walked_weights.append(nearest_weight)
        walked_nodes.append(nearest_node)
    #the last node and its weight are appended below.
    walked_weights.append(weights[(walked_nodes[-1],walked_nodes[0])]['w'])
    walked_nodes.append(walked_nodes[0])
    return walked_nodes,walked_weights
def visualize_route(G,walked_nodes,weights,random_nodes):
    #different colors for different steps
    colors = ["red","green","yellow","cyan","magenta","blue"]
    node_colors = []
    node_sizes = []
    for node in G.nodes(data=True):
        if node in random_nodes:
            node_colors.append('yellow')  # attach bright colors to chosen nodes
            node_sizes.append(100)  # show chosen nodes bigger
        else:
            node_sizes.append(0)   # hide other nodes

    #create canvas
    fig, ax = ox.plot_graph(G, show=False)
    #draw routes thanks to libraries
    for i in range(len(walked_nodes)-1):
        ox.plot_graph_route(G, 
                                weights[(walked_nodes[i],walked_nodes[i+1])]['r'], 
                                ax=ax,
                                node_size=0, 
                                route_color=colors[i%6], 
                                route_linewidth=4, 
                                show=False, 
                                close=False)
    #draw ndoes thanks to libraries
    for node in walked_nodes:
        x, y = G.nodes[node]['x'], G.nodes[node]['y']
        ax.text(x, y, str(walked_nodes.index(node) +1 ), 
                color=colors[i%6],
                fontsize=8, 
                ha='center', 
                va='bottom',
                bbox=dict(facecolor='black', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.2'))
    ox.plot_graph(G,ax=ax,
                            node_color=node_colors,
                            node_size=node_sizes,
                            edge_color='gray',
                            bgcolor='black',
                            show=False, 
                            close=False)
    #show canvas thanks to libraries
    plt.show()  
def foilumoutput(G,walked_nodes,weights):
    #magic folium function for html map output
    locations = []
    for node in walked_nodes:
        locations.append((G.nodes[node]['y'],G.nodes[node]['x']))
    center_location = locations[0]
    m = folium.Map(location=center_location, zoom_start=13)
    for i, loc in enumerate(locations):
        if i != len(locations) - 1:
            folium.Marker(
        location=loc,
        popup=f"{i+1}.Durak ",
        icon=folium.Icon(color='blue', icon='star')
    ).add_to(m)

    all_routes = []
    for i in range(len(walked_nodes) - 1):
        route = weights[(walked_nodes[i], walked_nodes[i+1])]['r']
        all_routes.extend(route)
    # print("all_routes")
    # print(all_routes)
    folium_route_coords = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in all_routes]

    folium.PolyLine(
        locations=folium_route_coords,
        color='red',
        weight=4,
        opacity=0.7
    ).add_to(m)
    output_file = "gorukle_tsp_turu.html"
    m.save(output_file)

#main code block
G,random_nodes = get_graph(5,12)
weights = get_weights_betwen_nodes(G,random_nodes)
walked_nodes,walked_weights = solve_tsp_heuristic(random_nodes)
visualize_route(G,walked_nodes,weights,random_nodes)                   
foilumoutput(G,walked_nodes,weights)






