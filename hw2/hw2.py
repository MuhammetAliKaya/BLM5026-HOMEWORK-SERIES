import osmnx as ox
import networkx as nx
import folium
from itertools import combinations

# --- Adım 1: Harita Verisini İndirme ---
# Üzerinde çalışacağımız bölgeyi belirliyoruz.
place_name = "Nilüfer, Bursa, Turkey"
print(f"'{place_name}' için sokak ağı indiriliyor...")

# osmnx ile OpenStreetMap'ten bölgenin araba yolu ağını indiriyoruz.
# Bu işlem internet hızınıza bağlı olarak biraz zaman alabilir.
street_graph = ox.graph_from_place(place_name, network_type='drive')
print("Sokak ağı başarıyla indirildi.")

# --- Adım 2: TSP Düğümlerini (Durakları) Belirleme ---
# Gezilecek durakların adreslerini bir liste olarak tanımlıyoruz.
addresses = [
    "PodyumPark, Bursa",
    "Korupark AVM, Bursa",
    "Fatih Sultan Mehmet Bulvarı, Bursa",
    "Uludağ Üniversitesi, Bursa",
    # "CarrefourSA AVM, Bursa",
    # "Suryapı Marka AVM, Bursa"
]

print("Adresler koordinatlara çeviriliyor ve en yakın düğümler bulunuyor...")
# Adresleri (enlem, boylam) koordinatlarına çeviriyoruz.
# Adresleri tek tek sorgulamak için boş bir liste oluşturalım.
locations = []
print("Adresler tek tek koordinatlara çeviriliyor...")
try:
    for address in addresses:
        # Her bir adresi tekil olarak geocode fonksiyonuna gönderiyoruz.
        point = ox.geocode(address)
        locations.append(point)
        print(f"  - {address} -> Bulundu")
except Exception as e:
    print(f"Hata: '{address}' adresi bulunamadı. Lütfen adresi kontrol edin. Detay: {e}")
    exit()

# Her bir koordinata sokak ağındaki en yakın kavşak (düğüm) ID'sini buluyoruz.
# Bunlar bizim TSP problemimizin "şehirleri" olacak.
tsp_node_ids = ox.nearest_nodes(street_graph, 
                                [point[1] for point in locations], 
                                [point[0] for point in locations])
print("TSP durakları belirlendi:", tsp_node_ids)


# --- Adım 3: Mesafe Matrisini Oluşturma ---
# Bu adım, seçtiğimiz duraklar arasındaki GERÇEK yol mesafelerini hesaplar.
# Bu, ödevin en önemli kısmıdır.

print("Duraklar arası gerçek yol mesafeleri hesaplanıyor...")
# Sadece TSP duraklarımızı ve aralarındaki gerçek mesafeleri içerecek yeni, küçük bir graf oluşturalım.
tsp_graph = nx.Graph()

# Seçtiğimiz her durak çifti için en kısa yol mesafesini hesaplayalım.
for u, v in combinations(tsp_node_ids, 2):
    # networkx ile iki düğüm arasındaki en kısa yolun uzunluğunu (metre cinsinden) buluyoruz.
    distance = nx.shortest_path_length(street_graph, source=u, target=v, weight='length')
    
    # Yeni ve küçük grafımıza bu iki durak arasına mesafeyi kenar olarak ekliyoruz.
    tsp_graph.add_edge(u, v, weight=distance)
    print(f"Mesafe hesaplandı: {u} -> {v} = {distance:.2f} metre")


# --- Adım 4: Heuristiği Uygulama (Bu kısmı kendi kodunuzla entegre edeceksiniz) ---
# İlk ödevde yazdığınız nearest_neighbor_tour fonksiyonunu burada kullanabilirsiniz.
# Girdi olarak `tsp_graph` nesnesini alacak.
# Şimdilik örnek olarak turu basitçe sıralı kabul edelim.
# KENDİ KODUNUZU BURAYA EKLEYİN: tour_node_order = nearest_neighbor_tour(tsp_graph)
# Örnek Çıktı: [12345, 67890, 24680, ...]
tour_node_order = list(tsp_node_ids) + [tsp_node_ids[0]] # Örnek sıralama
print("\nÖrnek tur sırası (kendi algoritmanızla değiştirin):", tour_node_order)


# --- Adım 5: Sonucu `folium` ile Görselleştirme ---
print("Harita oluşturuluyor...")
# Haritayı Bursa'ya odaklayarak başlatalım.
center_location = locations[0]
m = folium.Map(location=center_location, zoom_start=13)

# Tüm durakları haritaya birer işaretçi olarak ekleyelim.
for i, (address, loc) in enumerate(zip(addresses, locations)):
    folium.Marker(
        location=loc,
        popup=f"<b>{i+1}. Durak</b><br>{address.split(',')[0]}",
        icon=folium.Icon(color='blue', icon='star')
    ).add_to(m)

# Turdaki her bir adımı (örneğin Durak 1 -> Durak 2) haritaya çizelim.
# Bunun için iki durak arasındaki en kısa yolun geçtiği TÜM kavşakları bulmamız gerekir.
for i in range(len(tour_node_order) - 1):
    start_node = tour_node_order[i]
    end_node = tour_node_order[i+1]
    
    # İki durak arasındaki en kısa yolu (düğüm listesi olarak) bul
    route_nodes = nx.shortest_path(street_graph, source=start_node, target=end_node, weight='length')
    
    # Bu düğümlerin koordinatlarını al
    route_coords = [[street_graph.nodes[node]['y'], street_graph.nodes[node]['x']] for node in route_nodes]
    
    # Bu koordinatları haritaya bir çizgi olarak ekle
    folium.PolyLine(
        locations=route_coords,
        color='red',
        weight=4,
        opacity=0.7
    ).add_to(m)

# Haritayı bir HTML dosyası olarak kaydedelim.
output_file = "bursa_tsp_turu.html"
m.save(output_file)
print(f"\nHarita başarıyla '{output_file}' dosyasına kaydedildi. Bu dosyayı tarayıcıda açabilirsiniz.")