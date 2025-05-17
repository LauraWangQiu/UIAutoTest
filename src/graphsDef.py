# -*- coding: utf-8 -*-
from os import path

"""
    Class Node contains information about the image that represents the state, and a list of transitions 
    
    Attributes:
        name (str): State name
        image (Path): Path to image of the state
        transitions (list): List of transitions to change state
"""
class Node:
    def __init__(self, name):
        self.name = name
        self.image = None
        self.transitions = []

    def set_image(self, image_path):
        if path.exists(image_path):
            self.image = image_path
            print("[INFO] Image set to '" + image_path + "' for node " + self.name)
        else:
            print("[ERROR] Image path '" + image_path + "' does not exist")

    def add_transition(self, transition):
        self.transitions.append(transition)

    """
        Removes the transition to a node
    """
    def remove_transition(self, _node):
        for i, t in enumerate(self.transitions):
            if t.destination == _node:
                # Remove only the first occurrence
                print("[INFO] Removing transition from '" + self.name + "' to '" + _node.name + "'.")
                del self.transitions[i]
                break
        
    """
        Updates the name of the node
    """
    def update_name(self, new_name):
        print("[INFO] Changing node name from '" + self.name + "' to '" + new_name + "'.")
        self.name = new_name
    """
        Returns the image of the node
    """
    def get_transitions(self):
        return self.transitions

    def is_transition_in_node_image(self, image):
        print("[INFO] Graph nodes: ", self.nodes)
        for transition in self.transitions:
            if transition.destination.image is image:
                #print("[INFO] Node '" + node.name + "' is in the graph.")
                return True
        #print("[ERROR] Node '" + name + "' is not in the graph.")
        return False

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
    def __init__(self, destination):
        self.destination = destination
        self.action = None
        self.image = None
        self.text = None
        self.drag_image = None
        self.drop_image = None
   
    """
        Update the action type of this transition.
    """
    def update_action(self, action):
        self.action = action

    """
        Update the image for this transition.
    """
    def update_image(self, image_path):
        self.image = image_path

    """
        Update the text for CLICK_AND_TYPE transitions.
    """
    def update_text(self, text):
        self.text = text
    
    """
        Update the destination node
    """
    def update_destination(self, node):
        self.destination = node

    """
    Update drag and drop images for this transition.
    """
    def update_drag_and_drop(self, drag_image, drop_image):
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
        self.nodes = set()
        self.startNode = None

    """
        Adds a node to the graph
        Returns new node
    """
    def add_node(self, name):
        # Search for existing node with the same name
        for node in self.nodes:
            if node.name == name:
                print("[INFO] Node with name '" + name + "' already exists.")
                return node  
        n = Node(name)
        self.nodes.add(n)
        return n
    
    """
        Adds a node to the graph with an image.
        Returns the new node or None if the node already exists.
    """
    def add_node_with_image(self, name, image_path):
        print("[INFO] Adding node with image: " + image_path)
        for node in self.nodes:
            if node.name == name:
                print("[INFO] Node with name '" + name + "' already exists.")
                return node  
        n = Node(name)
        n.set_image(image_path)
        self.nodes.add(n)
        return n        
    
    """
        Removes the node from the graph and removes all transitions pointing to it
        Returns False if the node was not found or cannot be removed, True otherwise
    """
    def remove_node(self, node):
        if node not in self.nodes:
            print("[ERROR] Node " + node.name + " is not in graph.")
            return False

        self.nodes.remove(node)

        for other_node in self.nodes:
            other_node.transitions = [t for t in other_node.transitions if t.destination is not node]

        print("[INFO] Node '" + node.name + "' has been removed.")
        return True

    """
        Adds a transition to the graph
        Returns None if the origin or destination node is not in the graph, transition otherwise
    """
    def add_transition(self, origin, destination):
        if origin not in self.nodes or destination not in self.nodes:
            if origin not in self.nodes:
                print("[ERROR] Origin node '" + origin + "' is not in the graph.")
            if destination not in self.nodes:
                print("[ERROR] Destination node '" + destination + "' is not in the graph.")
            return None

        t = Transition(destination)
        origin.add_transition(t)
        return t

    """
        Returns the node with the given name.
    """
    def get_node(self, name):
        for node in self.nodes:
            if node.name == name:
                return node
        print("[ERROR] Node not found: " + str(name))
        return None

    """
        Returns the node with the given image.
    """
    def get_node_image(self, image):
        if not self.nodes:
            print("[ERROR] Graph has no nodes.")
            return None
        if image is None:
            print("[ERROR] Image argument is None.")
            return None
        for node in self.nodes:
            if node.image == image:
                return node
        print("[ERROR] Node not found: " + str(image))
        return None

    """
        Sets the start node of the graph.
    """
    def set_start_node(self, node):
        if node is None:
            print("[ERROR] The start node cannot be None.")
            return False

        if node not in self.nodes:
            print("[ERROR] The node '" + node.name + "' is not part of the graph.")
            return False

        self.startNode = node
        print("[INFO] Start node set to '" + node.name + "'.")
        return True

    """
        Updates the name of a node and ensures all transitions pointing to it remain valid.
    """
    def update_node_name(self, node, new_name):
        if node not in self.nodes:
            print("[ERROR] Node '" + node.name + "' is not in the graph.")
            return False
        node.update_name(new_name)
        print("[INFO] Node name updated to '" + new_name + "'.")
        return True

    """
        Clears the graph by removing all nodes and transitions.
    """
    def clear(self):
        self.nodes.clear()
        self.startNode = None
        print("[INFO] Graph cleared.")
    
    """
        Check if a node is in the graph.
    """
    def is_node_in_graph(self, name):
        print("[INFO] Graph nodes: ", self.nodes)
        for node in self.nodes:
            if node.name == name:
                #print("[INFO] Node '" + node.name + "' is in the graph.")
                return True
        #print("[ERROR] Node '" + name + "' is not in the graph.")
        return False

    def is_node_in_graph_image(self, image):
        print("[INFO] Graph nodes: ", self.nodes)
        for node in self.nodes:
            if node.image is image:
                #print("[INFO] Node '" + node.name + "' is in the graph.")
                return True
        #print("[ERROR] Node '" + name + "' is not in the graph.")
        return False