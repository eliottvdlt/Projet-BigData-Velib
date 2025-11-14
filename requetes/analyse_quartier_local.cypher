// -- Étape 1 : Trouver la station de départ
MATCH (depart:Station {name: "Hôtel de Ville de Vincennes"})

// -- Étape 2 : Trouver un chemin (p) qui part de "depart"
// et suit des relations EST_PROCHE sur 1 ou 2 niveaux (*1..2)
MATCH p = (depart)-[:EST_PROCHE*1..2]-(voisine)

// -- Étape 3 : Renvoyer le chemin complet
RETURN p
LIMIT 100 // Limite pour éviter de surcharger l'affichage