import requests
import shutil
from pathlib import Path
import os

# config rapide
# url chiee des donnees open data paris (bruit routier lden jour/nuit)
# si ca change, faut aller fouiller sur opendata.paris.fr
NOISE_DATA_URL = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/bruit-routier-zones-exposees-sur-24h-indicateur-lden/exports/geojson"
RAW_DIR = Path("data/raw")
FILE_PATH = RAW_DIR / "bruit_paris.geojson"

def get_noise_data():
    """
    recupere le gros geojson du bruit routier.
    c'est des polygones (zones de bruit), pas des points.
    """
    
    if FILE_PATH.exists():
        print(f"✅ skip, on a deja le fichier : {FILE_PATH}")
        # on se barre si c'est deja la
        return

    print("⬇️ on tente de dl le geojson bruit (ca peut etre long)...")
    
    try:
        # stream=true pcq le fichier peut faire 100mb+
        # pas envie de kill la ram pour rien
        with requests.get(NOISE_DATA_URL, stream=True) as r:
            r.raise_for_status() # si 404 ou 500, ca pte direct
            with open(FILE_PATH, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        
        print("✨ c bon, fichier recu.")

    except Exception as e:
        # cas classique : l'api a change ou le serveur est en pls
        print(f"❌ galere sur le download : {e}")
        print("⚠️ solution secours : va sur opendata.paris.fr, cherche 'bruit routier lden' et mets le geojson dans data/raw/")

if __name__ == "__main__":
    # check si le dossier existe sinon ca crash
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    get_noise_data()