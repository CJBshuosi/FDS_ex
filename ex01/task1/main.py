from collections import deque, defaultdict  # Import deque for queue operations and defaultdict for graph
import networkx as nx  # Import networkx for graph operations
from networkx.drawing.nx_pydot import write_dot  # Import write_dot to export graph as DOT format
import json  # Import json for reading/writing JSON files

"""
TASK 1: Vector Clock Computation and Causal Graph Construction
This program implements the Vector Clock algorithm for distributed systems:
1. Compute vector clocks for each event in a DAG(Directed Acyclic Graph)
2. Build a complete causal relationship graph
3. Reduce redundant edges

Example: For 3 processes A, B, C:
- Event A1: [1, 0, 0] (first event in process A)
- Event B1: [0, 1, 0] (first event in process B)
- Event A2 (after B1): [1, 1, 0] (take max of parent clocks, then increment A's component)
"""

def find_root(data):  # Find the root event (event with no parents)
    for branch in data:
        for event, parents in data[branch].items():
            if parents == []:
                return event, branch


def get_parents(data, event):  # Get all parent events of a given event
    for branch in data:
        if event in data[branch]:
            return data[branch][event]
    return []


def build_event_graph(data):    # data is {"A": {"A1": [], "A2": ["A1"]}, "B": {"B1": [], "B2": ["B1"]}}
    graph = defaultdict(list)
    for branch in data:  # For each branch
        for event, parents in data[branch].items():  # For each event in branch
            graph[event]
            for parent in parents:
                graph[parent].append(event)  # Add edge: parent -> event    A2-> A1
    return graph


# Kahn's Algorithm for topological sorting of DAG
# Example: Graph A1 -> A2 -> A3, B1 -> A2
# In-degrees: A1=0, A2=2, A3=1, B1=0
# Topological order: [A1, B1, A2, A3] or [B1, A1, A2, A3]
def kahns_algorithm(graph):
    in_degree = {u: 0 for u in graph}
    for u in graph:
        for v in graph[u]:  # assume graph = {"A1": ["B2"], "A2": ["A1"]}
            in_degree[v] += 1  # Increment in-degree of child.

    queue = deque([u for u in graph if in_degree[u] == 0])  # Add all nodes with in-degree 0 to queue
    L = []  # List to store topological order

    while queue:
        u = queue.popleft()  # Remove node with in-degree 0 from queue
        L.append(u)
        for v in graph[u]:
            in_degree[v] -= 1  # Because we removed parent, Decrement in-degree of child
            if in_degree[v] == 0:  # If child's in-degree becomes 0
                queue.append(v)
    return L

def compute_vector_clock(data):
    vector_clocks = {}
    branch_indices = {branch: idx for idx, branch in enumerate(data.keys())}  # Map branch names to indices: {"A": 0, "B": 1}

    event_graph = build_event_graph(data)  # Build adjacency list from event data.   {"A1": ["B2"], "A2": ["A1"]}
    topo_order = kahns_algorithm(event_graph)  # Get topological order of events

    # Initialize root event (first event with no parents)
    _, root_branch = find_root(data)
    vector_clocks[topo_order[0]] = [0] * len(data)  # Initialize root clock to [0, 0, ..., 0]
    vector_clocks[topo_order[0]][branch_indices[root_branch]] += 1  # Increment root's branch component
    topo_order = topo_order[1:]

    # Process remaining events in topological order
    while topo_order:
        event = topo_order[0]
        clock = [0] * len(data)

        # Take maximum of all parent clocks
        for parent in get_parents(data, event):
            parent_clock = vector_clocks[parent]  # Get parent's vector clock
            clock = [max(c, pc) for c, pc in zip(clock, parent_clock)]  # [1,0,0] [0,1,0] => [1,1,0]

        # Increment the component corresponding to current event's branch
        event_branch = [branch for branch in data if event in data[branch]][0]  # Find which branch this event belongs to
        clock[branch_indices[event_branch]] += 1  # Increment that branch's component [1,1,0+1]
        vector_clocks[event] = clock
        topo_order = topo_order[1:]

    return vector_clocks

# TASK 2: Build complete causal graph from vector clocks
# Causal precedence: vector a precedes b if all components a <= b AND at least one a < b
# Example: [1,0,0] precedes [2,1,0] because 1<=2, 0<=1, 0<=0 and 1<2

def causally_precedes(pre_node_vector, post_node_vector):
    less = True
    strickly_less = False
    for i, j in zip(pre_node_vector, post_node_vector):
        if i > j:   # if there is a component that is greater, then it is not a causal precedence
            less = False
            break
        if i < j:  # Then if  there is a component that is strictly less, then it is a causal precedence
            strickly_less = True
    return less and strickly_less

def build_edges(event_nodes, vector_clocks):    # In this function, we need to determine if there is a causal relationship between two events.
    edges = {nodes: set() for nodes in event_nodes}
    for pre_index, pre_node in enumerate(event_nodes):
        for post_index, post_node in enumerate(event_nodes):
            if pre_index != post_index and causally_precedes(vector_clocks[pre_node], vector_clocks[post_node]):  # If pre causally precedes post
                edges[post_node].add(pre_node)  # Add edge from post to pre (child to parent direction)
    return edges

def create_graph(edges):  # Convert edge dictionary to NetworkX directed graph
    G = nx.DiGraph()
    for node, neighbors in edges.items():   # edges = {"A1": {"B1", "B2"}, "A2": {"A1"}}
        for neighbor in neighbors:
            G.add_edge(node, neighbor)  # Add edge to graph 
    return G

# Remove transitive edges: if path A->B->C exists, remove direct edge A->C because it's redundant

def reduction(edges):
    nodes = list(edges.keys())  # nodes = ["A1", "A2", "B1", "B2"]
    reach = {node: set() for node in nodes}

    def dfs(start, current, visited):  # DFS to find all reachable nodes from start
        for next in edges[current]:
            if next not in visited:
                visited.add(next)
                reach[start].add(next)
                dfs(start, next, visited)

    for node in nodes:
        dfs(node, node, set())  # Find all nodes reachable from this node. reach = {"A1": {"B1", "B2"}, "B2": {"B1"}}

    reduced = {node: set() for node in nodes}
    for pivot_node in nodes:
        for node_neighbor in edges[pivot_node]:
            redundant = False
            for neighbor in edges[pivot_node]:  # edges = {"A1": {"B1", "B2"}, "A2": {"A1"}}
                if neighbor != node_neighbor and node_neighbor in reach[neighbor]:  # node_neighbor = B1, neighbor = B2,;B1 in reach[B2]
                    redundant = True  # Mark as redundant
                    break
            if not redundant:
                reduced[pivot_node].add(node_neighbor)
    return reduced

def main(): 
    # Step 1: Load data and compute vector clocks
    data = json.load(open('data.json', 'r'))    # data is like {"A": {"A1": [], "A2": ["A1"]}, "B": {"B1": [], "B2": ["B1"]}}
    vector_clocks = compute_vector_clock(data)  # vector_clocks = {"A1": [1,0,0], "A2": [2,0,0], ...}
    print(vector_clocks)
    with open('vector_data.json', 'w') as f:
        json.dump(vector_clocks, f)

    # Step 2: Build complete causal graph (with all edges)
    event_nodes = list(vector_clocks.keys())
    full_edges = build_edges(event_nodes, vector_clocks)    # full_edges = {"A1": {"B1", "B2"}, "A2": {"A1"}}
    G = create_graph(full_edges)
    write_dot(G, 'full_edges.dot')

    # Step 3: Reduce redundant edges
    reduction_edges = reduction(full_edges)
    G_reduced = create_graph(reduction_edges)
    write_dot(G_reduced, 'reduced_edges.dot')

if __name__ == '__main__':  # Entry point
   main()  # Run main function
