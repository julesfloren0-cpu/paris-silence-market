# 🔇 PARIS SILENCE MARKET
> **Biopolitique du Capital Sonore : Approche géospatiale des inégalités immobilières.**

![Status](https://img.shields.io/badge/STATUS-PRODUCTION-success?style=for-the-badge)
![Stack](https://img.shields.io/badge/ENGINE-POLARS_%2F_DUCKDB-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/DATA-OPEN_SOURCE-white?style=for-the-badge)

## 1. Le Constat (Thesis)
À Paris, le silence n'est pas une absence de bruit. C'est une **ressource économique rare** qui s'achète au prix fort.
Ce projet ne cherche pas à faire de la "Data Viz" jolie. Il vise à **quantifier le coût exact du silence** en croisant la réalité du marché (les notaires) avec la réalité physique (les décibels).

**Hypothèse :** L'exposition au bruit (Lden) agit comme une taxe invisible sur les classes populaires et un privilège spatial pour l'élite.

## 2. Architecture "Titanium" (Technical Stack)
Pas de Pandas. Pas de boucles `for`. Pas d'approximations.
Ce projet est conçu pour scaler sur des millions de points sans faire fondre le CPU.

* **Ingestion (ETL) :** Python + `Polars` (Rust engine). Streaming HTTP des données DVF pour éviter le crash RAM. Typage strict des schémas.
* **Moteur Spatial :** `DuckDB Spatial`.
    * Pourquoi ? Faire un *Spatial Join* (Point-in-Polygon) sur 75 000 appartements et 200 000 zones de bruit prend 15 minutes avec GeoPandas. Ça prend **4 secondes** avec DuckDB.
    * **Géodésie :** Reprojection dynamique de WGS84 (GPS) vers **Lambert-93 (EPSG:2154)** pour une précision métrique.
* **Visualisation :** `Deck.gl` (WebGL) pour le rendu 3D fluide de l'intégralité du dataset.

## 3. Données & Sources (Hard Data)
On ne travaille pas sur des sondages, mais sur des **preuves**.

1.  **Immobilier (Le Réel Économique) :** Base **DVF (Demandes de Valeurs Foncières)**. Transactions réelles actées par notaire (2024).
    * *Filtres :* Exclusion des ventes symboliques (<50k€), des micro-surfaces (<9m²) et des erreurs de saisie.
2.  **Acoustique (Le Réel Physique) :** Cartographie stratégique du bruit **Bruitparif** (Format Shapefile Vectoriel).

## 4. Résultats : Le Prix du Silence
L'analyse quantitative révèle une sécession urbaine nette. Voici les chiffres sortis du moteur de corrélation :

| Code Bruit | Profil Acoustique | Prix Moyen (2024) | Analyse |
| :--- | :--- | :--- | :--- |
| **33** | **Le Havre (Ultra-Calme)** | **11 399 € / m²** | Impasses privées, Villa Montmorency, Cœurs d'îlots. |
| **12/22** | Quartiers Standards | ~11 200 € / m² | Le standard parisien "vivable". |
| **23** | Zones de Flux | 10 591 € / m² | Rues passantes, boulevards secondaires. |
| **13** | **L'Enfer Sonore** | **10 202 € / m²** | Axes rouges, Périphérique, Gares. |

👉 **L'Insight :**
Le différentiel est de **1 197 € par m²**.
Sur un appartement familial de 80m², **le silence coûte 95 760 €**.
C'est le prix d'une Porsche. Ou de 5 ans de SMIC.

## 5. Reproduction
L'environnement est géré par `uv` (remplaçant moderne de pip) pour garantir la reproductibilité binaire.

```bash
# 1. Cloner & Installer
git clone [https://github.com/ton-user/paris-silence-market](https://github.com/ton-user/paris-silence-market)
uv sync

# 2. Lancer le Pipeline (Ingestion + Calcul)
uv run src/ingestion/fetch_dvf.py
uv run src/processing/match_noise.py

# 3. Voir la Preuve (Dashboard)
uv run streamlit run src/app/app.py