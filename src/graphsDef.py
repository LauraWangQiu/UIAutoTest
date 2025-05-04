from pathlib import Path

class Node:
    """
    Class Node contains information about the image that represents the state, and a list of transitions 
    
    Attributes:
        name (str): State name
        image (Path): Path to image of the state
        transitions (list): List of transitions to change state
    """

    def __init__(self, _name:str, _image:Path):
        self.name = _name
        self.image = _image
        self.transitions = []

    def add_transition(self, _transition):
        # Check if the transition already exists
        for t in self.transitions:
            if t.destination == _transition.destination and t.condition.__code__.co_code == _transition.condition.__code__.co_code:
                print(f"Transition to {t.destination.name} already exists.")
                return
        self.transitions.append(_transition)

    def remove_transition(self, _node):
        """
        Removes the transition to a node
        """
        self.transitions = [t for t in self.transitions if t.destination != _node]
    def update_name(self, new_name: str):
        """
        Updates the name of the node.
        """
        print(f"Changing node name from '{self.name}' to '{new_name}'")
        self.name = new_name

class Transition:
    """
    Class Transition contains a condition to go to destination node
    
    Attributes:
        destination (Node): Destination node
        condition (lambda): Condition to go to destination
    """

    def __init__(self, _destination, _condition):
        self.destination = _destination
        self.condition = _condition

    def is_valid(self) -> bool:
        """
        Check the condition of transition
        Returns true if condition is valid, false otherwise
        """
        return self.condition()
    

class Graph:
    """
    Class Graph contains the nodes and has functions to go through them
    
    Attributes:
        nodes (list): List of nodes
        startNode (Node): root node or main node
    """

    def __init__(self):
        self.nodes = []
        self.startNode = None

    def add_node(self, _name:str, _image:Path) ->Node:
        """
        Adds a node to the graph
        Returns new node
        """
        for node in self.nodes:
            if node.name == _name:
                print(f"Node with name '{_name}' already exists.")
                return None  

        n = Node(_name,_image)
        # Adds node to the list of nodes
        self.nodes.append(n)
        return n
    
    def remove_node(self, _node:Node) -> bool:
        """
        Removes the node from the graph and removes all transitions pointing to it
        Returns False if the node was not found or cannot be removed, True otherwise
        """
        # If node is not in graph
        if _node not in self.nodes:
            print(f"Node {_node.name} is not in graph")
            return False
        
        # Remove all the transitions to _node
        for node in self.nodes:
            node.transitions = [t for t in node.transitions if t.destination is not _node]
        
        # Remove node from list of nodes
        self.nodes.remove(_node)
        print(f"Node '{_node.name}' has been removed")
        return True

    def add_transition(self, _origin, _destination, _condition=None):
        if _origin not in self.nodes or _destination not in self.nodes:
            print("Origin or destination node is not in the graph.")
            return

        condition = _condition if _condition is not None else lambda: True
        _origin.add_transition(Transition(_destination, condition))

    def set_start_node(self, _node):
        """
        Sets the start node of the graph.
        """
        if _node is None:
            print("Error: The start node cannot be None.")
            return False

        if _node not in self.nodes:
            print(f"Error: The node '{_node.name}' is not part of the graph.")
            return False

        self.startNode = _node
        print(f"Start node set to '{_node.name}'.")
        return True

    # Recursive function to visit all the nodes using dfs
    def dfs(self, actual:Node = None, visited:set = None) -> set:
        if visited is None:
            visited = set()
        if actual is None:
            actual = self.startNode
            
        # If the actual node has been visited, it returns
        if actual in visited:
            return visited
        print(f"visiting node: {actual.name}")
        # Add the actual node to the visited nodes set
        visited.add(actual)
        # We go through the entire list of transitions and its destinations
        for transition in actual.transitions:
            if transition.is_valid(): # if condition is valid then check it destinations
                self.dfs(transition.destination, visited)
        
        # Returns the visited nodes
        return visited
    
    # A star algorithm. More or less.
    def a_star(self, cost: int, src: Node, dst: Node, actual: Node = None, path: set = None) -> set:
        # If the src and the dst are the same then it returns.
        if src == dst:
            print("Source node and destination node are the same.")
            return path
        # If path is not set then it is created.
        if path == None:
            path = set()
        # If actual is not set then it is the source.
        if actual == None:
            actual = src
        # If actual is the destination then return path.
        if actual == dst:
            path.add(actual)
            return path
        
        path.add(actual) # Add the actual node to the path.
        
        paths = [] # List of paths.
        
        # Checks every transition in the node.
        for transition in actual.transitions:
            # If it is valid then the destination is saved.
            if transition.is_valid():   
                 neighbor = transition.destination
                 # If it is not in the path then it continues.
                 if neighbor not in path:
                     aux_path = self.a_star(cost + 1, src, dst, neighbor, path.copy())
                     if aux_path is not None and dst in aux_path:
                         paths.append(aux_path)
        
        # Returns the shorter path.
        if paths:
            return min(paths, key = len)
    
    
    def update_node_name(self, node: Node, new_name: str):
            """
            Updates the name of a node and ensures all transitions pointing to it remain valid.
            """
            if node not in self.nodes:
                print(f"Node '{node.name}' is not in the graph.")
                return False
             # Update the node's name
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