import networkx as nx

def assign_roles(players, roles):
    """
    Assigns roles to players based on their preferences and role capacities.
    If there are more players than available positions, only the best assignments
    (minimizing dissatisfaction) are chosen, and some players remain unassigned.
    
    Parameters:
      players: a dict mapping player names to a list of roles (strings)
               in order of preference (most preferred first).
      roles: a dict mapping role names to the allowed capacity (int) in the group.

    Returns:
      A dict mapping each assigned player to the assigned role.
      (Players who are not selected will not appear in the returned dictionary.)
    """
    G = nx.DiGraph()

    # Define special source and sink nodes
    source = "source"
    sink = "sink"
    G.add_node(source)
    G.add_node(sink)

    # Determine the total number of available positions.
    num_positions = sum(roles.values())

    # Set demands for the source and sink.
    # The source will supply exactly num_positions units,
    # and the sink will demand num_positions units.
    G.nodes[source]['demand'] = -num_positions
    G.nodes[sink]['demand'] = num_positions

    # All other nodes default to demand 0.

    # 1. Connect the source to each player with capacity 1 (each player can be chosen at most once)
    for player in players:
        G.add_edge(source, player, capacity=1, weight=0)

    # 2. Connect each player to the roles they listed.
    #    The cost (weight) is determined by the player's rank for that role (0 for top choice, etc.).
    for player, pref_list in players.items():
        for rank, role in enumerate(pref_list):
            if role in roles:
                G.add_edge(player, role, capacity=1, weight=rank)

    # 3. Connect each role to the sink.
    #    The capacity of each edge is the number of players allowed in that role.
    for role, capacity in roles.items():
        G.add_edge(role, sink, capacity=capacity, weight=0)

    # 4. Compute the minimum cost flow.
    try:
        flowDict = nx.algorithms.flow.min_cost_flow(G)
    except nx.NetworkXUnfeasible:
        raise Exception("No feasible assignment exists with the given preferences and role limits.")

    # 5. Parse the result to build the assignment.
    assignment = {}
    for player in players:
        # Check if this player was selected (i.e. if any flow went from the player to a role)
        for role, flow in flowDict[player].items():
            if flow > 0:
                assignment[player] = role
                break  # only one role per player
    return assignment

# --- Example usage ---

players = {
    "Player1":  ["Tank", "Healer", "Ranged", "Caster", "Melee"],
    "Player2":  ["Healer", "Melee", "Caster", "Ranged"],
    "Player3":  ["Tank", "Melee", "Caster", "Ranged"],
    "Player4":  ["Healer", "Tank", "Melee", "Caster", "Ranged"],
    "Player5":  ["Tank", "Healer", "Melee"],
    "Player6":  ["Tank", "Caster"],
    "Player7":  ["Ranged", "Healer", "Caster", "Melee", "Tank"],
    "Player8":  ["Melee", "Tank"],
    "Player9":  ["Ranged", "Caster", "Healer"]
}

roles = {
    "Tank": 2,
    "Healer": 2,
    "Ranged": 1,
    "Caster": 1,
    "Melee": 2
}

assignment = assign_roles(players, roles)

print("Final Role Assignment:")
for player, role in assignment.items():
    print(f"  {player} → {role}")
