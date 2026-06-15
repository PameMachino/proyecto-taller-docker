from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
import networkx as nx
from dotenv import load_dotenv
import os

# Variables de entorno
load_dotenv()
app = FastAPI()

DB_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}
# Guarda el grafo dirigido (respeta sentidos de las calles) de Concepción
G_CONCE = nx.DiGraph()

def cargar_grafo_desde_bd():
    # Lee las calles de PostGIS y arma la red vial en NetworkX
    global G_CONCE
    print(" Cargando red vial de Concepción desde base de datos...")

    try:
        # RealDictCursor permite leer las columnas por su nombre
        conn = psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)
        cursor = conn.cursor()

        # Origen (u), destino (v)
        cursor.execute("SELECT u, v, length, name FROM red_vial;")
        calles = cursor.fetchall()

        cursor.close()
        conn.close()

        # Limpia el grafo y usa calles reales
        G_CONCE.clear()
        for calle in calles:
            # u y v son identificadores de esquinas (nodos)
            u = int(calle['u'])
            v = int(calle['v'])
            distancia = float(calle['length'])
            nombre = calle['name'] if calle['name'] else "Calle sin nombre"

            # Añade la calle al grafo con su peso (la distancia real en metros)
            G_CONCE.add_edge(u, v, weight=distancia, nombre=nombre)

        print(f" Red vial cargada. Total de conexiones: {G_CONCE.number_of_edges()}")
        return True
    except Exception as e:
        print(f" Error al cargar el grafo: {str(e)}")
        return False

# Configuración de lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ejecución al arrancar el servidor
    cargar_grafo_desde_bd()

    yield  # Activación de la api, escuchando peticiones
app = FastAPI(lifespan=lifespan)

# RUTAS / ENDPOINTS
@app.get("/")
def inicio():
    return {
        "sistema": "API de Optimización de Rutas activa",
        "calles_en_memoria": G_CONCE.number_of_edges()
    }

@app.get("/calcular-ruta")
def calcular_ruta(origen_nodo: int, destino_nodo: int):
    # Calcula la ruta más corta en metros entre dos nodos

    # Validación de grafo vacío
    if G_CONCE.number_of_edges() == 0:
        raise HTTPException(status_code=500, detail="El mapa no está cargado en el servidor.")

    try:
        # Algoritmo Dijkstra con calles reales
        ruta_nodos = nx.dijkstra_path(G_CONCE, source=origen_nodo, target=destino_nodo, weight='weight')
        distancia_total = nx.dijkstra_path_length(G_CONCE, source=origen_nodo, target=destino_nodo, weight='weight')

        # 2. Busca nombres de calles que componen la ruta
        instrucciones_ruta = []
        for i in range(len(ruta_nodos) - 1):
            u = ruta_nodos[i]
            v = ruta_nodos[i+1]
            datos_calle = G_CONCE.get_edge_data(u, v)
            instrucciones_ruta.append(datos_calle['nombre'])

        return {
            "origen": origen_nodo,
            "destino": destino_nodo,
            "distancia_total_metros": round(distancia_total, 2),
            "secuencia_nodos": ruta_nodos,
            "calles_a_seguir": instrucciones_ruta
        }

    except nx.NetworkXNoPath:
        raise HTTPException(status_code=404, detail="No existe una ruta transitable en bicicleta entre esos dos puntos.")
    except nx.NodeNotFound as e:
        raise HTTPException(status_code=400, detail=f"ID de esquina no válido: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))