import webbrowser
import pymongo
import requests  # Pour appeler l'API
import sys       # Pour quitter en cas d'erreur

# --- 0. IMPORTATION DES SECRETS ---
# On remonte d'un dossier (de 'scripts' à la racine) pour trouver config.py
try:
    sys.path.append('..') 
    import config
except ImportError:
    print("ERREUR : Le fichier 'config.py' est introuvable à la racine du projet.")
    print("Veuillez le créer avant de lancer ce script.")
    sys.exit()


# --- 1. APPEL À L'API VÉLIB' (Internet) ---

# URL de l'API Open Data de Paris pour les données Vélib'
api_url = "https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&rows=2000"

print("Appel à l'API Vélib' en cours...")
try:
    response = requests.get(api_url)
    response.raise_for_status()  # Vérifie les erreurs (ex: 404, 500)
    data = response.json()
    stations_api = data['records']
    print(f"Succès : {len(stations_api)} stations récupérées depuis l'API.")

except Exception as e:
    print(f"ERREUR : Impossible de contacter l'API Vélib'. {e}")
    sys.exit()  # Arrête le script si l'API ne répond pas


# --- 2. CONNEXION À MONGODB ATLAS (Cloud) ---

# On n'écrit PLUS le mot de passe ici.
# On va le chercher dans le fichier 'config.py' (qui est ignoré par Git)

print("Connexion à MongoDB Atlas en cours...")
try:
    # On utilise la variable importée depuis le fichier config
    client = pymongo.MongoClient(config.ATLAS_CONNECTION_STRING) 
    
    # Donnez des noms à votre BDD et collection dans le cloud
    db = client["velib_cloud_db"]
    collection = db["stations"]
    
    # Teste la connexion
    client.admin.command('ping') 
    print("Succès : Connecté à MongoDB Atlas.")

except Exception as e:
    print(f"ERREUR : Impossible de se connecter à Atlas. Vérifiez votre chaîne de connexion ou votre IP. {e}")
    sys.exit()


# --- 3. INSÉRER LES DONNÉES DANS ATLAS ---

try:
    # On vide la collection avant de la remplir (pour rafraîchir les données)
    collection.delete_many({})
    print("Anciennes données purgées de la collection 'stations'.")

    # L'API opendata met les données dans un champ 'fields'
    donnees_a_inserer = []
    for record in stations_api:
        station_data = record['fields']
        # On utilise 'recordid' comme _id unique
        station_data['_id'] = record['recordid'] 
        donnees_a_inserer.append(station_data)

    # Insérer toutes les stations d'un coup
    if donnees_a_inserer:
        collection.insert_many(donnees_a_inserer)
        print(f"Succès : {len(donnees_a_inserer)} nouvelles stations insérées dans Atlas.")
    else:
        print("Aucune station trouvée dans l'API.")

except Exception as e:
    print(f"ERREUR : Échec de l'insertion des données. {e}")

finally:
    client.close()
    print("Connexion à Atlas fermée.")