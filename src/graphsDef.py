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

    def remove_transition(self, _node):
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
        return self.condition()
    

class Graph:
    """
    Class Transition contains a condition to go to destination node
    
    Atributes:
        nodes (list): List of nodes
    """
    def __init__(self):
        self.nodes = []
        self.startNode = None

    def add_node(self, _name:str, _image:Path) ->Node:
        n = Node(_name,_image)
        self.nodes.append(n)
        return n
    
    def add_transition(self, _origin, _destination, _condition = None):
        for node in self.nodes:
            if node is _origin:
                if _condition is None:
                    node.add_transition(Transition(_destination, lambda:True))
                else:
                    node.add_transition(Transition(_destination, _condition))
                break
    
    def set_start_node(self, _node):
        self.startNode = _node

    # Recursive method to visit all the nodes using dfs
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