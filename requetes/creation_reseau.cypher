// -- Étape 1 : Trouver toutes les paires de stations
MATCH (s1:Station), (s2:Station)

// -- Étape 2 : Éviter les doublons et les boucles (utilise elementId)
WHERE elementId(s1) < elementId(s2)

// -- Étape 3 : Calculer la distance
WITH s1, s2,
     point.distance(
       point({latitude: s1.lat, longitude: s1.lon}), 
       point({latitude: s2.lat, longitude: s2.lon})
     ) AS distance

// -- Étape 4 : Filtrer pour garder les stations "marchables" (< 500m)
WHERE distance < 500

// -- Étape 5 : Créer la nouvelle relation
MERGE (s1)-[r:EST_PROCHE {distance_metres: round(distance)}]->(s2)

// -- Étape 6 : Compter le nombre de relations créées
RETURN count(r) AS nouvelles_relations_creees