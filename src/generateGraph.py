# -*- coding: utf-8 -*-
import argparse
import os
import shutil
import subprocess
import threading
import time
from sikulixWrapper import SikulixWrapper
from graphsDef import Graph, Transition
from actionTypes import ActionType
from stateResetMethod import StateResetMethod
import graphIO as _graph_io_module
GraphIO = _graph_io_module.GraphIO

class GenerateGraph:
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp'}

    def __init__(self, images_dir=None, practical_graph_file=None, selected_executable=None, delay=5, timeout=2, initial_similarity=0.99, min_similarity=0.85, similarity_step=0.01, state_reset_method=StateResetMethod.RELAUNCH):
        self.graph_io = GraphIO()  
        self.sikuli = SikulixWrapper()

        self.images_dir = images_dir
        self.practical_graph_file = practical_graph_file
        self.selected_executable = selected_executable
        self.delay = delay
        self.initial_similarity = initial_similarity
        self.min_similarity = min_similarity
        self.similarity_step = similarity_step
        self.timeout = timeout
        self.state_reset_method = state_reset_method

        self.graph = None
        self.visited_states = set()
        self.lastInput = None
        self.inputs = {
            value: [] for name, value in vars(ActionType).items()
            if not name.startswith("__") and not callable(value)
        }

        self.stop_loop = threading.Event()
        self.process = None
        self.executable_thread = None
        self.loop_thread = None

        self.buttons_dir = "buttons"
        self.default_state_name = "State_"
        self.debug_name = "DebugImages"
        self.full_debug_name = os.path.join(os.getcwd(), self.debug_name)
        self.full_images_dir = os.path.join(os.getcwd(), self.images_dir)
        
        self.phantom_state_counter = 0
        
    def generate_graph(self):
        print("[INFO] Generating graph for " + str(self.selected_executable))
        self.executable_thread = threading.Thread()
        self.executable_thread.start()

        self.loop_thread = threading.Thread(target=self._loop)
        self.loop_thread.start()

        self.loop_thread.join()
        self.executable_thread.join()

        self._stop_executable()
        if self.graph is None:
            print("[ERROR] No graph generated.")
            return
        
        for node in self.graph.nodes:
            print("[INFO] Node: " + str(node.name))
            for transition in node.transitions:
                print("[INFO] Transition: " + str(transition.action) + " -> " + str(transition.destination.name))
                print("[INFO] Image: " + str(transition.image))

        self.graph_io.write_graph(self.images_dir, self.practical_graph_file, self.graph)

    def _start_executable(self):
        try:
            print("[INFO] Starting executable: " + self.selected_executable)
            self.process = subprocess.Popen([self.selected_executable])
            print("[DEBUG] Executable process started: " + str(self.process))
            self.process.wait()
            print("[DEBUG] Executable process finished")
        except OSError:
            print("[INFO] Executable not found: " + str(self.selected_executable))
            self.process = None
        except Exception as e:
            print("[ERROR] Exception in _start_executable: " + str(e))

    def _stop_executable(self):
        try:
            if self.process is not None:
                print("[INFO] Stopping executable: " + str(self.selected_executable))
                self.process.terminate()
                try:
                    self.process.wait(timeout=self.delay)
                except Exception:
                    print("[INFO] Forcing the executable to stop...")
                    self.process.kill()
                    self.process.wait()
                print("[INFO] Executable terminated.")
                self.process = None
            if self.executable_thread is not None and self.executable_thread.is_alive():
                print("[INFO] Waiting the executable thread to end...")
                self.executable_thread.join(timeout=5)
                print("[INFO] Executable thread ended.")
        except Exception as e:
            print("[ERROR] Error on closing executable: "+str(e))
            self.process = None

    def _loop(self):
        # Check if the images directory exists and is a directory
        if not os.path.isdir(self.full_images_dir):
            print("[LOOP] Images directory does not exist or is not a directory: " + self.full_images_dir)
            return
        state_folders = [os.path.join(self.full_images_dir, d) for d in os.listdir(self.full_images_dir) if os.path.isdir(os.path.join(self.full_images_dir, d))]
        if not state_folders:
            print("[LOOP] No states found.")
            return
        if not os.path.exists(self.full_debug_name):
            os.makedirs(self.full_debug_name)
        print("[LOOP] Starting DFS graph generation loop...")
        self._ensure_executable_running()
        self.graph = Graph()
        self.graph.set_start_node(self._dfs_state())
        print("[LOOP] DFS graph loop finished.")
        self._stop_executable()
        self.stop_loop.set()

    def _dfs_state(self):
        current_state = None        # Node object
        current_state_path = None   # Path to the image of the current state
        current_state_name = None   # Name of the current state

        # Check if current state exists
        similarity = self.initial_similarity
        while similarity >= self.min_similarity and current_state is None:
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
                if self.sikuli.search_image_once(candidate_state_path, similarity=similarity, timeout=self.timeout):
                    # Create node in graph
                    current_state_path = candidate_path
                    current_state_name = candidate_state
                    current_state = self.graph.add_node_with_image(current_state_name, candidate_state_path)
                    print("[DFS] The screen matches with state: " + str(current_state_name))
                    break
                    
            similarity -= self.similarity_step

        if current_state is not None:
            self.sikuli.capture_error(current_state_name, self.full_debug_name)
            if current_state not in self.visited_states:
                print("[DFS] Visiting state: " + str(current_state.name))
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
                            
                            if os.path.splitext(btn)[1].lower() not in self.valid_extensions:
                                print("[DFS] Skipping non-image file: " + str(btn_path))
                                continue
                            print("[DFS] Simulating " + action_type + " with button image: " + str(btn_path))
                            self.lastInput = action_type
                            self.sikuli.capture_error(btn, self.full_debug_name)
                            text = None
                            result,text = self.do_action(action_type, btn_path,text)
                            if not result:
                                print("[DFS] Could not " + self.lastInput + " on: " + str(btn_path))
                                continue
                                                  
                            time.sleep(self.delay)
                            self._add_inputs_to_path(btn_path)
                            dst_node = self._dfs_state()
                            print("[DFS] Creating transition from node: " + str(current_state_name) + " with image: " + str(btn_path))
                            transition = self.graph.add_transition(current_state, dst_node)
                            transition.update_action(action_type)
                            transition.update_image(btn_path)
                            if action_type == ActionType.CLICK_AND_TYPE:
                                transition.update_text(text)
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

    def do_action(self, action_type, btn_path, text=str, btn2_path=None, similarity=1.0, timeout=0.01, retries=8, similarity_reduction=0.1, clear_before=False,enter=True):
        if action_type is None or not ActionType.is_valid_action(action_type):
            print("[ERROR] No action type selected.")
            return False

        result = False
        if action_type == ActionType.CLICK:
            print("[INFO] Clicking on: " + str(btn_path))
            result = self.sikuli.click_image(btn_path, similarity = similarity, timeout = timeout, retries = retries, similarity_reduction = similarity_reduction, capture_last_match = True, debug_image_name = os.path.basename(btn_path), debug_image_path = self.debug_name)
        elif action_type == ActionType.DOUBLE_CLICK:
            print("[INFO] Double clicking on: " + str(btn_path))
            return False
            # self.sikuli.double_click_image(btn_path, similarity=similarity, timeout=timeout, retries=retries, similarity_reduction=similarity_reduction, capture_last_match = True)
        elif action_type == ActionType.CLICK_AND_TYPE:
            txt_path = os.path.splitext(btn_path)[0] + ".txt"
            if os.path.isfile(txt_path):
               with open(txt_path, "r") as f:
                  text = f.read().strip()
            else:
                print("[ERROR] No .txt file found for click and type: " + str(txt_path))
                return False
            print("[INFO] Clicking and typing on: " + str(btn_path) + " with text: " + str(text))
            result = self.sikuli.write_text(btn_path, text=text, similarity=similarity, timeout=timeout, retries=retries, similarity_reduction=similarity_reduction, clear_before=clear_before,enter=enter)
        elif action_type == ActionType.DRAG_AND_DROP:
            if btn2_path is None:
                print("[ERROR] No second button path provided for drag and drop.")
                return False
            print("[INFO] Dragging and dropping from: " + str(btn_path) + " to: " + str(btn2_path))
            result = self.sikuli.drag_and_drop(btn_path, btn2_path, similarity=similarity, timeout=timeout, retries=retries, similarity_reduction=similarity_reduction)

        return result,text

    def _restart_executable_and_continue(self):
        print("[RESTART] Restarting executable...")
        self._stop_executable()
        print("Before if's" , self.inputs)
        
        print("Self last input" , self.lastInput)
        if not self.lastInput or not self.inputs.get(self.lastInput):
            return
        if self.inputs[self.lastInput]:
            print("Before pop ", self.inputs)
            self.inputs[self.lastInput].pop()
            print("After pop", self.inputs)
            
        else: 
            return
        
        self._ensure_executable_running()
        self._navigate_to_state(self.inputs[self.lastInput])

    def _add_inputs_to_path(self, btn_path):
        self.inputs[self.lastInput].append(btn_path)
        print("[PATH] " + self.lastInput + " added to path: " + str(btn_path))

    def _navigate_to_state(self, clicks_path, timeout=2):
        print("[NAVIGATE] Replaying the click sequence: " + str(clicks_path))
        for idx, btn_path in enumerate(clicks_path):
            print("[NAVIGATE] (" + str(idx+1) + "/" + str(len(clicks_path)) + ") Clicking on: " + str(btn_path))
            self.sikuli.click_image(btn_path, timeout=timeout, retries = 8, similarity_reduction = 0.05)
            time.sleep(self.delay)
        print("[NAVIGATE] Click sequence completed.")

    def _ensure_executable_running(self):
        if self.process is None:
            self.executable_thread = threading.Thread(target=self._start_executable)
            self.executable_thread.start()
            time.sleep(self.delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a graph using SikuliX and a specified executable.")
    parser.add_argument("--images_dir", required=True, help="Path to the directory containing images.")
    parser.add_argument("--practical_graph_file", required=True, help="Name of the practical graph file to save.")
    parser.add_argument("--selected_executable", required=True, help="Path to the executable to run.")
    parser.add_argument("--delay", type=int, default=5, help="Delay in seconds between actions.")
    parser.add_argument("--timeout", type=int, default=2, help="Timeout in seconds for image matching.")
    parser.add_argument("--initial_similarity", type=float, default=0.99, help="Initial similarity for image matching.")
    parser.add_argument("--min_similarity", type=float, default=0.85, help="Minimum similarity for image matching.")
    parser.add_argument("--similarity_step", type=float, default=0.01, help="Similarity step for image matching.")

    args = parser.parse_args()

    generator = GenerateGraph(
        images_dir=args.images_dir, 
        practical_graph_file=args.practical_graph_file, 
        selected_executable=args.selected_executable,
        delay=args.delay,
        timeout=args.timeout,
        initial_similarity=args.initial_similarity,
        min_similarity=args.min_similarity,
        similarity_step=args.similarity_step
    )
    generator.generate_graph()
