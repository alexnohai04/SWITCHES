import matplotlib.pyplot as plt
import geopandas as gpd
from geopy.geocoders import Nominatim
import time

def get_lat_lon(city, region, country):
    geolocator = Nominatim(user_agent="traceroute_plotter")
    location = geolocator.geocode(f"{city}, {region}, {country}")
    if location:
        return location.latitude, location.longitude
    return 0, 0

# Lista de site-uri pentru care avem rutele
sites = ["Google", "China", "South_Africa", "Australia"]

for site in sites:
    latitudes = []
    longitudes = []
    cities = []
    regions = []
    countries = []

    # Citim datele din fișierele de rezultate
    with open(f"{site}_traceroute.txt", 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 5:
                ttl, ip, city, region, country = parts
                if city != 'Unknown' and region != 'Unknown' and country != 'Unknown':
                    cities.append(city)
                    regions.append(region)
                    countries.append(country)

                    lat, lon = get_lat_lon(city, region, country)
                    if lat != 0 and lon != 0:  # Doar dacă locația este cunoscută
                        latitudes.append(lat)
                        longitudes.append(lon)
                    time.sleep(1)  # Pauză pentru a evita limitările API-ului

    # Generăm harta folosind GeoPandas și Matplotlib
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    world.boundary.plot(ax=ax)
    plt.scatter(longitudes, latitudes, color='red', zorder=5)

    # Etichetăm punctele de pe hartă
    for i, txt in enumerate(cities):
        ax.annotate(txt, (longitudes[i], latitudes[i]), fontsize=9)

    plt.title(f"Traceroute Path for {site}")
    plt.savefig(f"{site}_traceroute_map.png")
    plt.show()

