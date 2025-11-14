// -- Étape 1 : Trouver un chemin qui traverse la "frontière" d'une commune
MATCH (c1:Commune)<-[:EST_SITUÉE_DANS]-(s1:Station)
      -[r:EST_PROCHE]-
      (s2:Station)-[:EST_SITUÉE_DANS]->(c2:Commune)

// -- Étape 2 : S'assurer que ce sont bien deux communes différentes
WHERE c1 <> c2

// -- Étape 3 : Renvoyer un graphe des communes connectées
// 'DISTINCT' évite de tracer 50 lignes entre Paris et Vincennes
RETURN DISTINCT c1, c2
LIMIT 25 // Limite pour que le graphe soit lisible