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
        self._dfs_state(state_folders[0], self.full_images_dir, [])
        print("[LOOP] DFS graph loop finished.")
        self._stop_executable()
        self._stop_loop.set()

    def _dfs_state(self, state_path, base_path, clicks_path):
        if state_path in self.visited_states:
            self._stop_executable()
            self._ensure_executable_running()
            print("[DFS] State already visited: " + str(state_path))
            clicks_path.pop()
            self.navigate_to_state(clicks_path)
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
        action = ActionType.CLICK
        buttons_click_path = os.path.join(state_path, "buttons", action.lower())
        # buttons_double_click_path = os.path.join(state_path, "buttons", "double_click")
        # buttons_click_and_type_path = os.path.join(state_path, "buttons", "click_and_type")
        # buttons_drag_and_drop_path = os.path.join(state_path, "buttons", "drag_and_drop")

        print("[DFS] Click buttons path: " + str(buttons_click_path))
        if not os.path.isdir(buttons_click_path):
            print("[DFS] No click buttons folder in " + str(buttons_click_path))
            self._stop_executable()
            self._ensure_executable_running()
            clicks_path.pop()
            self.navigate_to_state(clicks_path)
            return

        # For each transition button
        buttons = [f for f in os.listdir(buttons_click_path) if os.path.isfile(os.path.join(buttons_click_path, f))]
        print("[DFS] Buttons found: " + str(buttons))
        for idx, btn in enumerate(buttons):
            btn_path = os.path.join(buttons_click_path, btn)
            print("[DFS] Simulating " + action + " on: " + str(btn_path))
            result = self.sikuli.click_image(btn_path, timeout=0.01)
            if not result:
                print("[DFS] Could not " + action + " on: " + str(btn_path))
                continue
            self.add_click_to_path(clicks_path, btn_path)  # save the clicks

            dest_state_path = None
            initial_similarity = 0.99
            min_similarity = 0.85
            similarity_step = 0.01
            similarity = initial_similarity

            while similarity >= min_similarity and dest_state_path is None:
                print("[DFS] Searching for destination state with similarity: " + str(similarity))
                for candidate_state in os.listdir(base_path):
                    candidate_path = os.path.join(base_path, candidate_state)
                    if not os.path.isdir(candidate_path):
                        continue
                    candidate_images = [f for f in os.listdir(candidate_path)
                                        if os.path.isfile(os.path.join(candidate_path, f)) and os.path.splitext(f)[1].lower() in self.valid_extensions]
                    if not candidate_images:
                        continue
                    candidate_image_path = os.path.join(candidate_path, candidate_images[0])
                    print("[DFS] Checking if the screen matches: " + str(candidate_image_path))
                    if self.sikuli.search_image_once(candidate_image_path, timeout=0.1, similarity=similarity):
                        dest_state_path = candidate_path
                        print("[DFS] The screen matches with state: " + str(dest_state_path))
                        break
                similarity -= similarity_step

            if dest_state_path is not None:
                print("[DFS] Creating transition from node: " + str(node_name) + " with image: " + str(btn_path))
                dst_node_name = os.path.splitext(os.path.basename(dest_state_path))[0]
                print("[DFS] Destination node name: " + str(dst_node_name))
                dst_node = self.graph.add_node_with_image(dst_node_name, candidate_image_path)
                transition = self.graph.add_transition(node, dst_node)
                transition.update_action(action)
                transition.update_image(btn_path)
                print("[DFS] Transition added. Recursively calling _dfs_state with destination: " + str(dest_state_path))
                self._dfs_state(dest_state_path, base_path, clicks_path)
            else:
                print("[DFS] Destination state not found for button " + str(btn))

                phantom_node_name = "phantom_state" + str(self.phantom_state_counter)

                # Build imgs directory path (search from base_path or state_path)
                if self.images_dir in base_path:
                    imgs_index = base_path.lower().find(self.images_dir)
                    imgs_root = base_path[:imgs_index + len(self.images_dir)]
                elif self.images_dir in state_path:
                    imgs_index = state_path.lower().find(self.images_dir)
                    imgs_root = state_path[:imgs_index + len(self.images_dir)]
                else:
                    imgs_root = base_path  # Fallback

                phantom_dir = os.path.join(imgs_root, phantom_node_name)
                if not os.path.exists(phantom_dir):
                    os.makedirs(phantom_dir)
                phantom_image_path = phantom_dir

                # Screenshot and save
                self.sikuli.capture_error(phantom_node_name, phantom_image_path)
                
                print("[DFS] Screenshot saved at: " + phantom_image_path)

                # Add the phantom node to the graph
                self.graph.add_node_with_image(phantom_node_name, phantom_image_path)
                print("[DFS] Phantom node created: " + phantom_node_name + " with image: " + phantom_image_path)

                # Increment the counter
                self.phantom_state_counter += 1
                # ---------- END PHANTOM BLOCK -----------

                self._stop_executable()
                self._ensure_executable_running()
                clicks_path.pop()
                self.navigate_to_state(clicks_path)

    def add_click_to_path(self, clicks_path, btn_path):
        clicks_path.append(btn_path)
        print("[PATH] Click added to path: " + str(btn_path))

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
