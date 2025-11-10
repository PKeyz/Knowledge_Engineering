// Neo4j Import Script for Energy Grid Dataset
// Run this in Neo4j Browser after generating CSVs

// ============================================
// STEP 1: Create Constraints and Indexes
// ============================================

CREATE CONSTRAINT substation_id IF NOT EXISTS FOR (s:Substation) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT transformer_id IF NOT EXISTS FOR (t:Transformer) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT line_id IF NOT EXISTS FOR (l:Line) REQUIRE l.id IS UNIQUE;
CREATE CONSTRAINT measurement_id IF NOT EXISTS FOR (m:Measurement) REQUIRE m.id IS UNIQUE;

CREATE INDEX substation_voltage IF NOT EXISTS FOR (s:Substation) ON (s.voltage_level);
CREATE INDEX transformer_voltage IF NOT EXISTS FOR (t:Transformer) ON (t.primary_voltage);
CREATE INDEX line_voltage IF NOT EXISTS FOR (l:Line) ON (l.voltage);

// ============================================
// STEP 2: Import Substations
// ============================================

LOAD CSV WITH HEADERS FROM 'file:///substations.csv' AS row
CREATE (s:Substation {
    id: row.id,
    name: row.name,
    type: row.type,
    voltage_level: row.voltage_level,
    installed: date(row.installed),
    capacity_mva: toInteger(row.capacity_mva),
    status: row.status
});

// ============================================
// STEP 3: Import Transformers
// ============================================

LOAD CSV WITH HEADERS FROM 'file:///transformers.csv' AS row
CREATE (t:Transformer {
    id: row.id,
    name: row.name,
    type: row.type,
    primary_voltage: row.primary_voltage,
    secondary_voltage: row.secondary_voltage,
    rating_mva: toInteger(row.rating_mva),
    installed: date(row.installed),
    efficiency: toFloat(row.efficiency),
    status: row.status
});

// ============================================
// STEP 4: Connect Transformers to Substations
// ============================================

LOAD CSV WITH HEADERS FROM 'file:///transformers.csv' AS row
MATCH (t:Transformer {id: row.id})
MATCH (s:Substation {id: row.substation_id})
CREATE (t)-[:LOCATED_IN]->(s);

// ============================================
// STEP 5: Import Lines
// ============================================

LOAD CSV WITH HEADERS FROM 'file:///lines.csv' AS row
CREATE (l:Line {
    id: row.id,
    name: row.name,
    type: row.type,
    length_km: toFloat(row.length_km),
    voltage: row.voltage,
    installed: date(row.installed),
    capacity_mw: toInteger(row.capacity_mw),
    status: row.status
});

// ============================================
// STEP 6: Connect Lines (from -> to)
// ============================================

LOAD CSV WITH HEADERS FROM 'file:///lines.csv' AS row
MATCH (l:Line {id: row.id})
MATCH (from) WHERE from.id = row.from_id
MATCH (to) WHERE to.id = row.to_id
CREATE (from)-[:CONNECTED_BY {line_id: l.id}]->(to)
CREATE (l)-[:CONNECTS_FROM]->(from)
CREATE (l)-[:CONNECTS_TO]->(to);

// ============================================
// STEP 7: Import Measurements
// ============================================

LOAD CSV WITH HEADERS FROM 'file:///measurements.csv' AS row
CREATE (m:Measurement {
    id: row.id,
    name: row.name,
    type: row.type,
    installed: date(row.installed),
    sampling_rate_hz: toInteger(row.sampling_rate_hz),
    accuracy_percent: toFloat(row.accuracy_percent),
    status: row.status
});

// ============================================
// STEP 8: Connect Measurements to Transformers
// ============================================

LOAD CSV WITH HEADERS FROM 'file:///measurements.csv' AS row
MATCH (m:Measurement {id: row.id})
MATCH (t:Transformer {id: row.transformer_id})
CREATE (m)-[:MONITORS]->(t);

// ============================================
// STEP 9: Verify Import
// ============================================

// Count nodes
MATCH (s:Substation) RETURN 'Substations' AS type, count(s) AS count
UNION
MATCH (t:Transformer) RETURN 'Transformers' AS type, count(t) AS count
UNION
MATCH (l:Line) RETURN 'Lines' AS type, count(l) AS count
UNION
MATCH (m:Measurement) RETURN 'Measurements' AS type, count(m) AS count;

// Count relationships
MATCH ()-[r]->() RETURN type(r) AS relationship_type, count(r) AS count;

// ============================================
// BONUS: Create Sample Queries
// ============================================

// 1. Find all transformers in a specific substation
MATCH (t:Transformer)-[:LOCATED_IN]->(s:Substation {name: 'Substation_1'})
RETURN t.name, t.type, t.rating_mva;

// 2. Find shortest path between two substations
MATCH path = shortestPath(
  (s1:Substation {name: 'Substation_1'})-[*]-(s2:Substation {name: 'Substation_10'})
)
RETURN path;

// 3. Find all transformers with measurements
MATCH (m:Measurement)-[:MONITORS]->(t:Transformer)
RETURN t.name, collect(m.type) AS measurement_types;

// 4. Find overloaded lines (>80% capacity)
MATCH (l:Line)
WHERE l.capacity_mw > 0
RETURN l.name, l.capacity_mw, l.status
ORDER BY l.capacity_mw DESC
LIMIT 10;
