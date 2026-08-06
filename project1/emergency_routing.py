import networkx as nx

# Simplified demo road network. For a real deployment, pull actual roads
# via OSMnx (OpenStreetMap) instead of hardcoding nodes.

def build_city_graph() -> nx.Graph:
    G = nx.Graph()
    nodes = {
        "A": (28.61, 77.20), "B": (28.62, 77.21), "C": (28.63, 77.22),
        "D": (28.60, 77.23), "E": (28.615, 77.225), "F": (28.625, 77.205),
        "Hospital1": (28.605, 77.195), "Hospital2": (28.635, 77.230),
    }
    for name, (lat, lng) in nodes.items():
        G.add_node(name, lat=lat, lng=lng)

    roads = [  # (node1, node2, base_travel_time_minutes)
        ("A", "B", 4), ("B", "C", 5), ("A", "E", 3), ("E", "C", 4),
        ("A", "F", 6), ("F", "B", 3), ("D", "E", 5), ("D", "C", 6),
        ("Hospital1", "A", 2), ("Hospital2", "C", 2),
        ("Hospital1", "F", 4), ("Hospital2", "D", 3),
    ]
    for u, v, t in roads:
        G.add_edge(u, v, base_time=t, congestion_multiplier=1.0)
    return G


_graph = build_city_graph()
EMERGENCY_UNITS = {"Ambulance-1": "Hospital1", "Ambulance-2": "Hospital2"}


def update_congestion(node_a: str, node_b: str, multiplier: float):
    """Called by the traffic module to raise/lower an edge's effective travel time."""
    if _graph.has_edge(node_a, node_b):
        _graph[node_a][node_b]["congestion_multiplier"] = multiplier


def _weight(u, v, data):
    return data["base_time"] * data["congestion_multiplier"]


def route_emergency_vehicle(incident_node: str) -> dict:
    """Finds the nearest emergency unit and the fastest route, accounting for congestion."""
    best = None
    for unit_id, start_node in EMERGENCY_UNITS.items():
        try:
            path = nx.shortest_path(_graph, start_node, incident_node, weight=_weight)
            eta = nx.shortest_path_length(_graph, start_node, incident_node, weight=_weight)
        except nx.NetworkXNoPath:
            continue
        if best is None or eta < best["eta_minutes"]:
            best = {"unit_id": unit_id, "route": path, "eta_minutes": round(eta, 1)}

    if best is None:
        return {"error": "No available route found."}

    best["route_coordinates"] = [
        {"node": n, "lat": _graph.nodes[n]["lat"], "lng": _graph.nodes[n]["lng"]}
        for n in best["route"]
    ]
    best["message"] = f"{best['unit_id']} dispatched. ETA {best['eta_minutes']} min via {' → '.join(best['route'])}."
    return best
