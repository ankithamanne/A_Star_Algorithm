from flask import Flask, render_template, request, redirect
import math
import heapq
from math import radians, sin, cos, sqrt, atan2

app = Flask(__name__)

# Campus location coordinates
locations = {
    "CSE Block": {"lat": 17.521600231862433, "lng": 78.36738726579225},
    "Mechanical/Civil/EEE Block": {"lat": 17.52123065303647, "lng": 78.36724560420778},
    "ECE Block": {"lat": 17.521101781355313, "lng": 78.36648995263315},
    "IIT Block": {"lat": 17.520951236273163, "lng": 78.36742153903911},
    "Canteen": {"lat": 17.52042355238384, "lng": 78.36655837309104},
    "Gokaraju Lailavathi Block": {"lat": 17.520899755428277, "lng": 78.3655906418605},
    "Bank": {"lat": 17.518968155008043, "lng": 78.36824539149862},
    "Pharmacy": {"lat": 17.52064588787157, "lng": 78.36884130980921},
    "Library": {"lat": 17.52052129795962, "lng": 78.3674706613302},
    "Hall 1&2": {"lat": 17.519167663376184, "lng": 78.36788463439972},
    "Volleyball Court": {"lat": 17.519404480238533, "lng": 78.367858664968},
    "Cricket Ground": {"lat": 17.51901452905933, "lng": 78.36632218639454},
    "Open Air Stadium": {"lat": 17.520656113410645, "lng": 78.3666894976822}
}

# Edges for pathfinding
edges = {
    "CSE Block": ["Mechanical/Civil/EEE Block", "Library"],
    "Mechanical/Civil/EEE Block": ["CSE Block", "IIT Block"],
    "ECE Block": ["IIT Block", "Canteen"],
    "IIT Block": ["Mechanical/Civil/EEE Block", "ECE Block", "Library"],
    "Canteen": ["ECE Block", "Gokaraju Lailavathi Block"],
    "Gokaraju Lailavathi Block": ["Canteen", "Cricket Ground"],
    "Bank": ["Pharmacy", "Hall 1&2"],
    "Pharmacy": ["Bank", "Library"],
    "Library": ["CSE Block", "IIT Block", "Pharmacy", "Open Air Stadium"],
    "Hall 1&2": ["Bank", "Volleyball Court"],
    "Volleyball Court": ["Hall 1&2", "Cricket Ground"],
    "Cricket Ground": ["Volleyball Court", "Gokaraju Lailavathi Block"],
    "Open Air Stadium": ["Library"]
}

# Haversine distance
def haversine(a, b):
    R = 6371  # km
    lat1, lon1 = radians(a["lat"]), radians(a["lng"])
    lat2, lon2 = radians(b["lat"]), radians(b["lng"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    x = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(x), sqrt(1 - x))

# A* algorithm
def a_star(start, end):
    open_set = [(0, start)]
    came_from = {}
    g_score = {loc: float('inf') for loc in locations}
    f_score = {loc: float('inf') for loc in locations}
    g_score[start] = 0
    f_score[start] = haversine(locations[start], locations[end])
    visited = set()

    while open_set:
        _, current = heapq.heappop(open_set)
        if current in visited:
            continue
        visited.add(current)
        if current == end:
            path = []
            while current in came_from:
                path.insert(0, current)
                current = came_from[current]
            path.insert(0, start)
            return path
        for neighbor in edges.get(current, []):
            tentative_g = g_score[current] + haversine(locations[current], locations[neighbor])
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + haversine(locations[neighbor], locations[end])
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_location = request.form['startLocation']
        destination = request.form['destination']

        if start_location == destination:
            return render_template('index.html', locations=locations, error="Start and destination cannot be the same.")

        path = a_star(start_location, destination)
        if not path:
            return render_template('index.html', locations=locations, error="No path found between selected locations.")

        # Google Maps Directions API URL
        waypoints = "|".join(f"{locations[loc]['lat']},{locations[loc]['lng']}" for loc in path[1:-1])
        map_url = f"https://www.google.com/maps/dir/?api=1&origin={locations[start_location]['lat']},{locations[start_location]['lng']}&destination={locations[destination]['lat']},{locations[destination]['lng']}&waypoints={waypoints}"
        return redirect(map_url)

    return render_template('index.html', locations=locations)

if __name__ == '__main__':
    app.run(debug=True)
