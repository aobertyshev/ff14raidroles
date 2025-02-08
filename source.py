import json
import networkx as nx
import matplotlib.pyplot as plt

def assign_roles(players, roles):
    """
    Assigns roles to players based on their preferences and role capacities.
    If there are more players than positions, only the best assignments are made.

    Parameters:
      players: dict mapping player names to a list of roles (strings) in order of preference.
      roles: dict mapping role names to allowed capacity (int) in the group.

    Returns:
      assignment: dict mapping each assigned player to the assigned role.
      G: the constructed flow network (a DiGraph) used for the assignment.
    """
    G = nx.DiGraph()

    # Define special source and sink nodes.
    source = "source"
    sink = "sink"
    G.add_node(source)
    G.add_node(sink)

    # Total available positions.
    num_positions = sum(roles.values())

    # Set demands: supply at source and demand at sink equals num_positions.
    G.nodes[source]['demand'] = -num_positions
    G.nodes[sink]['demand'] = num_positions

    # 1. Connect the source to each player (each edge has capacity 1, cost 0).
    for player in players:
        G.add_edge(source, player, capacity=1, weight=0)

    # 2. Connect each player to the roles they listed.
    #    The cost (weight) is the rank in their preference list.
    for player, pref_list in players.items():
        for rank, role in enumerate(pref_list):
            if role in roles:
                G.add_edge(player, role, capacity=1, weight=rank)

    # 3. Connect each role to the sink with capacity equal to allowed number.
    for role, capacity in roles.items():
        G.add_edge(role, sink, capacity=capacity, weight=0)

    # 4. Compute the minimum cost flow.
    try:
        flowDict = nx.algorithms.flow.min_cost_flow(G)
    except nx.NetworkXUnfeasible:
        raise Exception("No feasible assignment exists with the given preferences and role limits.")

    # 5. Parse the flow to build the assignment.
    assignment = {}
    for player in players:
        for role, flow in flowDict[player].items():
            if flow > 0:
                assignment[player] = role
                break  # one role per player

    return assignment, G

def draw_flow_graph(G, players, assignment, filename="flow_graph.png"):
    """
    Draws the flow network G and annotates player nodes with their assigned role (if any).
    Saves the resulting drawing to a PNG file.

    Parameters:
      G: the NetworkX graph to draw.
      players: dict of players (used to distinguish player nodes).
      assignment: dict mapping players to their assigned role.
      filename: name of the output PNG file.
    """
    # Use spring layout (with a fixed seed for reproducibility)
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(12, 8))

    # Create a custom label dictionary.
    labels = {}
    for node in G.nodes():
        # For player nodes, add the assigned role to the label if available.
        if node in players:
            if node in assignment:
                labels[node] = f"{node}\n({assignment[node]})"
            else:
                labels[node] = node
        else:
            labels[node] = node

    # Draw nodes.
    nx.draw_networkx_nodes(G, pos, node_size=1500, node_color="lightblue")
    # Draw directed edges.
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=20, edge_color="gray")
    # Draw node labels.
    nx.draw_networkx_labels(G, pos, labels, font_size=10)

    # Optionally, draw edge labels (here showing the weight/cost on each edge).
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(filename)
    print(f"Graph saved as {filename}")
    # Uncomment the next line to display the graph interactively.
    # plt.show()

if __name__ == "__main__":
    # Read players from a JSON file
    with open("players.json", "r") as f:
        players = json.load(f)

    # Define roles and their capacities.
    roles = {
        "Tank": 2,
        "Healer": 2,
        "Ranged": 1,
        "Caster": 1,
        "Melee": 2
    }

    # Compute the assignment and build the graph.
    assignment, G = assign_roles(players, roles)

    # Print assigned roles.
    print("Final Role Assignment:")
    for player, role in assignment.items():
        print(f"  {player} → {role}")

    # Draw the flow graph and save it as a PNG.
    draw_flow_graph(G, players, assignment, filename="flow_graph.png")
