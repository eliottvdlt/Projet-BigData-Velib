import requests
import sys
from neo4j import GraphDatabase  # La nouvelle bibliothèque

# --- 0. IMPORTATION DES SECRETS ---
# On remonte d'un dossier (de 'scripts' à la racine) pour trouver config.py
try:
    sys.path.append('..') 
    import config
except ImportError:
    print("ERREUR : Le fichier 'config.py' est introuvable à la racine du projet.")
    print("Veuillez le créer avant de lancer ce script.")
    sys.exit()

# --- 1. APPEL À L'API VÉLIB' (Identique à avant) ---
api_url = "https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&rows=2000"
print("Appel à l'API Vélib' en cours...")
try:
    response = requests.get(api_url)
    response.raise_for_status()
    data = response.json()
    stations_api = data['records']
    print(f"Succès : {len(stations_api)} stations récupérées depuis l'API.")
except Exception as e:
    print(f"ERREUR API : {e}")
    sys.exit()

# --- 2. FONCTION D'IMPORTATION DANS NEO4J ---
def importer_donnees_dans_neo4j(driver, stations):
    with driver.session() as session:
        
        # Étape 2a : Nettoyer la base de données
        print("Nettoyage de la base Neo4j...")
        session.run("MATCH (n) DETACH DELETE n")
        
        # Étape 2b : Créer les nœuds et les relations
        print("Importation des stations dans Neo4j...")
        
        query = """
        UNWIND $rows AS row
        WITH row.fields AS station
        
        MERGE (s:Station {stationcode: station.stationcode})
        ON CREATE SET
            s.name = station.name,
            s.capacity = station.capacity,
            s.lat = station.coordonnees_geo[0],
            s.lon = station.coordonnees_geo[1]
            
        MERGE (c:Commune {name: station.nom_arrondissement_communes})
        
        MERGE (s)-[:EST_SITUÉE_DANS]->(c)
        """
        
        session.run(query, rows=stations)
        print("Importation Neo4j terminée avec succès !")

# --- 3. EXÉCUTION DU SCRIPT ---
try:
    # Connexion à Neo4j en utilisant les variables de config.py
    driver = GraphDatabase.driver(
        config.NEO4J_URI, 
        auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
    )
    
    # Lancement de l'importation
    importer_donnees_dans_neo4j(driver, stations_api)
    
except Exception as e:
    print(f"ERREUR NEO4J : {e}")
    print("Vérifiez que Neo4j Desktop est démarré et que le mot de passe est correct.")
finally:
    if 'driver' in locals():
        driver.close()
        print("Connexion Neo4j fermée.")