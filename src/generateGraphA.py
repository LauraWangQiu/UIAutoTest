# -*- coding: utf-8 -*-
# generateGraph.py ARREGLADO

import subprocess
import os
import shutil
import threading
import time
from sikulixWrapper import SikulixWrapper
from graphsDef import Graph, Node, Transition
import GraphIO as _graph_io_module
GraphIO = _graph_io_module.GraphIO

class GenerateGraph:
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp'}

    def __init__(self, selected_executable=None):
        self.selected_executable = selected_executable
        self.graph = Graph()
        self.node_inputs = []
        self.delay_ms = 3   # Ahora en segundos para simplificar con time.sleep
        self.actual_node = None
        self.start_node = None
        self.process = None
        self.sikuli = SikulixWrapper()        
        self.graph_io = GraphIO()  
        self._stop_loop = threading.Event()
        self._executable_thread = None
        self._loop_thread = None

    def generate_graph(self):
        print("Generating graph for " + str(self.selected_executable))
        self._executable_thread = threading.Thread()
        self._executable_thread.start()

        self._loop_thread = threading.Thread(target=self._loop)
        self._loop_thread.start()

        # Espera a que termine el bucle
        self._loop_thread.join()
        self._executable_thread.join()

        # when the loop ends, we can save the graph
        self._stop_executable()
        self.graph_io.write_graph("output_graph.txt", self.graph)
        print("[INFO] graph has been saved to output_graph.txt")

    def _start_executable(self):
        try:
            print("[INFO] Starting executable: " + str(self.selected_executable))
            self.process = subprocess.Popen([self.selected_executable])
            self.process.wait()  # Espera a que termine el proceso
            print("[INFO] Executable terminado.")
        except FileNotFoundError:
            print("[INFO] Executable not found: " + str(self.selected_executable))
            self.process = None
        
    """
        Forces the executable to close.
    """
    def _stop_executable(self):
        try:
            if self.process is not None:
                print("[INFO] Stopping executable: " + str(self.selected_executable))
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)  # Waits 5 seconds to terminate.
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
            print("[ERROR] Error on closing executable: "+e)
            self.process = None

    def _loop(self):
        print("[LOOP] Starting graph generation loop...")
        actual_path = os.getcwd()
        self_path = os.path.join(actual_path, "imgs", "self_nodes")
        generated_path = os.path.join(actual_path, "imgs", "generated_nodes")
        visited_images = set()
        all_images = set(
            os.path.join(root, file)
            for root, _, files in os.walk(self_path)
            for file in files
            if os.path.splitext(file)[1].lower() in self.valid_extensions
            )
        
        print("[LOOP] All images: " + str(len(all_images)))

        while not self._stop_loop.is_set(): #mientras que no se haya terminado 
            end_loop = False
            print("[LOOP] Restarting loop...")
            self._ensure_executable_running() #asegurarse de que el ejecutable esta corriendo
            time.sleep(self.delay_ms)
            try:
                while not end_loop: # mientras que no termine el bucle
                    print("[LOOP] Trying branch...")
                    found_node = self._process_states(self_path, visited_images)
                    if not found_node:
                        self._handle_no_node_found(self_path)
                        end_loop = True
                    if self._should_end_loop(visited_images, all_images):
                        print("[LOOP] All images visited, ending loop.")
                        end_loop = True
                        self._stop_loop.set()
            except Exception as e:
                print("[LOOP] Error: " + str(e))
                end_loop = True
                self._stop_loop.set()
                break
            self._close_executable_if_needed(visited_images, all_images, found_node)
        print("[LOOP] Graph loop finished.")

    def _ensure_executable_running(self):
        if self.process is None:
            self._executable_thread = threading.Thread(target=self._start_executable)
            self._executable_thread.start()

    def _process_states(self, self_path, visited_images):
        found_node = False
        
        for file in os.listdir(self_path):
            state_path = os.path.join(self_path, file)
            print("[LOOP] Processing state: " + state_path)
            f = [
                file for file in os.listdir(state_path)
                if os.path.isfile(os.path.join(state_path, file)) and
                   os.path.splitext(file)[1].lower() in self.valid_extensions
                ]
            print("[LOOP] Files in state: " + str(f))
            if len(f) <= 0:
                print("[LOOP] No images found in state: " + state_path)
                continue
            image_menu = os.path.join(state_path, f[0])
            print("[LOOP] Images in state: " + str(image_menu))
            # If screen si the same as image_menu[0]
            if self.sikuli.search_image(os.path.join(state_path, image_menu), timeout=0.001):  
                found_node = True
                node = self.graph.get_node(image_menu)
                if node is None:
                    self.graph.add_node_with_image(name=image_menu,image_path=os.path.join(state_path, image_menu))
                    new_node = self.graph.get_node(image_menu)
                    print("[LOOP] New node added: " + new_node.name)
                    self.input_sikuli(os.path.join(state_path, "buttons"), new_node)
                    visited_images.add(state_path)  # Add the folder to the visited files.
                else:
                    # If node is already in the graph, check if it has an unused transition.
                    print("[LOOP] Node already in graph: " + image_menu)
                    path = self.check_transition(os.path.join(state_path, "buttons", "click"), node)
                    if path is not None:
                        print("[LOOP] Found unused transition, clicking...")
                        self.click(path, node)
                        time.sleep(self.delay_ms)
                    else:
                        print("[LOOP] All transitions visited, moving to next branch.")
                        end_loop = True  # All transitions visited, end loop.
                        return found_node
        return found_node

    def _handle_no_node_found(self, self_path):
        self.sikuli.capture_error("error_wait_.png")
        self.graph.add_node("NewNode")

    def _should_end_loop(self, visited_images, all_images):
        print("[LOOP] Checking if loop should end...")
        return len(visited_images) >= len(all_images)

    def _close_executable_if_needed(self, visited_images, all_images, found_node):
        print("[LOOP] Closing executable if needed...")
        # Close game
        if self.process is not None:
            self._stop_executable()
            
        # If graph has visited all images, end the loop
        if self._should_end_loop(visited_images, all_images):
            print("[LOOP] All images visited, ending loop.")
            end_loop = True
            self._stop_loop.set()
        if found_node and self.actual_node is None:
            pass
        print("[LOOP] Bucle de grafo terminado.")  

    """
        Method to check if a transition has been visited. 
    """
    def input_sikuli(self, buttons_path, node):
        print("[INPUT_SIKULI] Iniciando input_sikuli...")
        path = self.check_transition(os.path.join(buttons_path,"click"), node) 
        print("[INPUT_SIKULI] Path: " + str(path))
        if path is not None:
            self.click(path, node)
        else:
            return None

    """
        Method to check if the transition has been visited.
        If it have a transition that has not been visited, it will return it, else return None.
    """
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
        print("[INPUT_SIKULI] All thansitions visited.")
        return None

    """
        Clicks on the images in the given path.
    """
    def click(self, image_path, node):
        print("[INPUT_SIKULI] Clicking on image: " + image_path)
        transition = Transition(node)
        print("[INPUT_SIKULI] Transitions: ", node.transitions)
        transition.image = image_path
        node.add_transition(transition)
        self.sikuli.click_image(image_path, timeout=0.001)

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))  # Obtiene el directorio actual del script
    executable_path = os.path.join(base_path, "../bin/Cooking Bibble/Cooking Bibble.exe")  # Ruta relativa
    generator = GenerateGraph(executable_path)
    generator.generate_graph()
