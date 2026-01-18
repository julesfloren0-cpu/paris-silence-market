import duckdb
from pathlib import Path

# CONFIGURATION
DVF_PATH = "data/processed/dvf_2024_paris.parquet"
SHAPEFILE_PATH = "data/raw/AirBruit_2024.shp"
OUTPUT_PARQUET = "data/processed/final_dataset_ready.parquet"

def run_spatial_join():
    print("🚀 Démarrage du Moteur de Corrélation (Titanium V-FINAL)")
    
    if not Path(DVF_PATH).exists() or not Path(SHAPEFILE_PATH).exists():
        print("❌ Fichiers manquants. Vérifie data/processed et data/raw")
        return

    con = duckdb.connect()
    con.install_extension("spatial")
    con.load_extension("spatial")

    try:
        con.sql(f"CREATE OR REPLACE TABLE dvf AS SELECT * FROM '{DVF_PATH}'")
        con.sql(f"CREATE OR REPLACE TABLE noise_zones AS SELECT * FROM ST_Read('{SHAPEFILE_PATH}')")

        print("... Exécution du Spatial Join (Correction Axes : Lat/Lon)")
        
        # LA REQUÊTE CORRIGÉE AVEC LE BON ORDRE DES AXES (Test B)
        query = """
            SELECT 
                d.valeur_fonciere,
                d.surface_reelle_bati,
                CAST(d.valeur_fonciere / NULLIF(d.surface_reelle_bati, 0) AS INTEGER) as prix_m2,
                d.latitude,
                d.longitude,
                d.code_postal,
                n."9" as noise_code
            FROM dvf d, noise_zones n
            WHERE 
                ST_Within(
                    -- FIX ICI : d.latitude EN PREMIER
                    ST_Transform(ST_Point(d.latitude, d.longitude), 'EPSG:4326', 'EPSG:2154'), 
                    n.geom
                )
                AND d.surface_reelle_bati > 9
                AND d.valeur_fonciere > 50000
                AND (d.valeur_fonciere / d.surface_reelle_bati) BETWEEN 3000 AND 30000
        """
        
        con.sql(f"COPY ({query}) TO '{OUTPUT_PARQUET}' (FORMAT 'PARQUET', CODEC 'ZSTD')")
        
        # VERDICT
        print("✅ Traitement terminé. Analyse des résultats :")
        
        stats = con.sql(f"""
            SELECT 
                noise_code, 
                COUNT(*) as volume_ventes, 
                ROUND(AVG(prix_m2)) as prix_moyen_m2 
            FROM '{OUTPUT_PARQUET}' 
            GROUP BY noise_code 
            ORDER BY prix_moyen_m2 DESC
        """).fetchall()

        if not stats:
            print("⚠️ 0 correspondances. C'est impossible avec le diagnostic positif.")
        else:
            print("\n📊 TABLEAU DE CORRÉLATION (Bruit vs Prix) :")
            print(" CODE | VENTES  | PRIX MOYEN (€/m²)")
            print("-" * 35)
            for row in stats:
                print(f" {row[0]:<4} | {row[1]:<7} | {row[2]} €")
            print("-" * 35)

    except Exception as e:
        print(f"❌ CRASH : {e}")
    
    con.close()

if __name__ == "__main__":
    run_spatial_join()