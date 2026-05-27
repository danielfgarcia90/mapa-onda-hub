import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2

# ===== CONFIG =====
st.set_page_config(page_title="Mapa Diretor", layout="wide")
st.title("Cobertura por Área - Piloto HUB")

# ===== LOAD DATA =====
postos = pd.read_csv("postos_full.csv")

# ===== ANALISTAS =====
analistas = pd.DataFrame([
["Ana Mereu","Consumidor",-22.350212627482474,-47.38617494641834],
["Beatriz","Infra",-23.186911398457767,-50.650036859404075],
["Bianca","Consumidor",-22.691597722206897,-47.6853416133397],
["Breno","N2 Tech",-22.743565115420342,-47.35391914070124],
["Bruno","Revenda",-22.8929554761234,-47.07925423114696],
["Carlos","Infra",-22.740249584098223,-47.58879914314848],
["Daniel","Infra",-23.177570198984814,-47.343131760745734],
["Daniela","Rollout",-23.563286338727615,-46.482293601770415],
["Diego","N2 Tech",-22.565127487003185,-47.420938913769774],
["Deividi","N2 Tech",-22.892409456204923,-43.219809988105986],
["Giovana","Consumidor",-22.75643276967686,-47.62300755612971],
["Isa Galluce","Rollout",-22.76694427691573,-47.59934940842888],
["Isa Siqueira","Rollout",-23.095862743153933,-47.2560416131461],
["Jessica","Revenda",-22.676975116873596,-47.68248922431733],
["Joao Paulo","Consumidor",-22.742013267085245,-47.624648218567366],
["Juliana Coutinho","Rollout",-22.68054595996875,-47.62467961369291],
["Juliana Ventura","Infra",-23.701827579482423,-46.56198767679129],
["Laura","Consumidor",-22.689835091919765,-47.67174242781066],
["Leo Silva","N2 Tech",-22.751842124821284,-47.63059076026638],
["Lorena","N2 Tech",-19.920833163594967,-43.98049966645257],
["Mariana","Revenda",-22.723155128659194,-47.64443796914713],
["Marla","Revenda",-22.751420710658735,-47.63489332119582],
["Matheus","Infra",-22.643146727360982,-54.82062263197637],
["Moroni","Revenda",-22.344772220492445,-47.37414001656212],
["Romulo","Infra",-3.921524414327905,-38.59880675395854],
["Romulo Baciega","Revenda",-22.700189920975458,-47.66819315760095],
["Sotelo","Infra",-22.728590600550028,-47.61239429972871],
["Thalles","Infra",-23.22996742420059,-46.84475682152807]
], columns=["Analista","Area","Lat","Lon"])

# ===== RAIO DINÂMICO =====
raio_km = st.sidebar.slider(
    "Raio de cobertura (km)",
    min_value=10,
    max_value=100,
    value=35,
    step=5
)

# ===== FILTROS =====
areas = st.sidebar.multiselect(
    "Selecione as Áreas",
    options=sorted(analistas["Area"].unique()),
    default=list(analistas["Area"].unique())
)

analistas_area = analistas[analistas["Area"].isin(areas)]

nomes = sorted(analistas_area["Analista"].unique())

analistas_select = st.sidebar.multiselect(
    "Selecione os Analistas",
    options=nomes,
    default=nomes
)

analistas_sel = analistas_area[
    analistas_area["Analista"].isin(analistas_select)
]

# ===== FUNÇÃO DISTÂNCIA =====
def dist(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1-a))

# ===== COBERTURA =====
postos_cobertos = []
cobertos_set = set()

for i, p in postos.iterrows():
    for _, a in analistas_sel.iterrows():
        if dist(a['Lat'], a['Lon'], p['Latitude'], p['Longitude']) <= raio_km:
            postos_cobertos.append(p)
            cobertos_set.add(i)
            break

postos_cobertos_df = pd.DataFrame(postos_cobertos)
cobertos = len(cobertos_set)


# ===== KPI =====
col1, col2, col3 = st.columns(3)
col1.metric("Cobertos", cobertos)
col2.metric("Total", len(postos))
col3.metric("Cobertura %", round(cobertos / len(postos) * 100, 1))

# ===== DOWNLOAD (MOVER PRA CÁ) =====

csv = postos_cobertos_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label=f"📥 Baixar Postos Cobertos ({len(postos_cobertos_df)})",
    data=csv,
    file_name="postos_cobertos.csv",
    mime="text/csv"
)

# ===== MAPA =====
cores_area = {
    "Consumidor": "green",
    "Infra": "blue",
    "N2 Tech": "purple",
    "Revenda": "orange",
    "Rollout": "cadetblue"
}

m = folium.Map(location=[-22.8, -47.5], zoom_start=5)

# círculos analistas
for _, a in analistas_sel.iterrows():
    cor = cores_area.get(a["Area"], "blue")

    folium.Circle(
        location=[a['Lat'], a['Lon']],
        radius=raio_km * 1000,
        color=cor,
        fill=True,
        fill_opacity=0.15,
        popup=f"{a['Analista']} | {a['Area']} | {raio_km} km"
    ).add_to(m)

# postos
for i, p in postos.iterrows():
    color = "green" if i in cobertos_set else "red"
    folium.CircleMarker(
        location=[p['Latitude'], p['Longitude']],
        radius=3,
        color=color
    ).add_to(m)

st_folium(m, width=1200, height=700)
