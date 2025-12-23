# DFS - Depth-First Search

visited = set() # Set to keetp track of visited nodes
def dfs(visited, graph, node):
    if node not in visited:
        print(node, end=" ")
        visited.add(node) # Mark as visited

    # Recursively visit all neighbors
    for neighbor in graph[node]:
        dfs(visited, graph, neighbor)

# Representing the graph as a dictionary (Adjacency List)
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}
dfs(visited, graph, 'A')
