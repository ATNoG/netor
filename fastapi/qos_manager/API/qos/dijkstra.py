import heapq
def dijkstra(graph, src, dest):
    distances = {node: float('inf') for node in graph}  # Initialize distances to infinity
    distances[src] = 0  # Distance from source to itself is 0
    queue = [(0, src)]  # Priority queue to track nodes to visit
    previous_nodes = {}  # Keep track of previous nodes in the shortest path

    while queue:
        current_distance, current_node = heapq.heappop(queue)

        if current_node == dest:
            break  # Reached the destination node

        if current_distance > distances[current_node]:
            continue  # Skip if a shorter path to current_node has already been found

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    path = []
    current = dest
    while current != src:
        path.append(current)
        current = previous_nodes[current]
    path.append(src)
    path.reverse()

    return path


