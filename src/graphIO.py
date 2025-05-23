# -*- coding: utf-8 -*-
import os
from actionTypes import ActionType
from graphsDef import Graph

def singleton(cls):
    """
    Decorator to turn a class into a Singleton
    Ensures only one instance of the class is ever created
    """
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class GraphIO:
    """
    Singleton class to handle reading and writing of graph data
    """

    def __init__(self):
        """
        Initializes the GraphIO instance
        """
        self.graph = None 

    def load_graph(self, graph_file, img_dir):
        """
        Loads the graph definition from the file and creates a Graph object

        Args:
            graph_file (str): Path to the graph definition file
            img_dir (str): Directory containing the images

        Returns:
            Graph: A Graph object populated with nodes and transitions
        """
        self.graph = None
        print("[INFO] Loading graph from " + graph_file)
        try:
            if img_dir is None or not os.path.isdir(img_dir):
                print("[ERROR] Image directory not found: " + str(img_dir))
                return None
            if graph_file is None or not os.path.isfile(graph_file):
                print("[ERROR] Graph file not found: " + str(graph_file))
                return None
        
            self.graph = Graph()  # Create a new Graph instance
            with open(graph_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if parts[0] == 'v' and len(parts) == 3:
                        name = parts[1]
                        raw_path = parts[2]
                        node = self.graph.add_node(name)
                        if node:
                            image_path = os.path.join(img_dir, raw_path)
                            if not os.path.isfile(image_path):
                                print("[ERROR] Image file not found: " + image_path)
                                continue
                            node.set_image(os.path.join(img_dir, raw_path))

                    elif parts[0] == 'e':
                        action_str = parts[1]
                        src_name = parts[2] if len(parts) > 2 else None
                        tgt_name = parts[3] if len(parts) > 3 else None

                        src_node = next((n for n in self.graph.nodes if n.name == src_name), None)
                        tgt_node = next((n for n in self.graph.nodes if n.name == tgt_name), None)
                        if not src_node or not tgt_node:
                            print("[ERROR] Source or target node not found for edge: " + line)
                            continue

                        try:
                            action = ActionType.from_string(action_str)
                        except KeyError:
                            print("[ERROR] Unknown action " + action_str + " in graph file")
                            continue

                        if action in (ActionType.CLICK, ActionType.DOUBLE_CLICK):
                            if len(parts) != 5:
                                print("[ERROR] Invalid number of args for " + action_str + ", expected 5 but got " + str(len(parts)))
                                continue
                            img = parts[4]
                            if action == ActionType.CLICK:
                                self.handle_click_action(src_node, tgt_node, os.path.join(img_dir, img))
                            else:
                                self.handle_double_click_action(src_node, tgt_node, os.path.join(img_dir, img))

                        elif action == ActionType.CLICK_AND_TYPE:
                            if len(parts) != 6:
                                print("[ERROR] Invalid number of args for CLICK_AND_TYPE, expected 6 but got " + str(len(parts)))
                                continue
                            img = parts[4]
                            text = parts[5]
                            self.handle_click_and_type_action(src_node, tgt_node, text, os.path.join(img_dir, img))

                        elif action == ActionType.DRAG_AND_DROP:
                            if len(parts) != 6:
                                print("[ERROR] Invalid number of args for DRAG_AND_DROP, expected 6 but got " + str(len(parts)))
                                continue
                            drag_img = parts[4]
                            drop_img = parts[5]
                            self.handle_drag_and_drop_action(src_node, tgt_node, os.path.join(img_dir, drag_img), os.path.join(img_dir, drop_img))

                        else:
                            print("[ERROR] Unsupported action type: " + action_str)

        except FileNotFoundError:
            print("[ERROR] Graph file not found: " + graph_file)
        except Exception as e:
            print("[ERROR] An error occurred while loading the graph: " + str(e))

        if self.graph is not None and self.graph.nodes:
            first_node = next(iter(self.graph.nodes))
            self.graph.set_start_node(first_node)

        return self.graph

    def handle_click_action(self, src_node, tgt_node, image_path):
        transition = self.graph.add_transition(src_node, tgt_node)
        if not transition:
            print("[WARN] add_transition returned None. The transition was not created")
            return
        transition.update_action(ActionType.CLICK)
        transition.update_image(image_path)
        print("[INFO] CLICK action handled")

    def handle_double_click_action(self, src_node, tgt_node, image_path):
        transition = self.graph.add_transition(src_node, tgt_node)
        if not transition:
            print("[WARN] add_transition returned None. The transition was not created")
            return
        transition.update_action(ActionType.DOUBLE_CLICK)
        transition.update_image(image_path)
        print("[INFO] DOUBLE_CLICK action handled")

    def handle_click_and_type_action(self, src_node, tgt_node, text_to_type, image_path):
        transition = self.graph.add_transition(src_node, tgt_node)
        if not transition:
            print("[WARN] add_transition returned None. The transition was not created")
            return
        transition.update_action(ActionType.CLICK_AND_TYPE)
        transition.update_text(text_to_type)
        transition.update_image(image_path)
        print("[INFO] CLICK_AND_TYPE action handled")

    def handle_drag_and_drop_action(self, src_node, tgt_node, drag_image, drop_image):
        transition = self.graph.add_transition(src_node, tgt_node)
        if not transition:
            print("[WARN] add_transition returned None. The transition was not created")
            return
        transition.update_action(ActionType.DRAG_AND_DROP)
        transition.update_drag_and_drop(drag_image, drop_image)
        print("[INFO] DRAG_AND_DROP action handled")

    def write_graph(self, images_dir, graph_file, graph):
        print("[INFO] Writing graph to " + graph_file)
        try:
            with open(graph_file, "w") as f:
                edge_lines = []
                # Iterate nodes and write only the vertices, but accumulate edges
                for node in graph.nodes:
                    node_name = node.name.replace(" ", "_")
                    if node.image:
                        image_name = os.path.relpath(node.image, images_dir).replace("/", "\\")
                    else:
                        image_name = "unknown_image"
                        print("[WARNING] Node " + node_name + " has no valid image path.")
                    f.write("v " + node_name + " " + image_name + "\n")

                    for trans in node.transitions:
                        act = trans.action if trans.action else "None"
                        dst = trans.destination.name.replace(" ", "_")

                        if act in (ActionType.CLICK, ActionType.DOUBLE_CLICK):
                            image_name = trans.image.split(images_dir, 1)[1].lstrip("/\\")
                            edge_lines.append("e " + act + " " + node_name + " " + dst + " " + image_name + "\n")

                        elif act == ActionType.CLICK_AND_TYPE:
                            image_name = trans.image.split(images_dir, 1)[1].lstrip("/\\")
                            edge_lines.append("e " + act + " " + node_name + " " + dst + " " + image_name + " " + trans.text + "\n")

                        elif act == ActionType.DRAG_AND_DROP:
                            drag_image_name = os.path.relpath(trans.drag_image, images_dir).replace("/", "\\")
                            drop_image_name = os.path.relpath(trans.drop_image, images_dir).replace("/", "\\")
                            edge_lines.append("e " + act + " " + node_name + " " + dst + " " + drag_image_name + " " + drop_image_name + "\n")

                        else:
                            edge_lines.append("e " + act + " " + node_name + " " + dst + "\n")
                # Write all edges at the end
                f.writelines(edge_lines)
        except Exception as e:
            print("[ERROR] Exception while writing the graph: " + str(e))
        else:
            print("[INFO] Graph successfully written to " + graph_file)
