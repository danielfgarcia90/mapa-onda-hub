import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2

st.set_page_config(page_title="Mapa de Cobertura", layout="wide")

st.title("📍 Simulador de Cobertura por Área")

postos = pd.read_csv("postos.csv")

analistas = pd.DataFrame([
["Ana Mereu","Consumidor",-22.3502126,-47.3861749],
["Beatriz","Infra",-23.1869113,-50.6500368],
["Bianca","Consumidor",-22.6915977,-47.6853416],
["Breno","N2 Tech",-22.7435651,-47.3539191],
["Bruno","Revenda",-22.8929554,-47.0792542]
], columns=["Analista","Area","Lat","Lon"])

areas = st.sidebar.multiselect("Áreas", analistas["Area"].unique(), default=list(analistas["Area"].unique()))
analistas_sel = analistas[analistas["Area"].isin(areas)]

# distancia
def dist(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2*R*atan2(sqrt(a), sqrt(1-a))

# cobertura
cobertos = 0
for _, p in postos.iterrows():
    for _, a in analistas_sel.iterrows():
        if dist(a['Lat'], a['Lon'], p['Latitude'], p['Longitude']) <= 35:
            cobertos += 1
            break

col1, col2, col3 = st.columns(3)
col1.metric("Postos Cobertos", cobertos)
col2.metric("Total", len(postos))
col3.metric("Cobertura %", round(cobertos/len(postos)*100,1))

m = folium.Map(location=[-22.8, -47.5], zoom_start=6)

for _, row in analistas_sel.iterrows():
    folium.Circle([row['Lat'],row['Lon']], radius=35000).add_to(m)

for _, row in postos.iterrows():
    folium.Marker([row['Latitude'],row['Longitude']]).add_to(m)

st_folium(m, width=1200, height=700)
