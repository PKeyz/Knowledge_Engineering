"""
Synthetic Energy Grid Dataset Generator
Generates realistic power grid data similar to municipal infrastructure
~5000 assets: Substations, Transformers, Lines, Measurement Points
"""

import csv
import random
import uuid
from datetime import datetime, timedelta

# Configuration
NUM_SUBSTATIONS = 50
NUM_TRANSFORMERS = 800
NUM_LINES = 2500
NUM_MEASUREMENTS = 1650  # Total: 5000 assets

VOLTAGE_LEVELS = ['400kV', '110kV', '20kV', '10kV', '0.4kV']
TRANSFORMER_TYPES = ['Distribution', 'Power', 'Step-Down', 'Step-Up']
LINE_TYPES = ['Overhead', 'Underground', 'Cable']
SUBSTATION_TYPES = ['Primary', 'Secondary', 'Distribution']

def generate_id(prefix):
    """Generate realistic asset ID"""
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

def random_date(start_year=2000, end_year=2024):
    """Generate random installation date"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')

def generate_substations():
    """Generate substation nodes"""
    substations = []
    for i in range(NUM_SUBSTATIONS):
        substation = {
            'id': generate_id('SUB'),
            'name': f'Substation_{i+1}',
            'type': random.choice(SUBSTATION_TYPES),
            'voltage_level': random.choice(VOLTAGE_LEVELS[:3]),  # Higher voltages
            'installed': random_date(),
            'capacity_mva': random.randint(50, 500),
            'status': random.choice(['Active', 'Active', 'Active', 'Maintenance'])
        }
        substations.append(substation)
    return substations

def generate_transformers(substations):
    """Generate transformer nodes connected to substations"""
    transformers = []
    for i in range(NUM_TRANSFORMERS):
        parent_sub = random.choice(substations)
        # Voltage step-down logic
        parent_voltage = parent_sub['voltage_level']
        parent_idx = VOLTAGE_LEVELS.index(parent_voltage)
        if parent_idx < len(VOLTAGE_LEVELS) - 1:
            primary_voltage = parent_voltage
            secondary_voltage = VOLTAGE_LEVELS[parent_idx + 1]
        else:
            primary_voltage = parent_voltage
            secondary_voltage = parent_voltage
        
        transformer = {
            'id': generate_id('TRF'),
            'name': f'Transformer_{i+1}',
            'type': random.choice(TRANSFORMER_TYPES),
            'primary_voltage': primary_voltage,
            'secondary_voltage': secondary_voltage,
            'rating_mva': random.randint(1, 100),
            'installed': random_date(),
            'substation_id': parent_sub['id'],
            'efficiency': round(random.uniform(0.95, 0.99), 3),
            'status': random.choice(['Active', 'Active', 'Active', 'Standby'])
        }
        transformers.append(transformer)
    return transformers

def generate_lines(substations, transformers):
    """Generate power line connections"""
    lines = []
    all_nodes = substations + transformers
    
    for i in range(NUM_LINES):
        # Create realistic connections
        from_node = random.choice(all_nodes)
        to_node = random.choice(all_nodes)
        
        # Avoid self-loops
        while to_node['id'] == from_node['id']:
            to_node = random.choice(all_nodes)
        
        line = {
            'id': generate_id('LINE'),
            'name': f'Line_{i+1}',
            'type': random.choice(LINE_TYPES),
            'from_id': from_node['id'],
            'to_id': to_node['id'],
            'length_km': round(random.uniform(0.1, 50.0), 2),
            'voltage': from_node.get('voltage_level', from_node.get('secondary_voltage', '20kV')),
            'installed': random_date(),
            'capacity_mw': random.randint(1, 200),
            'status': random.choice(['Active', 'Active', 'Active', 'Under_Repair'])
        }
        lines.append(line)
    return lines

def generate_measurements(transformers):
    """Generate measurement points for monitoring"""
    measurements = []
    monitored_transformers = random.sample(transformers, min(NUM_MEASUREMENTS, len(transformers)))
    
    for i, transformer in enumerate(monitored_transformers):
        measurement = {
            'id': generate_id('MEAS'),
            'name': f'Measurement_{i+1}',
            'transformer_id': transformer['id'],
            'type': random.choice(['Current', 'Voltage', 'Power', 'Temperature']),
            'installed': random_date(2015, 2024),  # More recent
            'sampling_rate_hz': random.choice([1, 10, 50, 100]),
            'accuracy_percent': round(random.uniform(0.1, 2.0), 2),
            'status': 'Active'
        }
        measurements.append(measurement)
    return measurements

def write_csv(filename, data, fieldnames):
    """Write data to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"✓ Created {filename} ({len(data)} records)")

def main():
    print("Generating Energy Grid Dataset...")
    print(f"Target: ~{NUM_SUBSTATIONS + NUM_TRANSFORMERS + NUM_LINES + NUM_MEASUREMENTS} assets\n")
    
    # Generate data
    substations = generate_substations()
    transformers = generate_transformers(substations)
    lines = generate_lines(substations, transformers)
    measurements = generate_measurements(transformers)
    
    # Write CSVs
    write_csv('substations.csv', substations, 
              ['id', 'name', 'type', 'voltage_level', 'installed', 'capacity_mva', 'status'])
    
    write_csv('transformers.csv', transformers,
              ['id', 'name', 'type', 'primary_voltage', 'secondary_voltage', 
               'rating_mva', 'installed', 'substation_id', 'efficiency', 'status'])
    
    write_csv('lines.csv', lines,
              ['id', 'name', 'type', 'from_id', 'to_id', 'length_km', 
               'voltage', 'installed', 'capacity_mw', 'status'])
    
    write_csv('measurements.csv', measurements,
              ['id', 'name', 'transformer_id', 'type', 'installed', 
               'sampling_rate_hz', 'accuracy_percent', 'status'])
    
    print(f"\n✓ Total assets generated: {len(substations) + len(transformers) + len(lines) + len(measurements)}")
    print("\nNext steps:")
    print("1. Install Neo4j Desktop: https://neo4j.com/download/")
    print("2. Create new database")
    print("3. Run: python generate_energy_grid.py")
    print("4. Run: import_to_neo4j.cypher")

if __name__ == '__main__':
    main()
