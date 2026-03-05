import azure.functions as func
import json
import math
import heapq
import logging
import pandas as pd
import numpy as np
import re 
from sklearn.linear_model import LinearRegression


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


# ---------------------------------------------------------
# FUNCIÓN 1: Cálculo de Ruta Óptima (Utilizando A*)
# ---------------------------------------------------------
@app.route(route="calculate_route", methods=["POST"])
def calculate_route(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Procesando solicitud de ruta para AMR.')

    try:
        req_body = req.get_json()
        start_node = req_body.get('start_node')
        goal_node = req_body.get('goal_node')
        nodes_list = req_body.get('map_nodes', [])
        edges_list = req_body.get('map_edges', [])
        active_missions = req_body.get('active_missions', [])

        # 1. Mapa de coordenadas
        coords = {n['ID_Nodo']: (float(n['Coordenada_X']),
                                 float(n['Coordenada_Y'])) for n in nodes_list}

        # 2. Validar que los nodos inicio y fin existan en las coordenadas
        if start_node not in coords:
            return func.HttpResponse(
                f"Error: El nodo de inicio '{start_node}' no tiene coordenadas definidas.",
                status_code=400
            )
        if goal_node not in coords:
            return func.HttpResponse(
                f"Error: El nodo destino '{goal_node}' no tiene coordenadas definidas.",
                status_code=400
            )

        # 3. Construcción del Grafo con pesos dinámicos (Colisiones)
        graph = {}
        for edge in edges_list:
            u, v = edge['Origen'], edge['Destino']
            weight = float(edge['Peso_Base']) * \
                float(edge.get('Trafico_Actual', 1.0))

            # Penalización por colisión: si hay un robot en el nodo destino
            for mission in active_missions:
                if v == mission.get('Nodo_Actual'):
                    weight += 5000  # Penalización drástica

            if u not in graph:
                graph[u] = []
            graph[u].append((v, weight))

        # 4. Algoritmo A*
        def heuristic(a, b):
            if a not in coords or b not in coords:
                return 0  # O maneja el error de forma que el peso sea infinito
            (x1, y1) = coords[a]
            (x2, y2) = coords[b]
            return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

        def a_star(start, goal):
            pq = [(0 + heuristic(start, goal), start, [start], 0)]
            visited = {}

            while pq:
                (priority, current, path, current_cost) = heapq.heappop(pq)

                if current == goal:
                    return path, current_cost

                if current in visited and visited[current] <= current_cost:
                    continue

                visited[current] = current_cost

                for neighbor, weight in graph.get(current, []):
                    new_cost = current_cost + weight
                    new_priority = new_cost + heuristic(neighbor, goal)
                    heapq.heappush(pq, (new_priority, neighbor,
                                   path + [neighbor], new_cost))

            return None, float('inf')

        path, cost = a_star(start_node, goal_node)

        if path:
            return func.HttpResponse(
                json.dumps({"success": True, "path": path, "cost": cost}),
                status_code=200,
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                json.dumps(
                    {"success": False, "error": "Nodo no encontrado en el mapa"}),
                status_code=200,
                mimetype="application/json"
            )

    except Exception as e:
        return func.HttpResponse(f"Error interno: {str(e)}", status_code=500)
    
# ---------------------------------------------------------
# FUNCIÓN 2: Predicción de ETA
# ---------------------------------------------------------
@app.route(route="predict_eta", methods=["POST"])
def predict_eta(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        historial = req_body.get('historial')
        mision_actual = req_body.get('mision')
        
        # Si faltan datos, lanzamos un error para ir al bloque 'except'
        if not historial or not mision_actual:
            raise ValueError("Datos incompletos")
        
        df = pd.DataFrame(historial)
        df['Nodo_Dest_Num'] = df['Nodo_Destino'].str.extract('(\d+)').astype(int)
        X = df[['Nodo_Dest_Num', 'Robots_Activos']].values
        y = df['Duracion_Segundos'].values
        model = LinearRegression().fit(X, y)
        
        nodo_dest_num = int(re.search(r'\d+', mision_actual['Nodo_Destino']).group())
        input_data = np.array([[nodo_dest_num, mision_actual['Robots_Activos']]])
        eta = model.predict(input_data)[0]
        
        return func.HttpResponse(
            json.dumps({
                "eta_segundos": round(float(eta), 2),
                "error": False
            }),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({
                "eta_segundos": -1,
                "error": True,
                "mensaje": str(e)
            }),
            mimetype="application/json",
            status_code=200
        )
