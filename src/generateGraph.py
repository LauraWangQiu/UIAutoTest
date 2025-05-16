# -*- coding: utf-8 -*-
# generateGraph.py ARREGLADO - DFS Recursivo

import argparse
import os
import subprocess
import threading
import time
from sikulixWrapper import SikulixWrapper
from graphsDef import Graph, Transition
from actionTypes import ActionType
import GraphIO as _graph_io_module
GraphIO = _graph_io_module.GraphIO

class GenerateGraph:
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp'}

    def __init__(self, images_dir=None, practical_graph_file=None, selected_executable=None, delay=5):
        self.images_dir = images_dir
        self.practical_graph_file = practical_graph_file
        self.selected_executable = selected_executable
        self.visited_states = set()
        self.inputs = {
            value: [] for name, value in vars(ActionType).items()
            if not name.startswith("__") and not callable(value)
        }
        self.lastInput = None
        self.full_images_dir = os.path.join(os.getcwd(), self.images_dir)
        self.graph = Graph()
        self.delay = delay
        self.process = None
        self.sikuli = SikulixWrapper()        
        self.graph_io = GraphIO()  
        self._stop_loop = threading.Event()
        self._executable_thread = None
        self._loop_thread = None
        self.phantom_state_counter = 0
        self.buttons_dir = "buttons"
        self.default_state_name = "State_"
        
    def generate_graph(self):
        print("Generating graph for " + str(self.selected_executable))
        self._executable_thread = threading.Thread()
        self._executable_thread.start()

        self._loop_thread = threading.Thread(target=self._loop)
        self._loop_thread.start()

        self._loop_thread.join()
        self._executable_thread.join()

        self._stop_executable()
        for node in self.graph.nodes:
            print("[INFO] Node: " + str(node.name))
            for transition in node.transitions:
                print("[INFO] Transition: " + str(transition.action) + " -> " + str(transition.destination.name))
                print("[INFO] Image: " + str(transition.image))

        self.graph_io.write_graph(self.images_dir, self.practical_graph_file, self.graph)
        print("[INFO] graph has been saved to " + str(self.practical_graph_file))

    def _start_executable(self):
        try:
            print("[INFO] Starting executable: " + str(self.selected_executable))
            self.process = subprocess.Popen([self.selected_executable])
            self.process.wait()
        except FileNotFoundError:
            print("[INFO] Executable not found: " + str(self.selected_executable))
            self.process = None

    def _stop_executable(self):
        try:
            if self.process is not None:
                print("[INFO] Stopping executable: " + str(self.selected_executable))
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except Exception:
                    print("[INFO] Forcing the executable to stop...")
                    self.process.kill()
                    self.process.wait()
                print("[INFO] Executable terminated.")
                self.process = None
            if self._executable_thread is not None and self._executable_thread.is_alive():
                print("[INFO] Waiting the executable thread to end...")
                self._executable_thread.join(timeout=5)
                print("[INFO] Executable thread ended.")
        except Exception as e:
            print("[ERROR] Error on closing executable: "+str(e))
            self.process = None

    # --- DFS recursivo ---
    def _loop(self):
        print("[LOOP] Starting DFS graph generation loop...")
        # Check if the images directory exists
        state_folders = [os.path.join(self.full_images_dir, d) for d in os.listdir(self.full_images_dir) if os.path.isdir(os.path.join(self.full_images_dir, d))]
        if not state_folders:
            print("[LOOP] No states found.")
            return
        self._ensure_executable_running()
        # Selects the first state folder
        self._dfs_state(state_folders[0])
        print("[LOOP] DFS graph loop finished.")
        self._stop_executable()
        self._stop_loop.set()

    def _dfs_state(self, state_path):
        if state_path in self.visited_states:
            print("[DFS] State already visited: " + str(state_path))
            self._restart_executable_and_continue()
            return
        
        print("[DFS] Visiting state: " + str(state_path))
        self.visited_states.add(state_path)

        # Search for the main image of the state (only one, the first found)
        images = [f for f in os.listdir(state_path)
                if os.path.isfile(os.path.join(state_path, f)) and os.path.splitext(f)[1].lower() in self.valid_extensions]
        print("[DFS] Images found in the state: " + str(images))

        if not images:
            print("[DFS] No main image in " + str(state_path))
            return
        
        # There must be at least one image and the first one is the main image
        image_menu = os.path.join(state_path, images[0])
        node_name = os.path.splitext(images[0])[0]
        node = self.graph.get_node(node_name)
        print("[DFS] Main image selected: " + str(image_menu))
        print("[DFS] Node name: " + str(node_name))
        print("[DFS] Node: " + str(node))

        if node is None:
            print("[DFS] Node does not exist, it will be created with image: " + str(image_menu))
            self.graph.add_node_with_image(node_name, image_menu)
            node = self.graph.get_node(node_name)
            print("[DFS] Node created: " + str(node_name) + " with image: " + str(image_menu))
    
        # Buttons folder (transitions)
        buttons_path = os.path.join(state_path, self.buttons_dir)
        buttons_input_path = None
        for name, action_type in vars(ActionType).items():
            if isinstance(action_type, str) and name.isupper():
                print("[DFS] Checking action type: " + str(action_type))
                action_type_path = action_type.lower()
                
                buttons_input_path = os.path.join(buttons_path, action_type_path)
                print("[DFS] " + action_type_path +" buttons path: " + str(buttons_input_path))

                if not os.path.isdir(buttons_input_path):
                    print("[DFS] No " + action_type_path + " buttons folder in " + str(buttons_input_path))
                    continue
                
                print("[DFS] " + action_type_path + " buttons folder found: " + str(buttons_input_path))
                break
                    
        if buttons_input_path is None or not os.path.isdir(buttons_input_path):
            print("[DFS] No buttons folder found in " + str(state_path))
            self._restart_executable_and_continue()
            return
        
        # For each transition button
        buttons = [f for f in os.listdir(buttons_input_path) if os.path.isfile(os.path.join(buttons_input_path, f))]
        if not buttons:
            print("[DFS] No buttons found in " + str(buttons_input_path))
            return
        
        print("[DFS] Buttons images found: " + str(buttons))
        for idx, btn in enumerate(buttons):
            btn_path = os.path.join(buttons_input_path, btn)
            print("[DFS] Simulating " + action_type + " on: " + str(btn_path))
            result = self.do_action(action_type, btn_path)
            if not result:
                print("[DFS] Could not " + self.lastInput + " on: " + str(btn_path))
                continue

            self.add_inputs_to_path(btn_path)

            dest_state_path = None
            initial_similarity = 0.99
            min_similarity = 0.70
            similarity_step = 0.01
            similarity = initial_similarity

            # Checks the screen for the next state
            while similarity >= min_similarity and dest_state_path is None:
                print("[DFS] Searching for destination state with similarity: " + str(similarity))
                for candidate_state in os.listdir(self.full_images_dir):
                    candidate_path = os.path.join(self.full_images_dir, candidate_state)
                    # It must be a directory
                    if not os.path.isdir(candidate_path):
                        continue

                    candidate_states = [f for f in os.listdir(candidate_path)
                                        if os.path.isfile(os.path.join(candidate_path, f)) and os.path.splitext(f)[1].lower() in self.valid_extensions]
                    if not candidate_states:
                        continue
                    
                    # There must be at least one image and the first one selected is the main state image
                    candidate_state_path = os.path.join(candidate_path, candidate_states[0])
                    print("[DFS] Checking if the screen matches: " + str(candidate_state_path))
                    if self.sikuli.search_image_once(candidate_state_path, timeout=0.1, similarity=similarity):
                        dest_state_path = candidate_path
                        print("[DFS] The screen matches with state: " + str(dest_state_path))
                        break
                        
                similarity -= similarity_step

            if dest_state_path is not None:
                print("[DFS] Creating transition from node: " + str(node_name) + " with image: " + str(btn_path))
                dst_node_name = os.path.splitext(os.path.basename(dest_state_path))[0]
                print("[DFS] Destination node name: " + str(dst_node_name))
                dst_node = self.graph.add_node_with_image(dst_node_name, candidate_state_path)
                transition = self.graph.add_transition(node, dst_node)
                transition.update_action(self.lastInput)
                transition.update_image(btn_path)
                print("[DFS] Transition added. Recursively calling _dfs_state with destination: " + str(dest_state_path))
                self._dfs_state(dest_state_path)
            else:
                print("[DFS] Destination state not found for button " + str(btn))
                phantom_node_name = self.default_state_name + str(self.phantom_state_counter)
                phantom_dir = os.path.join(self.full_images_dir, phantom_node_name)
                if not os.path.exists(phantom_dir):
                    os.makedirs(phantom_dir)

                # Screenshot and save
                file_path = self.sikuli.capture_error(phantom_node_name, phantom_dir)
                print("[DFS] Screenshot saved at: " + phantom_dir)

                # Add the phantom node to the graph
                self.graph.add_node_with_image(phantom_node_name, file_path)
                print("[DFS] Phantom node created: " + phantom_node_name + " with image: " + file_path)

                # Increment the counter
                self.phantom_state_counter += 1
                # ---------- END PHANTOM BLOCK -----------
                self._restart_executable_and_continue()

    def do_action(self, action_type, btn_path, text=None, btn2_path=None, similarity=1.0, timeout=0.01, retries=6, similarity_reduction=0.1, clear_before=False):
        if action_type is None or not ActionType.is_valid_action(action_type):
            print("[ERROR] No action type selected.")
            return False

        result = False
        if action_type == ActionType.CLICK:
            print("[INFO] Clicking on: " + str(btn_path))
            result = self.sikuli.click_image(btn_path, similarity=similarity, timeout=timeout, retries=retries, similarity_reduction=similarity_reduction)
        elif action_type == ActionType.DOUBLE_CLICK:
            print("[INFO] Double clicking on: " + str(btn_path))
            return False
            # self.sikuli.double_click_image(btn_path, similarity=similarity, timeout=timeout, retries=retries, similarity_reduction=similarity_reduction)
        elif action_type == ActionType.CLICK_AND_TYPE:
            if text is None:
                print("[ERROR] No text provided for click and type.")
                return False
            print("[INFO] Clicking and typing on: " + str(btn_path))
            result = self.sikuli.write_text(btn_path, text=text, similarity=similarity, timeout=timeout, retries=retries, similarity_reduction=similarity_reduction, clear_before=clear_before)
        elif action_type == ActionType.DRAG_AND_DROP:
            if btn2_path is None:
                print("[ERROR] No second button path provided for drag and drop.")
                return False
            print("[INFO] Dragging and dropping from: " + str(btn_path) + " to: " + str(btn2_path))
            result = self.sikuli.drag_and_drop(btn_path, btn2_path, similarity=similarity, timeout=timeout, retries=retries, similarity_reduction=similarity_reduction)

        self.lastInput = action_type
        return result

    def _restart_executable_and_continue(self):
        self._stop_executable()
        self._ensure_executable_running()
        self.inputs[self.lastInput].pop()
        self.navigate_to_state(self.inputs[self.lastInput])

    def add_inputs_to_path(self, btn_path):
        self.inputs[self.lastInput].append(btn_path)
        print("[PATH] " + self.lastInput + " added to path: " + str(btn_path))

    def navigate_to_state(self, clicks_path, timeout=2):
        print("[NAVIGATE] Replaying the click sequence: " + str(clicks_path))
        for idx, btn_path in enumerate(clicks_path):
            print("[NAVIGATE] (" + str(idx+1) + "/" + str(len(clicks_path)) + ") Clicking on: " + str(btn_path))
            self.sikuli.click_image(btn_path, timeout=timeout, retries=8, similarity_reduction=0.05)
        print("[NAVIGATE] Click sequence completed.")

    def _ensure_executable_running(self):
        if self.process is None:
            self._executable_thread = threading.Thread(target=self._start_executable)
            self._executable_thread.start()
            time.sleep(self.delay)

    def input_sikuli(self, buttons_path, node, visited_images):
        print("[INPUT_SIKULI] Iniciando input_sikuli...")
        path = self.check_transition(os.path.join(buttons_path,"click"), node) 
        print("[INPUT_SIKULI] Path: " + str(path))
        if path is not None:
            self.click(path, node, visited_images)
        else:
            return None

    def check_transition(self, buttons_path, node):
        if not os.path.isdir(buttons_path):
            return None
        buttons_images = [f for f in os.listdir(buttons_path) if os.path.isfile(os.path.join(buttons_path, f))]
        transition_images = {t.image for t in node.transitions}
        for img_f in buttons_images:
            if os.path.join(buttons_path, img_f) not in transition_images or len(transition_images) == 0:
                print("[INPUT_SIKULI] Image not found in transitions: " + img_f)
                return os.path.join(buttons_path, img_f)
            else:
                print("[INPUT_SIKULI] Image found: " + img_f)
        print("[INPUT_SIKULI] All transitions visited.")
        return None

    def click(self, image_path, node, visited_images):
        print("[INPUT_SIKULI] Clicking on image: " + image_path)
        transition = Transition(node)
        print("[INPUT_SIKULI] Transitions: ", node.transitions)
        transition.image = image_path
        node.add_transition(transition)
        self.sikuli.click_image(image_path, timeout=0.001,retries=8,similarity_reduction= 0.05)
        if image_path not in visited_images:
            visited_images.add(image_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a graph using SikuliX and a specified executable.")
    parser.add_argument("--images_dir", required=True, help="Path to the directory containing images.")
    parser.add_argument("--practical_graph_file", required=True, help="Name of the practical graph file to save.")
    parser.add_argument("--selected_executable", required=True, help="Path to the executable to run.")
    parser.add_argument("--delay", type=int, default=5, help="Delay in seconds between actions.")

    args = parser.parse_args()

    print("[INFO] Images directory: " + str(args.images_dir))
    print("[INFO] Practical graph file: " + str(args.practical_graph_file))
    print("[INFO] Selected executable: " + str(args.selected_executable))
    print("[INFO] Delay in seconds: " + str(args.delay))

    generator = GenerateGraph(
        images_dir=args.images_dir, 
        practical_graph_file=args.practical_graph_file, 
        selected_executable=args.selected_executable,
        delay=args.delay
    )
    generator.generate_graph()
