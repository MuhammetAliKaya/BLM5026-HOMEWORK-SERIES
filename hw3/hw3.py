# adding libraries 
import osmnx as ox
import random
import matplotlib.pyplot as plt
import networkx as nx
import folium
import time


from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def get_graph():

    # get data from open street map as a graph thanks to osmnx
    # place_name = "Görükle Mahallesi ,Nilüfer, Bursa"
    place_name = "Nilüfer, Bursa"
    G = ox.graph_from_place(place_name, network_type='drive')
    # seed based randomization
    
    # if you want to check random seed unccomment below
    # print(f"chosed node ID's: {random_nodes}")
    return G

def get_random_nodes(G,seed,node_count):
    random.seed(seed)
    random_nodes = random.sample(list(G.nodes()), node_count)
    return random_nodes
def get_weights_betwen_nodes(G,random_nodes):
    #empty wight dictionary
    weights = {}
    #fill weights and routes using node tupples with networkx library function
    #this function help us to get distance betwen chosen nodes
    for i in range(len(random_nodes)):
        for j in range(i+1,len(random_nodes)):
            # in the comment line below is for the check everything is work properly
            # print(f'i = {i}   j = {j}')   
            try:     
                nx.shortest_path_length(G,random_nodes[i],random_nodes[j])
                nx.shortest_path(G, random_nodes[j], random_nodes[i])
            except nx.NetworkXNoPath:
                print("some osmnx prroblems about finding way node to node")
                return False , weights

                
            w = nx.shortest_path_length(G,random_nodes[i],random_nodes[j]) 
            weights[(random_nodes[i],random_nodes[j])] = {'w':w,'r': nx.shortest_path(G, random_nodes[i], random_nodes[j], weight='length')}
            weights[(random_nodes[j],random_nodes[i])] =  {'w':w,'r': nx.shortest_path(G, random_nodes[j], random_nodes[i], weight='length')}
            # in the comment line below is for the check everything is work properly
            # print(f'i = {random_nodes[i]}   j = {random_nodes[j]}')
    # in the comment line below is for the check everything is work properly
    #print(weights)
    return True , weights
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
    index_list=[]
    for node in walked_nodes:
        index_list.append(random_nodes.index(node))

    print(f"heuristik path ditance: {sum(walked_weights)}")
    print(f"heuristik path: {index_list}")
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
def create_distance_matrix(weights,random_nodes):
    w_matrix = [[0] * len(random_nodes) for _ in range(len(random_nodes))]
    # print("ilk hali")
    # print(w_matrix)

    for i in range(len(random_nodes)):
        for j in range(len(random_nodes)):
            # print(f"[{i}][{j}]")
            if i == j:
                w_matrix[i][j] = 0
            else:
                w_matrix[i][j] = weights[(random_nodes[i],random_nodes[j])]['w']
                # print(weights[(random_nodes[i],random_nodes[j])]['w'])

    # print('w_matrix')
    # print(w_matrix)
    return w_matrix
def solve_tsp_ortools(random_nodes,dist_matrix):
    manager = pywrapcp.RoutingIndexManager(len(dist_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

        # 2. Mesafe Callback Fonksiyonunu Tanımla
    def distance_callback(from_index, to_index):
        """Matristen iki nokta arasındaki mesafeyi döndürür."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return dist_matrix[from_node][to_node]

    # 3. Maliyet (Mesafe) Fonksiyonunu Modele Kaydet
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # 4. Çözümü Başlat
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    solution = routing.SolveWithParameters(search_parameters)

    def get_route_from_solution(manager, routing, solution):
        vehicle_id = 0
        # Aracın başlangıç noktasının solver'daki iç indeksini al
        index = routing.Start(vehicle_id)
        # Rota ve mesafe değişkenlerini başlat
        route = []
        route_distance = 0
        # Döngü, rota tamamlanana kadar (yani bitiş noktasına varana kadar) devam eder
        while not routing.IsEnd(index):
            # Solver'ın iç indeksini, sizin matrisinizdeki gerçek düğüm indeksine çevir
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            
            # Bir sonraki adıma geçmek için mevcut indeksi kaydet
            previous_index = index
            # Çözümden bir sonraki durağın indeksini öğren
            index = solution.Value(routing.NextVar(index))
            
            # Bu adımın (arc) mesafesini toplam mesafeye ekle
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
        # Döngü bittiğinde, son durak (depoya dönüş) hala 'index' değişkenindedir.
        # Onu da rotaya ekle.
        route.append(manager.IndexToNode(index))
        
        return route, route_distance

    final_route, final_distance = get_route_from_solution(manager, routing, solution)
    
    print(f"Optimize Edilmiş Rota: {final_route}")
    print(f"Toplam Mesafe: {final_distance}")

    return final_distance

efficiency_diff = []
#main code block

G = get_graph()
for i in range(12,42):
    print(f"{i}. try and compharation")
    random_nodes = get_random_nodes(G,i,10)
    status,weights = get_weights_betwen_nodes(G,random_nodes)
    while_iteration = 0
    while status is False:
        random_nodes = get_random_nodes(G,while_iteration*(30+i+while_iteration),10)
        status,weights = get_weights_betwen_nodes(G,random_nodes)
        while_iteration+=1

    start_time = time.perf_counter()
    walked_nodes,walked_weights = solve_tsp_heuristic(random_nodes)
    end_time = time.perf_counter()
    print(f'heuristic_func_work_time {end_time - start_time}')
    # visualize_route(G,walked_nodes,weights,random_nodes)     
    start_time = time.perf_counter()              
    dist_matrix = create_distance_matrix(weights,random_nodes)
    final_distance = solve_tsp_ortools(random_nodes,dist_matrix)
    end_time = time.perf_counter()
    print(f'or_tools_func_work_time {end_time - start_time}')

    # foilumoutput(G,walked_nodes,weights)
    efficiency_diff.append(((sum(walked_weights)-final_distance)/final_distance)*100)
    print(f'or tools solution %{((sum(walked_weights)-final_distance)/final_distance)*100} beter than heuristic')
    print("-----------------------------------")

print("final conculsion")
print(efficiency_diff)