import random
import math
import matplotlib.pyplot as plt
import networkx as nx

def random_graph_builder(seed, nodecount, height=100, width=100):
    G = nx.Graph()
    random.seed(seed)
    
    for i in range(nodecount):
        identifier = f"Node{i+1}"
        new_cord_x = random.uniform(0, width)
        new_cord_y = random.uniform(0, height)
        G.add_node(identifier, pos=(round(new_cord_x, 2), round(new_cord_y, 2)))

    nodes = list(G.nodes())
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            node1 = nodes[i]
            node2 = nodes[j]

            pos1 = G.nodes[node1]['pos']
            pos2 = G.nodes[node2]['pos']

            dist_x_sq = (pos1[0] - pos2[0]) ** 2
            dist_y_sq = (pos1[1] - pos2[1]) ** 2
            
            weight = round(math.sqrt(dist_x_sq + dist_y_sq), 2)
            
            G.add_edge(node1, node2, weight=weight)

    return G

def nearest_neighbor_tour(graph):
    all_nodes = list(graph.nodes())
    start_node = all_nodes[0]
    
    walked_nodes = [start_node]
    walked_nodes_weights = []
    
    while len(walked_nodes) < len(all_nodes):
        current_node = walked_nodes[-1]
        unvisited_nodes = [node for node in all_nodes if node not in walked_nodes]
        
        nearest_weight = float('inf')
        nearest_neighbor = None

        for neighbor_node in graph.neighbors(current_node):
            if neighbor_node in unvisited_nodes:
                weight = graph[current_node][neighbor_node]['weight']
                if weight < nearest_weight:
                    nearest_weight = weight
                    nearest_neighbor = neighbor_node
        
        walked_nodes.append(nearest_neighbor)
        walked_nodes_weights.append(nearest_weight)
    
    final_weight = graph[walked_nodes[-1]][start_node]['weight']
    walked_nodes_weights.append(final_weight)
    
    return {
        "walked_nodes": walked_nodes + [start_node],
        "walked_nodes_weights": walked_nodes_weights
    }

def visualize_tour(graph, tour_result, total_distance, used_method):
    pos = nx.get_node_attributes(graph, 'pos')
    tour_path = tour_result["walked_nodes"]
    tour_edges = list(zip(tour_path[:-1], tour_path[1:]))

    plt.figure(figsize=(16, 9))
    
    nx.draw_networkx_nodes(graph, pos, node_color='skyblue', node_size=500)
    nx.draw_networkx_labels(graph, pos, font_size=8)
    nx.draw_networkx_edges(graph, pos, edgelist=tour_edges, edge_color='r', width=2.0, label='TSP Tour')

    plt.title("TSP Problem",
              bbox=dict(boxstyle='round,pad=0.5', facecolor='skyblue', alpha=0.5),
              pad=15)
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    
    plt.text(0.01, 1.05, f"Total Distance: {total_distance:.2f}", 
             transform=plt.gca().transAxes, fontsize=12,
             verticalalignment='top', horizontalalignment='left', 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.5))

    plt.text(0.99, 1.05, used_method, 
             transform=plt.gca().transAxes, fontsize=12,
             verticalalignment='top', horizontalalignment='right', 
             fontweight='bold',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.5))
             
    plt.grid(True)
    plt.show()

my_random_graph = random_graph_builder(259, 15)
tour_data = nearest_neighbor_tour(my_random_graph)
total_tour_distance = sum(tour_data['walked_nodes_weights'])

visualize_tour(my_random_graph, tour_data, total_tour_distance, "Nearest Neighbor Heuristic")