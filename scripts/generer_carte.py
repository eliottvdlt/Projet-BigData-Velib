import webbrowser
import folium
import pymongo
import sys
import os

# --- 0. IMPORTATION DES SECRETS ---
# On remonte d'un dossier (de 'scripts' à la racine) pour trouver config.py
try:
    sys.path.append('..') 
    import config
except ImportError:
    print("ERREUR : Le fichier 'config.py' est introuvable à la racine du projet.")
    print("Veuillez le créer avant de lancer ce script.")
    sys.exit()


# --- 1. CONNEXION À MONGODB ATLAS (Cloud) ---

# LA CHAÎNE SECRÈTE A ÉTÉ SUPPRIMÉE D'ICI
print("Connexion à MongoDB Atlas en cours...")
try:
    # On utilise la variable importée depuis le fichier config
    client = pymongo.MongoClient(config.ATLAS_CONNECTION_STRING) 
    db = client["velib_cloud_db"] 
    collection = db["stations"]
    client.admin.command('ping') 
    print("Succès : Connecté à MongoDB Atlas.")
except Exception as e:
    print(f"ERREUR : Impossible de se connecter à Atlas. {e}")
    sys.exit()

# --- NOUVELLE PARTIE : STATISTIQUES AVANCÉES ---
print("\n--- ANALYSE STATISTIQUE AVANCÉE ---")
try:
    # --- Stat 1: Top 5 des communes (inchangée) ---
    pipeline_top_communes = [
        {"$group": {"_id": "$nom_arrondissement_communes", "totalStations": {"$sum": 1}}},
        {"$sort": {"totalStations": -1}},
        {"$limit": 5}
    ]
    top_communes = list(collection.aggregate(pipeline_top_communes))
    print("Top 5 des communes par nombre de stations :")
    for commune in top_communes:
        print(f"  - {commune['_id']}: {commune['totalStations']} stations")

    # --- Stat 2: Analyse du parc de vélos (Mécanique vs Électrique) ---
    pipeline_types_velos = [
        {
            "$group": {
                "_id": "types_de_velos",
                "totalMechanical": {"$sum": "$mechanical"},
                "totalEbike": {"$sum": "$ebike"},
                "totalBikesAvailable": {"$sum": "$numbikesavailable"}
            }
        }
    ]
    stats_velos = list(collection.aggregate(pipeline_types_velos))[0]
    total_velos = stats_velos['totalMechanical'] + stats_velos['totalEbike']
    
    # Sécurité: éviter la division par zéro si le parc est vide
    if total_velos > 0:
        pct_meca = (stats_velos['totalMechanical'] / total_velos) * 100
        pct_ebike = (stats_velos['totalEbike'] / total_velos) * 100
        print("\nAnalyse du parc de vélos disponibles (actuellement) :")
        print(f"  - Mécaniques: {stats_velos['totalMechanical']} ({pct_meca:.1f}%)")
        print(f"  - Électriques: {stats_velos['totalEbike']} ({pct_ebike:.1f}%)")
        print(f"  - Total (calculé): {total_velos} vélos")
    else:
        print("\nAnalyse du parc de vélos : 0 vélos disponibles.")

    # --- Stat 3: Analyse de "Tension" (les 10 zones les plus en manque de vélos) ---
    pipeline_tension = [
        {
            "$match": {"capacity": {"$gt": 0}, "is_renting": "OUI"} # Évite les stations fermées ou division par zéro
        },
        {
            "$group": {
                "_id": "$nom_arrondissement_communes",
                "avgCapacity": {"$avg": "$capacity"},
                "avgBikesAvailable": {"$avg": "$numbikesavailable"}
            }
        },
        {
            "$addFields": { # On crée un nouveau champ (pourcentage de disponibilité)
                "pctDisponibilite": {
                    "$divide": ["$avgBikesAvailable", "$avgCapacity"]
                }
            }
        },
        {"$sort": {"pctDisponibilite": 1}}, # 1 = Tri ascendant (les pires en premier)
        {"$limit": 10}
    ]
    
    zones_en_tension = list(collection.aggregate(pipeline_tension))
    print("\nTop 10 des zones les plus en 'tension' (manque de vélos) :")
    for zone in zones_en_tension:
        pct = zone['pctDisponibilite'] * 100
        print(f"  - {zone['_id']}: {pct:.1f}% de vélos disponibles en moyenne")

    # --- Stat 4: Stations "Fantômes" (vides) et "Saturées" (pleines) ---
    stations_vides = collection.count_documents({"numbikesavailable": 0, "is_renting": "OUI"})
    stations_pleines = collection.count_documents({"numdocksavailable": 0, "is_returning": "OUI"})
    total_stations = collection.count_documents({"is_installed": "OUI"})

    print("\nAnalyse des stations problématiques (en temps réel) :")
    print(f"  - Stations 100% VIDES : {stations_vides} / {total_stations}")
    print(f"  - Stations 100% PLEINES: {stations_pleines} / {total_stations}")

    print("------------------------------------------\n")

except Exception as e:
    print(f"ERREUR lors du calcul des statistiques : {e}")


# --- 2. PARTIE FOLIUM (Corrigée) ---

m = folium.Map(location=[48.8566, 2.3522], zoom_start=12, tiles="OpenStreetMap")

print("Récupération des stations depuis Atlas...")
for station in collection.find():
    try:
        nom = station["name"]
        capacite = station.get("capacity", "N/A")
        
        coordonnees = station["coordonnees_geo"] 
        
        latitude = coordonnees[0]
        longitude = coordonnees[1]
        
        popup_text = f"<b>{nom}</b><br>Capacité: {capacite}"
        
        folium.Marker(
            location=[latitude, longitude],
            popup=popup_text,
            icon=folium.Icon(color="green", icon="bicycle", prefix='fa')
        ).add_to(m)
        
    except Exception as e:
        print(f"Données incomplètes pour {station.get('name')}, ignorée. Erreur: {e}")


# 3. Sauvegarder la carte dans un fichier HTML
output_file_relative = "cartes_generees/carte_velib_CLOUD.html"

# Convertir le chemin relatif en chemin absolu (complet)
output_path_absolute = os.path.abspath(output_file_relative)

print(f"Sauvegarde de la carte dans : {output_path_absolute}")
m.save(output_path_absolute)

# Ouvrir le chemin absolu avec le préfixe 'file://'
webbrowser.open('file://' + output_path_absolute) 

print(f"Carte '{output_file_relative}' générée avec succès depuis le Cloud !")