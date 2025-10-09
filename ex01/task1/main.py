from collections import deque, defaultdict
import networkx as nx
from networkx.drawing.nx_pydot import write_dot
import json

"""
task1_1 Compute vector clocks from given DAG
"""
def find_root(data):
    for branch in data:
        for event, parents in data[branch].items():
            if parents == []:
                return event, branch


def get_parents(data, event):
    for branch in data:
        if event in data[branch]:
            return data[branch][event]
    return []


def build_event_graph(data):
    graph = defaultdict(list)
    for branch in data:
        for event, parents in data[branch].items():
            graph[event]  # Ensure each event is in graph
            for parent in parents:
                graph[parent].append(event)
    return graph


# We used Kahns algorithm to get topological order of events
# The idea came from: https://www.baeldung.com/cs/dag-topological-sort
def kahns_algorithm(graph):
    in_degree = {u: 0 for u in graph}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1

    queue = deque([u for u in graph if in_degree[u] == 0])
    L = []

    while queue:
        u = queue.popleft()
        L.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    return L

"""
    Compute vector clock for each event in the given data
    Input: JSON file containing DAG
    Output: JSON file containing vector clocks for each event
    Format of output JSON: { "Commit_Name": list of clock values}
"""
def compute_vector_clock(data):
    vector_clocks = {}
    branch_indices = {branch: idx for idx, branch in
                      enumerate(data.keys())}  # Give each branch an index for vector clock

    # Create a topological order of events
    event_graph = build_event_graph(data)
    topo_order = kahns_algorithm(event_graph)

    # Set vector clock for root event (first event in topological order)
    vector_clocks[topo_order[0]] = [0] * len(data)
    vector_clocks[topo_order[0]][branch_indices[find_root(data)[1]]] += 1
    topo_order = topo_order[1:]

    while topo_order:
        event = topo_order[0]
        clock = [0] * len(data)
        # Clock is max of parents in each pos in clock
        for parent in get_parents(data, event):
            parent_clock = vector_clocks[parent]
            clock = [max(c, pc) for c, pc in zip(clock, parent_clock)]

        # Increment the index of the branch where the event belongs
        clock[branch_indices[[branch for branch in data if event in data[branch]][0]]] += 1
        vector_clocks[event] = clock
        topo_order = topo_order[1:]

    return vector_clocks

"""
task1_2 Build complete causal graph from vector clocks
"""
def causally_precedes(pre_node_vector, post_node_vector):
    less = True
    strickly_less = False
    for i, j in zip(pre_node_vector, post_node_vector):
        if i < j:
            less = False
            break
        if i > j:
            strickly_less = True
    return less and strickly_less

def build_edges(event_nodes, vector_clocks):
    edges = {nodes: set() for nodes in event_nodes}
    for pre_index, pre_node in enumerate(event_nodes):
        for post_index, post_node in enumerate(event_nodes):
            if pre_index != post_index and causally_precedes(vector_clocks[pre_node], vector_clocks[post_node]):
                edges[pre_node].add(post_node)
    return edges

def create_graph(edges):
    G = nx.DiGraph()
    for node, neighbors in edges.items():
        for neighbor in neighbors:
            G.add_edge(node, neighbor)
    return G

"""
task1_3 Reduction of redundant edges
"""
def reduction(edges):
    nodes = list(edges.keys())
    reach = {node: set() for node in nodes}
    def dfs(start, current, visited):
        for next in edges[current]:
            if next not in visited:
                visited.add(next)
                reach[start].add(next)
                dfs(start, next, visited)

    for node in nodes:
        dfs(node, node, set())

    reduced = {node: set() for node in nodes}
    for pivot_node in nodes:
        for node_neighbor in edges[pivot_node]:
            redundant = False
            for neighbor in edges[pivot_node]:
                if neighbor != node_neighbor and node_neighbor in reach[neighbor]:
                    redundant = True
                    break
            if not redundant:
                reduced[pivot_node].add(node_neighbor)
    return reduced

def main():
    # Load data and compute vector clocks
    data = json.load(open('data.json', 'r'))
    vector_clocks = compute_vector_clock(data)
    print(vector_clocks)
    with open('vector_data.json', 'w') as f:
        json.dump(vector_clocks, f)

    # Build complete causal graph
    event_nodes = list(vector_clocks.keys())
    full_edges = build_edges(event_nodes, vector_clocks)
    G = create_graph(full_edges)
    write_dot(G, 'full_edges.dot')

    #reduction
    reduction_edges = reduction(full_edges)
    G_reduced = create_graph(reduction_edges)
    write_dot(G_reduced, 'reduced_edges.dot')

if __name__ == '__main__':
   main()



