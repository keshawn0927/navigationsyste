import os
import heapq
import webbrowser
from collections import defaultdict
from tkinter import Tk, Label, Button, messagebox, simpledialog

import folium
import googlemaps
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GOOGLE_MAPS_API_KEY")

if not api_key:
    messagebox.showerror("API Key Error", "Google Maps API key not found. Check your .env file.")
    exit()

gmaps = googlemaps.Client(key=api_key)

pickup_location = ""
delivery_destination = ""
client_name = ""
driver_name = ""


def company_info():
    messagebox.showinfo(
        "Company Info",
        "Company Name: FastRoute Delivery\n\n"
        "Mission: Help delivery drivers find efficient routes.\n\n"
        "Founded: 2026\n\n"
        "Team Members: Keshawn Ross"
    )


def set_pickup_location():
    global pickup_location

    value = simpledialog.askstring("Pickup Location", "Enter pickup location:")

    if value:
        pickup_location = value.strip()
        pickup_label.config(text="Pickup: " + pickup_location)


def set_delivery_destination():
    global delivery_destination

    value = simpledialog.askstring("Delivery Destination", "Enter delivery destination:")

    if value:
        delivery_destination = value.strip()
        destination_label.config(text="Destination: " + delivery_destination)


def set_client_name():
    global client_name

    value = simpledialog.askstring("Client Name", "Enter client name:")

    if value:
        client_name = value.strip()
        client_label.config(text="Client Name: " + client_name)


def set_driver_name():
    global driver_name

    value = simpledialog.askstring("Driver Name", "Enter delivery driver name:")

    if value:
        driver_name = value.strip()
        driver_label.config(text="Driver Name: " + driver_name)


def fetch_directions(pickup, destination):
    try:
        directions = gmaps.directions(pickup, destination, mode="driving")

        if not directions:
            messagebox.showerror("Route Error", "No route found. Check the addresses.")
            return None

        return directions

    except Exception as error:
        messagebox.showerror("Google Maps Error", str(error))
        return None


def parse_route(directions):
    leg = directions[0]["legs"][0]
    steps = leg["steps"]

    route_steps = []

    for step in steps:
        start = (
            step["start_location"]["lat"],
            step["start_location"]["lng"]
        )

        end = (
            step["end_location"]["lat"],
            step["end_location"]["lng"]
        )

        distance = step["distance"]["value"]

        route_steps.append((start, end, distance))

    total_distance = leg["distance"]["text"]
    total_time = leg["duration"]["text"]

    return route_steps, total_distance, total_time


def build_graph(route_steps):
    graph = defaultdict(list)

    for start, end, distance in route_steps:
        graph[start].append((end, distance))
        graph[end].append((start, distance))

    return graph


def dijkstra(graph, start, end):
    distances = {node: float("inf") for node in graph}
    previous = {}

    distances[start] = 0
    queue = [(0, start)]

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_node == end:
            break

        for neighbor, weight in graph[current_node]:
            new_distance = current_distance + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_node
                heapq.heappush(queue, (new_distance, neighbor))

    path = []
    current = end

    while current in previous:
        path.append(current)
        current = previous[current]

    path.append(start)
    path.reverse()

    return path, distances[end]


def visualize_path(path, pickup, destination):
    route_map = folium.Map(location=path[0], zoom_start=13)

    folium.Marker(path[0], popup="Pickup: " + pickup).add_to(route_map)
    folium.Marker(path[-1], popup="Destination: " + destination).add_to(route_map)
    folium.PolyLine(path, weight=5).add_to(route_map)

    route_map.save("route_map.html")
    webbrowser.open("file://" + os.path.abspath("route_map.html"))


def calculate_route():
    if pickup_location == "":
        messagebox.showerror("Error", "Enter pickup location.")
        return

    if delivery_destination == "":
        messagebox.showerror("Error", "Enter delivery destination.")
        return

    if client_name == "":
        messagebox.showerror("Error", "Enter client name.")
        return

    if driver_name == "":
        messagebox.showerror("Error", "Enter driver name.")
        return

    directions = fetch_directions(pickup_location, delivery_destination)

    if directions is None:
        return

    route_steps, total_distance, total_time = parse_route(directions)

    graph = build_graph(route_steps)

    start = route_steps[0][0]
    end = route_steps[-1][1]

    shortest_path, dijkstra_distance = dijkstra(graph, start, end)

    result_text = (
        "Delivery Record\n\n"
        f"Client Name: {client_name}\n"
        f"Driver Name: {driver_name}\n"
        f"Pickup Location: {pickup_location}\n"
        f"Delivery Destination: {delivery_destination}\n"
        f"Total Distance: {total_distance}\n"
        f"Estimated Time: {total_time}\n"
        f"Dijkstra Distance: {dijkstra_distance} meters\n\n"
        "The map has been opened in your browser."
    )

    messagebox.showinfo("Route Summary", result_text)

    visualize_path(shortest_path, pickup_location, delivery_destination)


root = Tk()
root.title("FastRoute Delivery Navigation System")
root.geometry("700x700")
root.configure(bg="white")


Label(
    root,
    text="FastRoute Delivery Navigation System",
    font=("Arial", 18, "bold"),
    bg="white",
    fg="darkblue"
).pack(pady=15)


Label(
    root,
    text="Use the buttons below to enter delivery information.",
    font=("Arial", 12),
    bg="white",
    fg="black"
).pack(pady=10)


Button(
    root,
    text="Enter Pickup Location",
    width=30,
    height=2,
    command=set_pickup_location,
    bg="lightyellow",
    fg="black",
    font=("Arial", 12, "bold")
).pack(pady=5)

pickup_label = Label(
    root,
    text="Pickup: Not Entered",
    bg="white",
    fg="black",
    font=("Arial", 11)
)
pickup_label.pack(pady=3)


Button(
    root,
    text="Enter Delivery Destination",
    width=30,
    height=2,
    command=set_delivery_destination,
    bg="lightyellow",
    fg="black",
    font=("Arial", 12, "bold")
).pack(pady=5)

destination_label = Label(
    root,
    text="Destination: Not Entered",
    bg="white",
    fg="black",
    font=("Arial", 11)
)
destination_label.pack(pady=3)


Button(
    root,
    text="Enter Client Name",
    width=30,
    height=2,
    command=set_client_name,
    bg="lightyellow",
    fg="black",
    font=("Arial", 12, "bold")
).pack(pady=5)

client_label = Label(
    root,
    text="Client Name: Not Entered",
    bg="white",
    fg="black",
    font=("Arial", 11)
)
client_label.pack(pady=3)


Button(
    root,
    text="Enter Driver Name",
    width=30,
    height=2,
    command=set_driver_name,
    bg="lightyellow",
    fg="black",
    font=("Arial", 12, "bold")
).pack(pady=5)

driver_label = Label(
    root,
    text="Driver Name: Not Entered",
    bg="white",
    fg="black",
    font=("Arial", 11)
)
driver_label.pack(pady=3)


Button(
    root,
    text="Calculate Route",
    width=30,
    height=2,
    command=calculate_route,
    bg="lightgreen",
    fg="darkgreen",
    font=("Arial", 12, "bold")
).pack(pady=15)


Button(
    root,
    text="Company Info",
    width=30,
    height=2,
    command=company_info,
    bg="lightblue",
    fg="darkblue",
    font=("Arial", 12, "bold")
).pack(pady=5)


Button(
    root,
    text="Exit",
    width=30,
    height=2,
    command=root.destroy,
    bg="lightcoral",
    fg="darkred",
    font=("Arial", 12, "bold")
).pack(pady=5)


root.mainloop()