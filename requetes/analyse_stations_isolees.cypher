// -- Étape 1 : Trouver toutes les stations...
MATCH (s:Station)

// -- Étape 2 : ...OÙ il n'existe PAS (WHERE NOT) de relation EST_PROCHE
WHERE NOT (s)-[:EST_PROCHE]-()

// -- Étape 3 : Renvoyer le nom de ces stations isolées
RETURN s.name AS station_isolee, s.stationcode