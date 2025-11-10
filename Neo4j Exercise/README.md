# Energy Grid Dataset for Neo4j Practice

Synthetisches Stromnetz-Dataset mit ~5000 Assets für Cypher-Übungen.
Ähnliche Struktur wie reale kommunale Stromnetze (z.B. SWM).

## 📊 Datenstruktur

### Nodes (4 Typen)
- **Substation** (50): Umspannwerke (Primary, Secondary, Distribution)
- **Transformer** (800): Transformatoren (verschiedene Typen, Spannungsebenen)
- **Line** (2500): Stromleitungen (Overhead, Underground, Cable)
- **Measurement** (1650): Messpunkte (Current, Voltage, Power, Temperature)

### Relationships
- `(Transformer)-[:LOCATED_IN]->(Substation)` - Transformator in Umspannwerk
- `(Node)-[:CONNECTED_BY]->(Node)` - Elektrische Verbindung
- `(Line)-[:CONNECTS_FROM]->(Node)` - Leitung von Knoten
- `(Line)-[:CONNECTS_TO]->(Node)` - Leitung zu Knoten
- `(Measurement)-[:MONITORS]->(Transformer)` - Messpunkt überwacht Transformator

## 🚀 Setup (15 Minuten)

### 1. CSVs generieren
```bash
python generate_energy_grid.py
```

Erstellt:
- `substations.csv`
- `transformers.csv`
- `lines.csv`
- `measurements.csv`

### 2. Neo4j installieren
- Download: https://neo4j.com/download/
- Neo4j Desktop installieren
- Neue Datenbank erstellen
- Datenbank starten

### 3. CSVs kopieren
CSVs in Neo4j Import-Verzeichnis kopieren:

**Neo4j Desktop:**
1. Datenbank öffnen → "..." → "Open folder" → "Import"
2. Alle CSV-Dateien hinein kopieren

**Alternative (manuell):**
```
Windows: C:\Users\<Username>\.Neo4jDesktop\relate-data\dbmss\<dbms-id>\import\
Mac: ~/Library/Application Support/Neo4j Desktop/Application/relate-data/dbmss/<dbms-id>/import/
Linux: ~/.config/Neo4j Desktop/Application/relate-data/dbmss/<dbms-id>/import/
```

### 4. Import in Neo4j
Neo4j Browser öffnen → `import_to_neo4j.cypher` Schritt für Schritt ausführen

**Oder alles auf einmal:**
```cypher
// In Neo4j Browser die komplette import_to_neo4j.cypher Datei öffnen und ausführen
```

### 5. Verify
```cypher
MATCH (n) RETURN count(n);  // Sollte ~5000 sein
MATCH ()-[r]->() RETURN count(r);  // Relationships
```

## 🎯 Übungs-Queries (Interview-Prep)

### Basic Queries
```cypher
// 1. Alle Substations mit hoher Kapazität
MATCH (s:Substation)
WHERE s.capacity_mva > 200
RETURN s.name, s.voltage_level, s.capacity_mva
ORDER BY s.capacity_mva DESC;

// 2. Transformers nach Spannungsebene gruppieren
MATCH (t:Transformer)
RETURN t.primary_voltage AS voltage, count(t) AS count
ORDER BY count DESC;

// 3. Leitungen nach Typ und Status
MATCH (l:Line)
RETURN l.type, l.status, count(*) AS count;
```

### Multi-Hop Queries (wichtig für Interview!)
```cypher
// 4. Alle Transformers 2 Hops von Substation_1
MATCH (s:Substation {name: 'Substation_1'})<-[:LOCATED_IN]-(t1:Transformer)
MATCH (t1)-[:CONNECTED_BY*1..2]-(t2:Transformer)
RETURN DISTINCT t2.name, t2.type;

// 5. Kürzester Pfad zwischen zwei Substations
MATCH (s1:Substation {name: 'Substation_1'}),
      (s2:Substation {name: 'Substation_10'})
MATCH path = shortestPath((s1)-[*]-(s2))
RETURN path, length(path) AS hops;

// 6. Alle Leitungen länger als 20km mit ihren Verbindungen
MATCH (from)-[:CONNECTED_BY]->(to)
MATCH (l:Line)-[:CONNECTS_FROM]->(from)
MATCH (l)-[:CONNECTS_TO]->(to)
WHERE l.length_km > 20
RETURN from.name, to.name, l.length_km, l.type;
```

### Aggregation & Analytics
```cypher
// 7. Durchschnittliche Transformer-Effizienz pro Substation
MATCH (t:Transformer)-[:LOCATED_IN]->(s:Substation)
RETURN s.name, 
       count(t) AS transformer_count,
       round(avg(t.efficiency), 3) AS avg_efficiency
ORDER BY transformer_count DESC
LIMIT 10;

// 8. Meistgemessene Transformers
MATCH (m:Measurement)-[:MONITORS]->(t:Transformer)
RETURN t.name, 
       count(m) AS measurement_count,
       collect(m.type) AS measurement_types
ORDER BY measurement_count DESC
LIMIT 10;

// 9. Netzwerk-Statistik: Grad-Verteilung
MATCH (n)
RETURN labels(n)[0] AS node_type,
       count(n) AS node_count,
       round(avg(size((n)-[]-()))) AS avg_degree;
```

### Performance-Optimierung (Interview-relevant!)
```cypher
// 10. PROFILE für Query-Analyse
PROFILE
MATCH (t:Transformer)-[:LOCATED_IN]->(s:Substation)
WHERE s.voltage_level = '110kV'
RETURN t.name, s.name;

// 11. Index-Test: Mit vs. Ohne Index
// Erst Index löschen, Query ausführen, dann Index erstellen, nochmal
DROP INDEX transformer_voltage IF EXISTS;
MATCH (t:Transformer) WHERE t.primary_voltage = '110kV' RETURN count(t);
CREATE INDEX transformer_voltage FOR (t:Transformer) ON (t.primary_voltage);
MATCH (t:Transformer) WHERE t.primary_voltage = '110kV' RETURN count(t);
```

### Graph-Algorithmen (Bonus)
```cypher
// 12. PageRank für wichtigste Nodes
CALL gds.pageRank.stream('myGraph')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).name AS name, score
ORDER BY score DESC LIMIT 10;

// 13. Community Detection
CALL gds.louvain.stream('myGraph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name AS name, communityId
LIMIT 20;
```

## 💡 Interview-Tipps

### Typische Fragen:
1. **"Wie würdest du diesen Query optimieren?"**
   → PROFILE/EXPLAIN verwenden, Indexes prüfen, Query-Struktur verbessern

2. **"Wann Graph vs. Relational?"**
   → Graph bei vielen Beziehungen, variable Tiefe, Pattern-Matching

3. **"Performance-Problem bei großen Graphen?"**
   → Indexes, Query-Limits, Property-Filter früh anwenden, PROFILE nutzen

### Deine SWM-Stories:
- "Bei SWM hatten wir 50k Assets - ähnliche Struktur wie hier"
- "Performance-Optimierung durch gezielte Indexes auf Spannungsebenen"
- "Multi-Hop-Queries für Netzanalyse (z.B. welche Assets betroffen bei Ausfall)"

## 📁 Dateien

- `generate_energy_grid.py` - Generiert CSV-Daten
- `import_to_neo4j.cypher` - Neo4j Import-Script
- `substations.csv` - Umspannwerke
- `transformers.csv` - Transformatoren
- `lines.csv` - Stromleitungen
- `measurements.csv` - Messpunkte

## 🔍 Nächste Schritte

1. ✅ Daten generieren & importieren
2. ✅ Basic Queries durchgehen
3. ✅ Multi-Hop-Queries üben (wichtig!)
4. ✅ Performance-Analyse mit PROFILE
5. ✅ 3-5 SWM-Stories mit konkreten Query-Beispielen vorbereiten

Viel Erfolg beim Interview! 🚀
