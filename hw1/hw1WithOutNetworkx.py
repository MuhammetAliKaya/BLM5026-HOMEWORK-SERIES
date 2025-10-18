import random
import math
import json
import matplotlib.pyplot as plt

class Graph:
    def __init__(self):

        self.adjacency_list = {}
        self.node_info = {}

    def add_node(self, identifier, new_cord_x, new_cord_y):
        # Düğüm zaten varsa işlem yapma (veya güncelleme).
        if identifier not in self.adjacency_list:

            self.adjacency_list[identifier] = []
            self.node_info[identifier] = {
                'x': new_cord_x,
                'y': new_cord_y,
                'id': identifier
            }

    def add_edge(self, node1, node2, weight=1):
        if node1 in self.adjacency_list and node2 in self.adjacency_list:

            self.adjacency_list[node1].append({
                'target_node': node2,
                'weight': weight
            })
 
            self.adjacency_list[node2].append({
                'target_node': node1,
                'weight': weight
            })

def random_graph_builder(seed, nodecount, height=100, width=100):
    random.seed(seed)
    g = Graph()
    
    for i in range(nodecount):
        identifier = f"Node{i+1}"
        new_cord_x = random.uniform(0, width)
        new_cord_y = random.uniform(0, height)
        g.add_node(identifier, round(new_cord_x,2) ,round(new_cord_y,2))

    nodes = list(g.adjacency_list.keys())
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            node1 = nodes[i]
            node2 = nodes[j]


            info1 = g.node_info[node1]
            info2 = g.node_info[node2]

            dist_x_sq = (info1['x'] - info2['x']) ** 2
            dist_y_sq = (info1['y'] - info2['y']) ** 2
            
            weight =round( math.sqrt(dist_x_sq + dist_y_sq),2)
            
            g.add_edge(node1, node2, weight)

    return g

def shortest_route(graph):
    print("shorter route start")
    walked_nodes = []
    walked_nodes_weights = []
    walked_nodes.append(all_node_names[0])
    print(walked_nodes)

    while len(walked_nodes) < len(all_node_names):
        unvisited_nodes = [node for node in all_node_names if node not in walked_nodes]

        nearest_weight = math.inf
        nearest_neighbour = None

        for neighbour in graph.adjacency_list[walked_nodes[-1]]:
            if neighbour["target_node"] in unvisited_nodes and neighbour["weight"] < nearest_weight:
                nearest_weight = neighbour["weight"]
                nearest_neighbour = neighbour["target_node"]
            print("neighbour")
            print(neighbour)

        walked_nodes.append(nearest_neighbour)
        walked_nodes_weights.append(nearest_weight)
        print("walked_nodes")
        print(walked_nodes)

    if len(walked_nodes) == len(all_node_names):
        walked_nodes[-1]

        final_weight = None

        for neighbor in graph.adjacency_list[walked_nodes[-1]]:
            if neighbor['target_node'] == walked_nodes[0] :
                final_weight = neighbor['weight']
                break

        walked_nodes_weights.append(final_weight)
        return {"walked_nodes": walked_nodes + [walked_nodes[0]],"walked_nodes_weights": walked_nodes_weights }

def visualize_tour(graph, tour_result, used_method):
    node_info = graph.node_info
    tour_path = tour_result["walked_nodes"]

    x_coords = [info['x'] for info in node_info.values()]
    y_coords = [info['y'] for info in node_info.values()]
    node_labels = list(node_info.keys())

    plt.figure(figsize=(16, 8))

    # 1. Tüm düğümleri mavi noktalar olarak çiz
    plt.scatter(x_coords, y_coords, s=100, color='skyblue', label='Cities')

    # 2. Düğümlerin üzerine isimlerini yazdır
    for i, label in enumerate(node_labels):
        plt.text(x_coords[i], y_coords[i] + 1.5, label, fontsize=9, ha='center')

    # 3. Bulunan turu kırmızı çizgilerle çiz
    # Turun geçtiği düğümlerin koordinatlarını sırasıyla al
    tour_x = [node_info[node_id]['x'] for node_id in tour_path]
    tour_y = [node_info[node_id]['y'] for node_id in tour_path]

    # Rota boyunca çizgileri çiz. `plot` fonksiyonu noktaları sırasıyla birleştirir.
    plt.plot(tour_x, tour_y, 'r-', label='TSP tour')

    # 4. Başlangıç noktasını farklı bir renkle işaretle
    start_node_id = tour_path[0]
    plt.scatter(node_info[start_node_id]['x'], node_info[start_node_id]['y'], s=150, color='green', marker='*', label='Start/End')

    # 5. Grafiği düzenle ve göster
    plt.title("TSP Problem",
          bbox=dict(boxstyle='round,pad=0.5', facecolor='skyblue', alpha=0.5),
          pad=15)
    plt.xlabel("X Cordinate")
    plt.ylabel("Y Cordinate")
    plt.legend()
    plt.text(0, 1.05, f"total distance {sum(sr['walked_nodes_weights'])}", transform=plt.gca().transAxes, fontsize=12,
             verticalalignment='top',
              horizontalalignment='left', bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.5))

    plt.text(1, 1.05, used_method , transform=plt.gca().transAxes, fontsize=12,
             verticalalignment='top', horizontalalignment='right', bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.5))
    plt.grid(True)
    plt.show()

my_random_graph = random_graph_builder(259, 15)
all_node_names = []
for key in my_random_graph.node_info.keys(): 
    all_node_names.append(key)
    print(my_random_graph.node_info[key]['x'])

sr = shortest_route(my_random_graph)
visualize_tour(my_random_graph, sr , "heroustic approach/shortest node in all case" )


