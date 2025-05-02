from pathlib import Path

class Node:
    """
    Class Node contains information about the image that represents the state, and a list of transitions 
    
    Atributes:
        name (str): State name
        image (Path): Path to image of the state
        transitions (list): List of transitions to change state
    """

    def __init__(self, _name:str, _image:Path):
        self.name = _name
        self.image = _image
        self.transitions= []

    def add_transition(self, _transition):
        self.transitions.append(_transition)

    # Im not using this function, but we can keep it just in case
    def remove_transition(self, _node):
        """
        Removes the transition to a node
        """
        for transition in self.transitions:
            if transition.destination == _node:
                self.transitions.remove(_node)
                break


class Transition:
    """
    Class Transition contains a condition to go to destination node
    
    Atributes:
        destination (Node): Destination node
        condition (lambda): Condition to fo to destination
    """

    def __init__(self, _destination, _condition):
        self.destination = _destination
        self.condition = _condition

    def is_valid(self) -> bool:
        """
        Function to check the condition of transition
        Returns true if condition is valid, false otherwise
        """
        return self.condition()
    

class Graph:
    """
    Class Graph contains the nodes and has functions to go through them
    
    Atributes:
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
        print(f"node has been removed")
        return True

    def add_transition(self, _origin, _destination, _condition = None):
        for node in self.nodes:
            if node is _origin:
                # In case we dont want a condition
                if _condition is None:
                    node.add_transition(Transition(_destination, lambda:True))
                else:
                    node.add_transition(Transition(_destination, _condition))
                break
    
    def set_start_node(self, _node):
        self.startNode = _node

    # Recursive function to visit all the nodes using dfs
    def dfs(self, actual:Node = None, visited:list = None):
        if visited is None:
            visited = set()
        if actual is None:
            actual = self.startNode
            
        # If the actual node has been visited, it returns
        if actual in visited:
            return
        print(f"fisiting node: {actual.name}")
        # We go through the entire list of transitions and its destinations
        for transition in actual.transitions:
            if transition.is_valid(): # if condition is valid then check it destinations
                self.dfs(transition.destination, visited)

g = Graph()
n1 = g.add_node("1", Path("imgs/image.png"))
n2 = g.add_node("2", Path("imgs/image.png"))
n3 = g.add_node("3", Path("imgs/image.png"))
n4 = g.add_node("4", Path("imgs/image.png"))
n5 = g.add_node("5", Path("imgs/image.png"))

g.set_start_node(n1)
g.add_transition(n1,n2)
g.add_transition(n1,n3)
g.add_transition(n3,n4)
g.add_transition(n3,n5)

g.dfs()

g.remove_node(n3)

g.dfs()