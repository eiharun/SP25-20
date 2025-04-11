import csv
import folium 
from IPython.display import display
gs_coords = (37.23076314126423, -80.42473322034601)

with open("4-8-log.csv", "r") as f:
    reader = csv.reader(f, delimiter=",")
    
map = folium.Map(location=[21.39, 84.29], zoom_start=13)