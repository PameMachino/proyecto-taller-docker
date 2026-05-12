# Proyecto Taller de Desarrollo

Este repositorio contiene la configuración de **Docker Compose** para desplegar la arquitectura del sistema de optimización de rutas para ciclistas basado en rangos de seguridad.

## Servicios Incluidos
El proyecto organiza los siguientes componentes en contenedores:
* **Frontend**: Interfaz de usuario desarrollada en **Flutter**.
* **Backend NestJS**: API principal que gestiona la lógica del servidor.
* **Backend FastAPI**: Servicio especializado en cálculos de rutas utilizando el algoritmo de **Dijkstra**.
* **Base de Datos**: *PostgreSQL** con la extensión **PostGIS** para el manejo avanzado de datos geográficos y espaciales.

## Instrucciones de Despliegue
Para levantar el proyecto completo por primera vez o después de realizar cambios en el código, abra una terminal en la raíz de la carpeta y ejecute:

```bash
docker compose up --build

Si las imágenes ya fueron construidas previamente y no se han realizado cambios en la configuración, puede iniciar el sistema más rápido con::
`docker compose up`

Una vez levantado, puede acceder al frontend en:
http://localhost:3000
