# -*- coding: utf-8 -*-
# generateGraph.py ARREGLADO

import subprocess
import os
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

        # Cuando todo termina, guarda el grafo
        self.graph_io.write_graph("output_graph.txt", self.graph)
        print("Grafo generado y guardado.")

    def _start_executable(self):
        try:
            print("Starting executable: " + str(self.selected_executable))
            self.process = subprocess.Popen([self.selected_executable])
            self.process.wait()  # Espera a que termine el proceso
            print("Executable terminado.")
        except FileNotFoundError:
            print("Executable not found: " + str(self.selected_executable))
            self.process = None

        # Marca para terminar el bucle del grafo cuando acabe el ejecutable
        self._stop_loop.set()

    def _loop(self):
        time.sleep(self.delay_ms)  # Espera antes de volver a iterar
        print("[LOOP] Iniciando bucle de generación de grafo...")
        actual_path = os.getcwd()
        folder_path = os.path.join(actual_path, "imgs", "self_nodes")
        print("[LOOP] Carpeta de nodos: " + folder_path)
        while not self._stop_loop.is_set():
            found_node = False
            for file in os.listdir(folder_path):
                state_path = os.path.join(folder_path, file)
                image_menu = [f for f in os.listdir(state_path) if os.path.isfile(os.path.join(state_path, f))]
                print("[LOOP] Revisando archivo: " + os.path.join(state_path, image_menu[0]))
                #if os.path.isfile(image_menu[0]) and os.path.splitext(image_menu[0])[1].lower() in self.valid_extensions:
                #print("[LOOP] Archivo válido encontrado: " + state_path)
                if self.sikuli.search_image(os.path.join(state_path, image_menu[0]), timeout=1):  # Si la pantalla coincide
                    print("[LOOP] Imagen coincidente encontrada: " + state_path)
                    new_node = Node("a")
                    #new_node.set_image(os.path.join(state_path, image_menu[0]))
                    self.graph.add_node(new_node.name)
                    found_node = True
                    print("[LOOP] Nodo añadido al grafo: " + new_node.name)
                    self.input_sikuli(os.path.join(folder_path, "buttons"), new_node)
                    break
            if not found_node:
                print("[LOOP] No se encontró nodo, creando uno nuevo...")                
                self.sikuli.capture_error("error_wait_.png")
                self.graph.add_node("NewNode")
                print("[LOOP] Nodo 'NewNode' añadido al grafo.")

        print("[LOOP] Bucle de grafo terminado.")

    # Si quieres dejar input_sikuli y click, hazlos métodos de instancia
    def input_sikuli(self, buttons_path, node):
        print("[INPUT_SIKULI] Iniciando input_sikuli...")
        click_buttons_path = os.path.join(buttons_path,"click")
        self.click(click_buttons_path, node)

    def click(self, images_path, node):
        buttons_images = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
        for img in buttons_images:
            print("[INPUT_SIKULI] clicking "+img+"...")
            transition = Transition(node)
            node.add_transition(transition)
            self.sikuli.click_image(img)
            # Aquí podrías añadir más lógica si quieres seguir el ciclo tras cada click

if __name__ == "__main__":
    # Example usage
    executable_path = "C://Users//Andrés//Documents//GitHub//UIAutoTest//bin//Cooking Bibble//Cooking Bibble.exe"
    generator = GenerateGraph(executable_path)
    generator.generate_graph()
    graph = generator.get_graph()
