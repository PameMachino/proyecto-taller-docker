import osmnx as ox
from sqlalchemy import create_engine
import shapely.geometry

print(" Descargando red vial")
# "bike" filtra calles con ciclovías
G = ox.graph_from_place("Concepción, Chile", network_type="bike")

# Convierte el grafo en tablas de datos de nodos y calles
nodos, calles = ox.graph_to_gdfs(G)

# Limpia datos de calles 
calles = calles.copy()
calles['geometry'] = calles['geometry'].apply(lambda x: shapely.wkt.dumps(x))
# Convierte listas a texto (a veces OSM trae nombres o tipos en listas)
for col in calles.columns:
    if calles[col].apply(lambda x: isinstance(x, list)).any():
        calles[col] = calles[col].astype(str)

# Conexión a PostGIS en Docker (Puerto 5433)
# Usa SQLAlchemy necesario para OSMnx 
engine = create_engine("postgresql://postgres:chema1998@localhost:5433/appciclista")

print(" Guardando mapa en la base de datos...")

# Las calles se guardan en la tabla 'red_vial'
calles.to_sql('red_vial', engine, if_exists='replace', index=True)

print(" Mapa guardado.")