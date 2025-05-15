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
        # Close game and restart
        self.process.terminate()
        self.process.wait()
        print("[INFO] Executable terminated.")

    def _start_executable(self):
        try:
            print("[INFO] Starting executable: " + str(self.selected_executable))
            self.process = subprocess.Popen([self.selected_executable])
            self.process.wait()  # Espera a que termine el proceso
            print("[INFO] Executable terminado.")
        except FileNotFoundError:
            print("[INFO] Executable not found: " + str(self.selected_executable))
            self.process = None

        # Marca para terminar el bucle del grafo cuando acabe el ejecutable
        self._stop_loop.set()

    def _loop(self):
        time.sleep(self.delay_ms)  # Espera antes de volver a iterar
        print("[LOOP] Iniciando bucle de generación de grafo...")
        actual_path = os.getcwd()
        self_path = os.path.join(actual_path, "imgs", "self_nodes")
        generated_path = os.path.join(actual_path, "imgs", "generated_nodes")
        end_loop = False # Flag to end the loop
        while not self._stop_loop.is_set() and not end_loop:
            found_node = False
            for file in os.listdir(self_path):
                state_path = os.path.join(self_path, file)
                image_menu = [f for f in os.listdir(state_path) if os.path.isfile(os.path.join(state_path, f))]
                #print("[LOOP] Archivo válido encontrado: " + state_path)
                if self.sikuli.search_image(os.path.join(state_path, image_menu[0]), timeout=0.001):  # Si la pantalla coincide
                    print("[LOOP] Imagen coincidente encontrada: " + image_menu[0])
                    found_node = True
                    if self.graph.is_node_in_graph(image_menu[0]):
                        print("[LOOP] Node already in graph: " + image_menu[0])
                        self._stop_loop.set()  # Ends the loop
                        return
                    
                    new_node = Node(image_menu[0]) # Creates a new node
                    new_node.set_image(os.path.join(state_path, image_menu[0])) # Sets the image
                    self.graph.add_node(new_node.name)
                    self.input_sikuli(os.path.join(state_path, "buttons"), new_node)
                    break
            if not found_node:
                self.sikuli.capture_error("error_wait_.png")
                self.graph.add_node("NewNode")
                
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
        buttons_images = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
        for img in buttons_images:
            print("[INPUT_SIKULI] clicking "+os.path.join(images_path,img)+"...")
            transition = Transition(node)
            node.add_transition(transition)
            self.sikuli.click_image(os.path.join(images_path,img),timeout=0.001)

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))  # Obtiene el directorio actual del script
    executable_path = os.path.join(base_path, "../bin/Cooking Bibble/Cooking Bibble.exe")  # Ruta relativa
    generator = GenerateGraph(executable_path)
    generator.generate_graph()
