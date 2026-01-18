import requests
import polars as pl
from pathlib import Path
import shutil
import os

# CONFIG
BASE_URL = "https://files.data.gouv.fr/geo-dvf/latest/csv"
YEARS = [2024] # On focus sur 2024 pour l'instant pour aller vite
TARGET_DEPT = "75"
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

def download_and_convert(year: int):
    filename = "full.csv.gz"
    url = f"{BASE_URL}/{year}/{filename}"
    local_gz_path = RAW_DIR / f"dvf_{year}.csv.gz"
    output_parquet = PROCESSED_DIR / f"dvf_{year}_paris.parquet"

    # 1. DOWNLOAD (Si pas déjà là)
    if not local_gz_path.exists():
        print(f"⬇️  [DOWNLOAD] {year}...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_gz_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
    else:
        print(f"✅ [CACHE] Fichier {year} déjà téléchargé.")

    print(f"⚙️  [PROCESS] Conversion & Filtrage {year} (Mode Bulldozer)...")
    
    # 2. LECTURE ROBUSTE
    # On force les types critiques en String pour éviter les bugs "75" vs 75
    try:
        q = (
            pl.scan_csv(
                local_gz_path, 
                separator=",", 
                ignore_errors=True,
                infer_schema_length=0, # On n'infère rien, on lit tout en string au début pour pas crasher
                dtypes={
                    "valeur_fonciere": pl.Float64,
                    "surface_reelle_bati": pl.Float64,
                    "latitude": pl.Float64,
                    "longitude": pl.Float64,
                    # Tout le reste sera du String par défaut
                }
            )
            # 3. FILTRAGE AGRESSIF
            # On cast explicitement la colonne dept en string avant de comparer
            .filter(pl.col("code_departement").cast(pl.String) == TARGET_DEPT)
            .select([
                "id_mutation", "date_mutation", "valeur_fonciere", 
                "code_postal", "nom_commune", "code_departement",
                "type_local", "surface_reelle_bati", 
                "latitude", "longitude" 
            ])
        )

        # Exécution
        q.sink_parquet(output_parquet)
        
        # VERIFICATION IMMEDIATE
        df_verif = pl.read_parquet(output_parquet)
        count = len(df_verif)
        if count == 0:
            print(f"⚠️ ALERTE : 0 lignes trouvées pour Paris ! Le filtre a tout tué.")
        else:
            print(f"✨ [SUCCESS] {count} transactions trouvées pour Paris.")

    except Exception as e:
        print(f"❌ ERREUR POLARS : {e}")

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for year in YEARS:
        download_and_convert(year)

if __name__ == "__main__":
    main()