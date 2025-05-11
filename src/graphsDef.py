from pathlib import Path

"""
    Class Node contains information about the image that represents the state, and a list of transitions 
    
    Attributes:
        name (str): State name
        image (Path): Path to image of the state
        transitions (list): List of transitions to change state
"""
class Node:
    def __init__(self, name:str):
        self.name = name
        self.image = None
        self.transitions = []

    def set_image(self, image_path: str):
        if Path(image_path).exists():
            self.image = Path(image_path)
            print(f"Image set to '{image_path}' for node '{self.name}'.")
        else:
            print(f"Error: Image path '{image_path}' does not exist.")

    def add_transition(self, transition):
        print(f"Adding transition from '{self.name}' to '{transition.destination.name}'.")
        self.transitions.append(transition)

    """
        Removes the transition to a node
    """
    def remove_transition(self, _node):
        for i, t in enumerate(self.transitions):
            if t.destination == _node:
                # Remove only the first occurrence
                print(f"Removing transition from '{self.name}' to '{_node.name}'.")
                del self.transitions[i]
                break
        
    """
        Updates the name of the node
    """
    def update_name(self, new_name: str):
        print(f"Changing node name from '{self.name}' to '{new_name}'.")
        self.name = new_name

"""
    Class Transition contains a condition to go to destination node
    
    Attributes:
        destination (Node): Destination node
        condition (callable): Condition function
        action (ActionType): Type of action (CLICK, etc.)
        image (str): Image path for the action
        text (str): Text for CLICK_AND_TYPE
        drag_image (str): Drag image for DRAG_AND_DROP
        drop_image (str): Drop image for DRAG_AND_DROP
"""
class Transition:
    def __init__(self, destination, condition= None):
        self.destination = destination
        self.condition = condition if condition is not None else (lambda: True)
        self.action = None
        self.image = None
        self.text = None
        self.drag_image = None
        self.drop_image = None

    """
        Check the condition of transition
        Returns true if condition is valid, false otherwise
    """
    def is_valid(self) -> bool:
        return self.condition()
   
    def update_action(self, action):
        """Update the action type of this transition."""
        self.action = action

    def update_image(self, image_path: str):
        """Update the image for this transition."""
        self.image = image_path

    def update_text(self, text: str):
        """Update the text for CLICK_AND_TYPE transitions."""
        self.text = text

    def update_drag_and_drop(self, drag_image: str, drop_image: str):
        """Update drag and drop images for this transition."""
        self.drag_image = drag_image
        self.drop_image = drop_image
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
    def add_node(self, name:str) -> Node:
        for node in self.nodes:
            if node.name == name:
                print(f"Node with name '{name}' already exists.")
                return None  
        n = Node(name)
        self.nodes.append(n)
        return n
    
    """
        Removes the node from the graph and removes all transitions pointing to it
        Returns False if the node was not found or cannot be removed, True otherwise
    """
    def remove_node(self, node:Node) -> bool:
        if node not in self.nodes:
            print(f"Node {node.name} is not in graph.")
            return False

        self.nodes.remove(node)

        for other_node in self.nodes:
            other_node.transitions = [t for t in other_node.transitions if t.destination is not node]

        print(f"Node '{node.name}' has been removed.")
        return True

    """
        Adds a transition to the graph
        Returns False if the origin or destination node is not in the graph, True otherwise
    """
    def add_transition(self, origin, destination, condition=None) -> Transition:
        """
        Adds a transition to the graph.
        Returns the new Transition, or None if origin/destination no están en el grafo.
        """
        if origin not in self.nodes or destination not in self.nodes:
            if origin not in self.nodes:
                print(f"Origin node '{origin.name}' is not in the graph.")
            if destination not in self.nodes:
                print(f"Destination node '{destination.name}' is not in the graph.")
            return None

        condition = condition if condition is not None else (lambda: True)
        t = Transition(destination, condition)
        origin.add_transition(t)
        return t

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
        Updates the name of a node and ensures all transitions pointing to it remain valid.
    """
    def update_node_name(self, node: Node, new_name: str):
        if node not in self.nodes:
            print(f"Node '{node.name}' is not in the graph.")
            return False
        node.update_name(new_name)
        print(f"Node name updated to '{new_name}'.")
        return True

    """
        Clears the graph by removing all nodes and transitions.
    """
    def clear(self):
        self.nodes.clear()
        self.startNode = None
        print("Graph cleared.")