// -- Étape 1 : Trouver la station de départ et d'arrivée
MATCH (depart:Station {stationcode: "4016"}),  // Station "Lobau - Hôtel de Ville"
      (arrivee:Station {stationcode: "15203"}) // Station "Porte de Versailles"

// -- Étape 2 : Trouver le chemin le plus court en utilisant nos relations
// 'EST_PROCHE*' signifie "0 ou plusieurs sauts de type EST_PROCHE"
MATCH p = shortestPath( (depart)-[:EST_PROCHE*]-(arrivee) )

// -- Étape 3 : Renvoyer le chemin complet (nœuds ET relations)
RETURN p