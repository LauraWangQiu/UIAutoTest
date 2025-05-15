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
        self._executable_thread = threading.Thread(target=self._start_executable)
        self._executable_thread.start()

        self._loop_thread = threading.Thread(target=self._loop)
        self._loop_thread.start()

        # Espera a que termine el bucle
        self._loop_thread.join()
        self._executable_thread.join()

        # when the loop ends, we can save the graph
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

        print("[LOOP] Iniciando bucle de generación de grafo...")
        actual_path = os.getcwd()
        self_path = os.path.join(actual_path, "imgs", "self_nodes")
        generated_path = os.path.join(actual_path, "imgs", "generated_nodes")
        # set to save the visited folders
        visited_images = set()  
        all_images = set([i for i, _, _ in os.walk(self_path) if os.path.isfile(i)]) # All images in self_path
        while not self._stop_loop.is_set():
            end_loop = False # Flag to end the loop
            print("[LOOP] Restarting loop...")
            # Restart the executable.
            if self.process is None:
            	self._executable_thread = threading.Thread(target=self._start_executable)
                self._executable_thread.start()
            time.sleep(self.delay_ms)  # Espera antes de volver a iterar
            while not end_loop:
                print("[LOOP] Trying branch...")
                found_node = False
                for file in os.listdir(self_path):
                    state_path = os.path.join(self_path, file)
                    image_menu = [f for f in os.listdir(state_path) if os.path.isfile(os.path.join(state_path, f))]
                    # If screen si the same as image_menu[0]
                    if self.sikuli.search_image(os.path.join(state_path, image_menu[0]), timeout=0.001):  
                        print("[LOOP] Founded screen: " + image_menu[0])
                        found_node = True
                        if self.graph.is_node_in_graph(image_menu[0]):
                            print("[LOOP] Node already in graph: " + image_menu[0])
                            visited_images.add(state_path)  # Add the folder to the visited folders
                            end_loop = True
                            break

                        new_node = Node(image_menu[0]) # Creates a new node
                        new_node.set_image(os.path.join(state_path, image_menu[0])) # Sets the image
                        self.graph.add_node(new_node.name)
                        self.input_sikuli(os.path.join(state_path, "buttons"), new_node)
                        break
                if not found_node:
                    self.sikuli.capture_error("error_wait_.png")
                    self.graph.add_node("NewNode")
            
            # Close game
            if self.process is not None:
                self._stop_executable()
                

            # If graph has visited all images, end the loop
            if len(visited_images) >= len(all_images):
                print("[LOOP] All images visited, ending loop.")
                end_loop = True
        if found_node and self.actual_node is None:
            pass
        print("[LOOP] Bucle de grafo terminado.")  

    # Si quieres dejar input_sikuli y click, hazlos métodos de instancia
    def input_sikuli(self, buttons_path, node):
        print("[INPUT_SIKULI] Iniciando input_sikuli...")
        if self.check_transition(buttons_path, node):
            click_buttons_path = os.path.join(buttons_path,"click")
            self.click(click_buttons_path, node)

    """
        Checks if the transitions of actual node had been visited.
    """
    def check_transition(self, buttons_path, node):
        return True  # Aquí puedes implementar la lógica para verificar si las transiciones han sido visitadas
    """
        Clicks on the images in the given path.
    """
    def click(self, images_path, node):
        if not os.path.isdir(images_path):
            print("[INPUT_SIKULI] El directorio " + images_path + " no existe o no es un directorio. Saltando click.")
            return
        buttons_images = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
        for img in buttons_images:
            print("[INPUT_SIKULI] clicking " + os.path.join(images_path, img) + "...")
            transition = Transition(node)
            node.add_transition(transition)
            self.sikuli.click_image(os.path.join(images_path, img), timeout=0.001)

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))  # Obtiene el directorio actual del script
    executable_path = os.path.join(base_path, "../bin/Cooking Bibble/Cooking Bibble.exe")  # Ruta relativa
    generator = GenerateGraph(executable_path)
    generator.generate_graph()
