import streamlit as st
import polars as pl
import pydeck as pdk

# CONFIGURATION DE LA PAGE
st.set_page_config(layout="wide", page_title="Paris Silence Market", page_icon="🔇")

# CSS "DARK MODE ACADEMIC"
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    h1 {font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: -1px;}
    .metric-card {background-color: #1E1E1E; padding: 20px; border-radius: 10px; border-left: 5px solid #00FF00;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    # On charge la donnée brute Titanium
    df = pl.read_parquet("data/processed/final_dataset_ready.parquet")
    
    # MAPPING DES COULEURS (Data-Driven Design)
    # Basé sur l'analyse : 13 = Moins Cher (Rouge), 33 = Plus Cher (Vert)
    # Format PyDeck : [R, G, B, Alpha]
    
    def get_color(code):
        if code == 13: return [255, 0, 0, 180]    # Rouge (10.2k€ - Mass Market)
        if code == 23: return [255, 100, 0, 180]  # Orange
        if code == 12: return [0, 255, 0, 180]    # Vert Vif (11.2k€ - Premium)
        if code == 33: return [0, 255, 150, 200]  # Vert/Bleu (11.4k€ - Elite)
        return [200, 200, 200, 100]               # Gris (Autres)

    # On applique la couleur en Python (plus rapide que JS pour 70k points)
    # Note : Polars est rapide mais PyDeck veut souvent du Pandas ou des listes
    df_pandas = df.to_pandas()
    df_pandas["color"] = df_pandas["noise_code"].apply(get_color)
    
    return df_pandas

def main():
    # HEADER
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔇 LE SILENCE EST UN LUXE.")
        st.markdown("""
        **Étude sociologique quantitative sur la valorisation du silence à Paris.** *Croisement : 74 677 Transactions (DVF) x Cartographie Bruit (Bruitparif).*
        """)
    with col2:
        st.metric(label="Coût du Silence (Différentiel)", value="60 000 €", delta="pour 50m²")

    # CHARGEMENT
    try:
        data = load_data()
    except Exception as e:
        st.error(f"Erreur data : {e}")
        return

    # CARTE 3D (PYDECK)
    layer = pdk.Layer(
        "ScatterplotLayer", # On affiche chaque vente comme un point
        data,
        get_position=["longitude", "latitude"],
        get_color="color",
        get_radius=30, # Taille du point
        pickable=True,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=1,
        radius_min_pixels=1,
        radius_max_pixels=100,
    )

    # VUE INITIALE (Paris Centre)
    view_state = pdk.ViewState(
        latitude=48.8566,
        longitude=2.3522,
        zoom=12,
        pitch=0,
    )

    # RENDU
    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "{prix_m2} €/m² (Code Bruit: {noise_code})"},
        map_style="mapbox://styles/mapbox/dark-v10" # Style sombre
    ))

    # LÉGENDE
    st.markdown("### 🧬 Analyse des Clusters")
    colA, colB, colC = st.columns(3)
    colA.info("🔴 **Cluster 13 (La Ville)** : 10 200 €/m². Le bruit standard.")
    colB.warning("🟠 **Cluster 23 (Transition)** : 10 600 €/m².")
    colC.success("🟢 **Cluster 33 (Le Havre)** : 11 400 €/m². Le calme absolu.")

    st.caption("Architecture : Rust (Polars) + C++ (DuckDB) + WebGL (Deck.gl). Code by L'Architecte Radical.")

if __name__ == "__main__":
    main()