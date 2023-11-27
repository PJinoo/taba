import folium
import pandas as pd
from folium.plugins import MarkerCluster

file = r'C:\Users\ParkJinoh\Desktop\Crowlling\output_yongin.csv'
file = file.replace('\\','//')

safezone = pd.read_csv(file,encoding='cp949')
x = []
y = []
safezone_name = []
for i in range(len(safezone['xcord'])):
    x.append(safezone['ycord'][i])
    y.append(safezone['xcord'][i])
    safezone_name.append(safezone['vt_acmdfclty_nm'][i])

print('x갯수: ',len(x))
print('y갯수: ',len(y))
map = folium.Map(location=[37.321559,127.126960], zoom_start=14)
marker_cluster = MarkerCluster().add_to(map)

for i in range(len(x)):
    folium.Marker([x[i],y[i]], popup=safezone_name[i], icon=folium.Icon(color='blue', icon='info-sign')).add_to(marker_cluster)
map.save("safezone.html")