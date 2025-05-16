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
        self.debug_name = "Debug"
        self.full_debug_name = os.path.join(self.full_images_dir, self.debug_name)
        
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
        if not os.path.exists(self.full_debug_name):
                os.makedirs(self.full_debug_name)

        self._ensure_executable_running()
        self.graph.set_start_node(self._dfs_state())
        print("[LOOP] DFS graph loop finished.")
        self._stop_executable()
        self._stop_loop.set()

    def _dfs_state(self):
        initial_similarity = 0.99
        min_similarity = 0.85
        similarity_step = 0.01
        timeout = 2

        current_state = None        # Node object
        current_state_path = None   # Path to the image of the current state
        current_state_name = None   # Name of the current state

        # Check if current state exists
        similarity = initial_similarity
        while similarity >= min_similarity and current_state is None:
            print("[DFS] Searching for current state with similarity: " + str(similarity))
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
                if self.sikuli.search_image_once(candidate_state_path, similarity=similarity, timeout=timeout):
                    # Create node in graph
                    current_state_path = candidate_path
                    current_state_name = candidate_state
                    current_state = self.graph.add_node_with_image(current_state_name, candidate_state_path)
                    print("[DFS] The screen matches with state: " + str(current_state_name))
                    break
                    
            similarity -= similarity_step

        if current_state is not None:
            found = False
            self.sikuli.capture_error(current_state_name, self.full_debug_name)
            if current_state not in self.visited_states:
                print("[DFS] Visiting state: " + str(current_state))
                self.visited_states.add(current_state)

                # If there are no action types, return the current state (first found state)
                if not any(isinstance(value, str) and name.isupper() for name, value in vars(ActionType).items()):
                    print("[DFS] No action types found.")
                    return current_state

                # Check if buttons folder exists
                buttons_path = os.path.join(current_state_path, self.buttons_dir)
                if not os.path.isdir(buttons_path):
                    print("[DFS] No buttons folder found in " + str(current_state_path))
                    return current_state

                buttons_input_path = None
                for name, action_type in vars(ActionType).items():
                    if isinstance(action_type, str) and name.isupper():
                        print("[DFS] Checking action type: " + str(action_type))
                        action_type_path = action_type.lower()
                        aux_path = os.path.join(buttons_path, action_type_path)
                        if not os.path.isdir(aux_path):
                            print("[DFS] No " + action_type_path + " buttons folder in " + str(buttons_input_path))
                            continue
                        
                        buttons_input_path = aux_path
                        print("[DFS] " + action_type_path + " buttons folder found: " + str(buttons_input_path))
                        
                        # Check if there are button images in the folder
                        buttons_input_path_names = [f for f in os.listdir(buttons_input_path) if os.path.isfile(os.path.join(buttons_input_path, f))]
                        if not buttons_input_path_names:
                            print("[DFS] No buttons found in " + str(buttons_input_path))
                            continue
                        
                        print("[DFS] Buttons images found: " + str(buttons_input_path))
                        for idx, btn in enumerate(buttons_input_path_names):
                            btn_path = os.path.join(buttons_input_path, btn)
                            print("[DFS] Simulating " + action_type + " with button image: " + str(btn_path))
                            if self.lastInput is not None and len(self.inputs[self.lastInput]) >= 1:
                                print ("Desde ruta: "  + str(self.inputs[self.lastInput]))
                            print(current_state_name + " Nombreeeeeeeeeeeeeeeeeeeeeeeeeee")
                            self.lastInput = action_type
                            self.sikuli.capture_error(btn, self.full_debug_name)
                            result = self.do_action(action_type, btn_path)
                            if not result:
                                print("[DFS] Could not " + self.lastInput + " on: " + str(btn_path))
                                continue
                            
                            found = True                            
                            time.sleep(self.delay)
                            self.add_inputs_to_path(btn_path)
                            dst_node = self._dfs_state()
                            print("[DFS] Creating transition from node: " + str(current_state_name) + " with image: " + str(btn_path))
                            transition = self.graph.add_transition(current_state, dst_node)
                            transition.update_action(action_type)
                            transition.update_image(btn_path)
                        
                #self._restart_executable_and_continue()
            
            self._restart_executable_and_continue()

        else:
            print("[DFS] Current state not found")
            phantom_node_name = self.default_state_name + str(self.phantom_state_counter)
            phantom_dir = os.path.join(self.full_images_dir, phantom_node_name)
            if not os.path.exists(phantom_dir):
                os.makedirs(phantom_dir)

            # Screenshot and save
            file_path = self.sikuli.capture_error(phantom_node_name, phantom_dir)
            print("[DFS] Screenshot saved at: " + phantom_dir)

            # Add the phantom node to the graph
            current_state = self.graph.add_node_with_image(phantom_node_name, file_path)
            print("[DFS] Phantom node created: " + phantom_node_name + " with image: " + file_path)

            # Increment the counter
            self.phantom_state_counter += 1
        
        return current_state

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

        return result

    def _restart_executable_and_continue(self):
        self._stop_executable()
        
        if (self.lastInput is None or self.inputs[self.lastInput] is None or len(self.inputs[self.lastInput]) == 0):
            print("[INFO] AAAAAAA.")
            return
        print("Begin " + str(self.inputs[self.lastInput]))
        self.inputs[self.lastInput].pop()
        print("Began/Begun " + str(self.inputs[self.lastInput]))
       
        if (self.inputs[self.lastInput] is None or len(self.inputs[self.lastInput]) == 0):
            print("[INFO] BBBBBBB.")
            return
        self._ensure_executable_running()
        self.navigate_to_state(self.inputs[self.lastInput])
        

    def add_inputs_to_path(self, btn_path):
        self.inputs[self.lastInput].append(btn_path)
        print("[PATH] " + self.lastInput + " added to path: " + str(btn_path))

    def navigate_to_state(self, clicks_path, timeout=2):
        print("[NAVIGATE] Replaying the click sequence: " + str(clicks_path))
        for idx, btn_path in enumerate(clicks_path):
            print("[NAVIGATE] (" + str(idx+1) + "/" + str(len(clicks_path)) + ") Clicking on: " + str(btn_path))
            self.sikuli.click_image(btn_path, timeout=timeout, retries=8, similarity_reduction=0.05)
            time.sleep(self.delay)
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
