# Minimum Genetic Mutation

from collections import deque

def is_one_mutation_apart(gene1: str, gene2: str) -> bool:
    diff_count = 0

    for char1, char2 in zip(gene1, gene2):
        if char1 != char2:
            diff_count += 1

            if diff_count > 1:
                return False
    
    return diff_count == 1

def build_graph(nodes: list[str]) -> dict:
    # Initialize the adjacency list dict
    adj_lst = {n: [] for n in nodes}
    
    # Use a nested loop to check every unique pairs of nodes
    for i in range(len(nodes)):
        n1 = nodes[i]

        # Start the inner loop from i + 1 to avoid checking pairs twice
        for j in range(i + 1, len(nodes)):
            n2 = nodes[j]

            if is_one_mutation_apart(n1, n2):
                adj_lst[n1].append(n2)
                adj_lst[n2].append(n1)
    return adj_lst

def compute_nodes(start_gene: str, end_gene: str, bank: list[str]) -> list[str]:
    # Initialize a set with all the bank genes
    all_genes_set = set(bank)

    # Add the start_gene
    all_genes_set.add(start_gene)
    all_genes_set.add(end_gene)

    # Convert the set back to a list 
    nodes = list(all_genes_set)

    return nodes

def min_mutation(start_gene, end_gene, bank):
    nodes = compute_nodes(start_gene, end_gene, bank)
    adj_lst = build_graph(nodes)

    # Base case
    # -- Start gene is already equal to the end gene. 
    if start_gene == end_gene:
        return 0

    # Ensure the end gene is a valid node
    if end_gene not in bank:
        return -1

    # Breadth-First Search (BFS)

    # -- The queue stores a tuple of (current_gene, steps_taken)
    queue = deque([(start_gene, 0)])

    # -- The visited set prevents cycles and redundant work
    visited = {start_gene}

    # -- BFS search loop
    while queue:
        current_gene, steps = queue.popleft()
        # Explore neighbors
        for neighbor in adj_lst.get(current_gene, []):
            # Goal check
            if neighbor == end_gene:
                return steps + 1 # Shortest path found!!
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, steps + 1))

    return -1 # Failure -- target not reached

start_gene = "AACCGGTT"
end_gene = "AAACGGTA"
bank = ["AACCGGTA","AACCGCTA","AAACGGTA"]

print(min_mutation(start_gene, end_gene, bank))
