import collections

def bfs(graph, root):
    visited = set()
    queue = collections.deque([root]) # Initialize queue with root
    visited.add(root)

    while queue:
        # Dequeu a vertex from queue
        vertex = queue.popleft()
        print(vertex, end=" ")

        # Get all adjacent vertices of the dequeued vertex
        # If a adjacent has not been visited, mark it and enqueue it
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

# Representing the graph as a dictionary (Adjacency List)
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}
bfs(graph, 'A')
