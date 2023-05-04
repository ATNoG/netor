

def dijkstra(graph, start, end):
    dist = {node: float('inf') for node in graph}
    dist[start] = 0

    # The distance to each node is initially unknown.
    queue = [start]

    # Keep track of the path to each node.
    prev = {node: None for node in graph}

    # The main loop.
    while queue:
        # Pop the next node with the smallest distance.
        curr = min(queue, key=lambda node: dist[node])
        queue.remove(curr)

        # Stop if we've reached the end.
        if curr == end:
            break

        # Update the distances to the neighbors of the current node.
        for neighbor, threshold in graph[curr].items():
            alt = dist[curr] + 1/threshold
            if alt < dist[neighbor]:
                dist[neighbor] = alt
                prev[neighbor] = curr
                queue.append(neighbor)
    
    path = []
    node = end
    while node is not None:
        path.append(node)
        node = prev[node]

    # Reverse the path so that it goes from the start to the end.
    path = path[::-1]

    return path