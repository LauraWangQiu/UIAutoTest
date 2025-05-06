from pathlib import Path

"""
    Class Node contains information about the image that represents the state, and a list of transitions 
    
    Attributes:
        name (str): State name
        image (Path): Path to image of the state
        transitions (list): List of transitions to change state
"""
class Node:
    def __init__(self, name:str, image:Path):
        self.name = name
        self.image = image
        self.transitions = []

    def add_transition(self, transition):
        for t in self.transitions:
            if t.destination == transition.destination and t.condition.__code__.co_code == transition.condition.__code__.co_code:
                print(f"Transition to {t.destination.name} already exists.")
                return
        self.transitions.append(transition)

    """
        Removes the transition to a node
    """
    def remove_transition(self, _node):
        self.transitions = [t for t in self.transitions if t.destination != _node]

    """
        Updates the name of the node.
    """
    def update_name(self, new_name: str):
        print(f"Changing node name from '{self.name}' to '{new_name}'")
        self.name = new_name

"""
    Class Transition contains a condition to go to destination node
    
    Attributes:
        destination (Node): Destination node
        condition (lambda): Condition to go to destination
"""
class Transition:
    def __init__(self, destination, condition):
        self.destination = destination
        self.condition = condition

    """
        Check the condition of transition
        Returns true if condition is valid, false otherwise
    """
    def is_valid(self) -> bool:
        return self.condition()

"""
    Class Graph contains the nodes and has functions to go through them
    
    Attributes:
        nodes (list): List of nodes
        startNode (Node): root node or main node
"""
class Graph:
    def __init__(self):
        self.nodes = []
        self.startNode = None

    """
        Adds a node to the graph
        Returns new node
    """
    def add_node(self, name:str, image:Path) ->Node:
        for node in self.nodes:
            if node.name == name:
                print(f"Node with name '{name}' already exists.")
                return None  
        n = Node(name, image)
        self.nodes.append(n)
        return n
    
    """
        Removes the node from the graph and removes all transitions pointing to it
        Returns False if the node was not found or cannot be removed, True otherwise
    """
    def remove_node(self, node:Node) -> bool:
        if node not in self.nodes:
            print(f"Node {node.name} is not in graph")
            return False
        
        self.nodes.remove(node)

        for node in self.nodes:
            node.transitions = [t for t in node.transitions if t.destination is not node]
        
        print(f"Node '{node.name}' has been removed")
        return True

    """
        Adds a transition to the graph
        Returns False if the origin or destination node is not in the graph, True otherwise
    """
    def add_transition(self, origin, destination, condition=None):
        if origin not in self.nodes or destination not in self.nodes:
            print("Origin or destination node is not in the graph.")
            return

        condition = condition if condition is not None else lambda: True
        origin.add_transition(Transition(destination, condition))

    """
        Sets the start node of the graph.
    """
    def set_start_node(self, node):
        if node is None:
            print("Error: The start node cannot be None.")
            return False

        if node not in self.nodes:
            print(f"Error: The node '{node.name}' is not part of the graph.")
            return False

        self.startNode = node
        print(f"Start node set to '{node.name}'.")
        return True

    """
        Depth First Search (DFS) algorithm to traverse the graph.
        It starts from the start node and visits all reachable nodes.
        Returns a set of visited nodes.
    """
    def dfs(self, actual:Node = None, visited:set = None) -> set:
        if visited is None:
            visited = set()
        if actual is None:
            actual = self.startNode
            
        if actual in visited:
            return visited
        print(f"visiting node: {actual.name}")
        visited.add(actual)
        for transition in actual.transitions:
            if transition.is_valid():
                self.dfs(transition.destination, visited)
        
        return visited
    
    """
        A* algorithm to find the shortest path from source to destination node.
        It uses a cost parameter to determine the cost of the path.
        Returns the shortest path as a set of nodes.
    """
    def a_star(self, cost: int, src: Node, dst: Node, actual: Node = None, path: set = None) -> set:
        if src == dst:
            print("Source node and destination node are the same.")
            return path
        if path == None:
            path = set()
        if actual == None:
            actual = src
        if actual == dst:
            path.add(actual)
            return path
        
        path.add(actual)
        paths = []
        for transition in actual.transitions:
            if transition.is_valid():   
                neighbor = transition.destination
                if neighbor not in path:
                    aux_path = self.a_star(cost + 1, src, dst, neighbor, path.copy())
                    if aux_path is not None and dst in aux_path:
                        paths.append(aux_path)
        
        if paths:
            return min(paths, key = len)
    
    """
        Updates the name of a node and ensures all transitions pointing to it remain valid.
    """
    def update_node_name(self, node: Node, new_name: str):
        if node not in self.nodes:
            print(f"Node '{node.name}' is not in the graph.")
            return False
        node.update_name(new_name)
        print(f"Node name updated to '{new_name}'")
        return True

# --------------------
# Example of use
# --------------------

# g = Graph()
# n1 = g.add_node("1", Path("imgs/image.png"))
# n2 = g.add_node("2", Path("imgs/image.png"))
# n3 = g.add_node("3", Path("imgs/image.png"))
# n4 = g.add_node("4", Path("imgs/image.png"))
# n5 = g.add_node("5", Path("imgs/image.png"))

# g.set_start_node(n1)
# g.add_transition(n1,n2)
# g.add_transition(n1,n3)
# g.add_transition(n3,n4)
# g.add_transition(n3,n5)

# g.dfs(n3)
# --->  Had visitted:   3, 4, 5

# g.remove_node(n3)

# visit = g.dfs()
# --->  Had visitted:   1, 2

# print([v.name for v in visit])
# --->  Prints:         ['1', '2']