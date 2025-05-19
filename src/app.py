# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import threading


import inspect
import importlib.util

from test import Test
from graphsDef import Graph

import graphIO as _graph_io_module
GraphIO = _graph_io_module.GraphIO
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class App():
    """
        Constructor for the App class

        Args:
            tests_directory (str): The directory where test files are located
    """
    def __init__(self, 
                java_path, jython_jar, sikulix_jar,
                sikuli_script,
                images_dir, tests_dir, 
                theorical_graph_file,
                practical_graph_file,
                selected_executable,
                executable_delay,
                transition_delay,
                debug_images,
                timeout,
                initial_similarity,
                min_similarity,
                similarity_step,
                retries,
                state_reset_method,
                external_reset_script,
                tests_to_run,
                solution_file,
                pdf_file):
        
        self.java_path = java_path                                      # Path to Java executable
        self.jython_jar = jython_jar                                    # Path to Jython jar file
        self.sikulix_jar = sikulix_jar                                  # Path to SikuliX jar file
        self.sikuli_script = sikuli_script                              # Path to Sikuli script

        self.jython_thread = None                                       # Jython thread
            
        self.graph_io = GraphIO()                                       # GraphIO instance
        self.graph = Graph()                                            # Theorical graph
        self.generated_graph = None                                     # Practical graph
        self.theorical_graph_file   = theorical_graph_file              # Theoretical graph file
        self.practical_graph_file   = practical_graph_file              # Practical graph file
        self.images_dir             = images_dir                        # Directory of images
        self.tests_dir              = tests_dir                         # Directory of tests
        self.test_classes           = None                              # List of test classes        
        self.selected_executable    = selected_executable               # Selected executable path
        self.executable_delay       = executable_delay                  # Delay for the executable to start
        self.transition_delay       = transition_delay                  # Delay for the transition to complete
        self.debug_images           = debug_images                      # Flag to show debug images when generating the graph
        self.timeout                = timeout                           # Timeout for SikuliX
        self.initial_similarity     = initial_similarity                # Initial similarity for SikuliX
        self.min_similarity         = min_similarity                    # Minimum similarity for SikuliX
        self.similarity_step        = similarity_step                   # Similarity step for SikuliX
        self.retries                = retries                           # Number of retries for SikuliX
        self.state_reset_method     = state_reset_method                # State reset method
        self.external_reset_script  = external_reset_script             # External reset script
        self.tests_to_run           = tests_to_run                      # List of tests to run
        self.solution_file          = solution_file                     # Test solution file
        self.pdf_file               = pdf_file                          # PDF file for graph differences and tests results                         # Store the headless mode flag

        self.diff = {
            'missing_nodes_prac': set(),
            'missing_nodes_theo': set(),
            'missing_edges_gen': set(),
            'missing_edges_the': set(),
        }
        self.test_results = []
        
    """
        Load theorical graph from a file using GraphIO
    """
    def load_graph_from_file(self, file_name):
        try:
            self.graph = self.graph_io.load_graph(file_name, self.images_dir)
            if self.graph is None:
                print("[ERROR] Graph not loaded")
                return False
            print("[INFO] Graph successfully loaded")
            return True
        except FileNotFoundError:
            print("[ERROR] File " + file_name + " not found")
        except Exception as e:
            print("[ERROR] An error occurred while loading the graph: " + str(e))

        return False

    # ==============================================================================================
    # TESTS TAB
    # ==============================================================================================
    """
        Get all test classes from the specified directory
        The test classes should inherit from the Test class
        Returns a list of test class names
    """
    def get_test_classes(self):
        test_classes = []
        test_folder = os.path.join(os.getcwd(), self.tests_dir)

        for file_name in os.listdir(test_folder):
            if file_name.endswith(".py"):
                file_path = os.path.join(test_folder, file_name)
                module_name = file_name[:-3]

                # Load dynamically the tests
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Search for classes that inherit from Test
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Test) and obj is not Test:
                        test_classes.append((name, obj))

        return test_classes

    def update_test_output(self, test_class_name, attr_name, values):
        try:
            if test_class_name not in self.test_output_widgets:
                print(f"[WARNING] No widgets found for test class '{test_class_name}'")
                return
            if attr_name not in self.test_output_widgets[test_class_name]:
                print(f"[WARNING] No widget for attribute '{attr_name}' in test class '{test_class_name}'")
                return
            textbox = self.test_output_widgets[test_class_name][attr_name]
            textbox.configure(state="normal")
            textbox.delete("1.0", "end")
            textbox.insert("1.0", str(values))
            textbox.configure(state="disabled")
        except Exception as e:
            print(f"[ERROR] update_test_output failed: {e}")

    """
        Generate the graph from the selected executable calling the Jython script
    """
    def generate_graph_from_executable(self):
        if not self.selected_executable:
            print("[ERROR] No executable selected. Please select an executable first.")
            return
        
        if not self.images_dir:
            print("[ERROR] No images directory selected. Please select an images directory first.")
            return

        self.run_jython()

    """
        Run the selected tests. 
    """
    def run_tests(self):
        selected_test_classes = []
        
        selected_test_classes = self.get_selected_test_classes()
        
        if selected_test_classes:
            self.execute_selected_tests(selected_test_classes)
        else:
            print("[ERROR] No tests selected.")
        pass
        
    """
        Base for the children for returning the selected tests for running the tests.
    """   
    def get_selected_test_classes(self):
        pass 
        
    """
        Run the Jython script to generate the graph
    """
    def run_jython(self):
        def execute_command():
            try:
                command = [
                    self.java_path,
                    "-cp",
                    f"{self.jython_jar};{self.sikulix_jar}",
                    "org.python.util.jython",
                    self.sikuli_script,
                    "--images_dir", self.images_dir,
                    "--practical_graph_file", self.practical_graph_file,
                    "--selected_executable", self.selected_executable,
                    "--executable_delay", str(self.executable_delay),
                    "--transition_delay", str(self.transition_delay),
                ]
                if self.debug_images:
                    command.append("--debug_images")
                command += [
                    "--timeout", str(self.timeout),
                    "--initial_similarity", str(self.initial_similarity),
                    "--min_similarity", str(self.min_similarity),
                    "--similarity_step", str(self.similarity_step),
                    "--retries", str(self.retries),
                    "--state_reset_method", str(self.state_reset_method),
                    "--external_reset_script", str(self.external_reset_script),
                ]
                print("[INFO] Running Jython script: " + " ".join(command))
                process = subprocess.Popen(
                    command,
                    stdout=sys.__stdout__,
                    stderr=sys.__stderr__,
                    text=True,
                    shell=True
                )
                self.jython_process = process
                process.wait()  # Espera solo dentro del subhilo, no bloquea la GUI
                print("[INFO] Jython script finished.")
            except Exception as e:
                print("[ERROR] Failed to run Jython script: " + str(e))
            finally:
                self.jython_process = None

        self.jython_thread = threading.Thread(target=execute_command, daemon=True)
        self.jython_thread.start()

    """
        Execute the selected tests
    """
    def execute_selected_tests(self, selected_test_classes):
        file_path = os.path.abspath(self.practical_graph_file)
        self.generated_graph = self.graph_io.load_graph(file_path, self.images_dir)
        if self.generated_graph is None:
            print("[ERROR] No generated graph found. Please generate the graph first or select correctly.")
            return

        test_instances = []
        for test_class_ref in selected_test_classes:
            test_instance = test_class_ref(self.generated_graph, self.solution_file)
            test_class_name = getattr(test_instance, "name", test_class_ref.__name__)
            test_instance.set_update_callback(lambda attr_name, content, tcn=test_class_name: self.update_test_output(tcn, attr_name, content))
            test_instance.run()
            test_instance.write_solution()
            self.test_results.append(test_instance.get_results())
            test_instances.append((test_class_name, test_instance))

    """
        Compare the generated graph with specified graph
    """
    def compare(self):
        print("aqui llega")
        file_path = os.path.abspath(self.practical_graph_file)
        # Check if the graph is already loaded
        if self.generated_graph is None:
            self.generated_graph = self.graph_io.load_graph(file_path, self.images_dir)
        if self.generated_graph is None:
            print("[ERROR] No generated graph found. Please generate the graph first or select correctly.")
            return
        # Check if the given graph is already loaded
        if not self.graph or not hasattr(self.graph, "nodes") or not self.graph.nodes:
            self.load_graph_from_file(self.theorical_graph_file)
        if not self.graph or not hasattr(self.graph, "nodes") or not self.graph.nodes:
            print("[ERROR] No given graph found. Please load the given graph first or generate it and save it.")
            return
        print("[INFO] Comparing results...")
        differences_found = 0
        try:
            with open(self.solution_file, "a") as f:
                print("[INFO] Comparing generated graph with given graph...")
                f.write("[COMPARING GENERATED GRAPH vs GIVEN GRAPH]\n")
                differences_found += self.compare_aux(f, self.generated_graph, self.graph, self.theorical_graph_file, "diff_in_gen")
                print("[INFO] Comparing given graph with generated graph...")
                f.write("[COMPARING GIVEN GRAPH vs GENERATED GRAPH]\n")
                differences_found += self.compare_aux(f, self.graph, self.generated_graph, self.practical_graph_file, "diff_in_the")
                if differences_found == 0:
                    f.write("[NO DIFFERENCES FOUND]\n")
            print("[INFO] Comparison finished. No differences found." if differences_found == 0 else f"[INFO] Comparison finished. {differences_found} differences found.")
        except Exception as e:
            print(f"[ERROR] Exception during comparison: {e}")

    def compare_aux(self, file_output, graph1:Graph, graph2:Graph, graph_file:str, diff_in):
        differences_found = 0
        for node1 in graph1.nodes:
            print("[INFO] Comparing node: " + node1.name)
            node2 = graph2.get_node_image(node1.image)
            if node2 is None: # Node is not in generated graph
                print("[INFO] Node not found: " + node1.name)
                file_output.write("[MISSING NODE] " + node1.name + " not in " + graph_file + "\n")
                if diff_in == "diff_in_gen":
                    self.diff['missing_nodes_theo'].add(node1.name)
                else:
                    self.diff['missing_nodes_prac'].add(node1.name)
                differences_found += 1
                continue

            for trans1 in node1.transitions:
                dest_image = trans1.destination.image
                found = False
                
                for trans2 in node2.transitions:
                    print("[INFO] Comparing transition: " + trans1.image)
                    if trans2.image == trans1.image:
                        print("[INFO] Transition found: " + trans1.image)
                        if trans2.destination.image != dest_image:
                            print("[INFO] Transition mismatch: " + trans1.image)
                            # Writes the objetive destination and the real destination
                            file_output.write("[MISMATCH TRANSITION] Supposed: " + node1.name + " -/-> " + trans1.destination.name + " Real: " + node1.name +" -> " + trans2.destination.name + "\n")
                            self.diff['mismatch_trans'].append((node1.name, trans1.destination.name, trans2.destination.name, f"{graph1.name} vs {graph2.name}"))   
                            if diff_in == "diff_in_gen":
                                self.diff['missing_edges_the'].add((node1.name, trans1.destination.name))                         
                            else:
                                self.diff['missing_edges_gen'].add((node1.name, trans1.destination.name))
                            differences_found += 1
                        found = True
                        continue
                if not found:
                    print("[INFO] Transition not found: " + trans1.image)
                    file_output.write("[MISSING TRANSITION] " + node1.name + " -/-> " + trans1.destination.name + " " + trans1.image + "\n")
                    if diff_in == "diff_in_gen":
                        self.diff['missing_edges_the'].add((node1.name, trans1.destination.name))
                    else:
                        self.diff['missing_edges_gen'].add((node1.name, trans1.destination.name))
                    differences_found += 1
        return differences_found

    """
        Creates a PDF with the diff graph after the comparison. 
    """                 
    def create_PDF(self, output_pdf_path: str):
        try:
            # A4.
            page_size = (8.27, 11.69)

            with PdfPages(output_pdf_path) as pdf:
                # ------PAG.1------
                pag1 = plt.figure(figsize = page_size)
                gs_p1 = gridspec.GridSpec(
                    nrows = 2, ncols = 3,
                    height_ratios = [0.1, 0.9],
                    width_ratios = [0.2, 0.6, 0.2],
                    hspace = 0.0, wspace = 0.0
                )


                # Tittle:
                doc_title = pag1.add_subplot(gs_p1[0, 0])
                doc_title.axis('off')
                doc_title.text(0.0, 0.8, "Difference between \nthe theo_graph \nand the gen_graph:", fontsize = 20, va = 'top')


                # Caption:
                doc_legend = pag1.add_subplot(gs_p1[0, 2])
                doc_legend.axis('off')

                black_caption = mpatches.Patch(color = 'black', label = 'In both graphs')
                red_caption = mpatches.Patch(color = 'red',   label = 'Not in generated graph')
                green_caption = mpatches.Patch(color = 'green', label = 'Not in theorical graph') 
                caption = [black_caption, red_caption, green_caption]

                doc_legend.legend(handles = caption, loc = 'upper right', fontsize = 15, frameon = True, labelcolor = "orange")


                # Graph:
                doc_graph = pag1.add_subplot(gs_p1[1, 0:3])
                doc_graph.axis('off')

                G = nx.DiGraph()
                all_nodes = {n.name for n in self.graph.nodes} | {n.name for n in self.generated_graph.nodes}
                for name in all_nodes:
                    if name in self.diff['missing_nodes_prac']:
                        color = 'red'
                    elif name in self.diff['missing_nodes_theo']:
                        color = 'green'
                    else:
                        color = 'black'
                    G.add_node(name, color=color)

                for n in self.graph.nodes:
                    for t in n.transitions:
                        u, v = n.name, t.destination.name
                        edge_color = 'red' if (u, v) in self.diff['missing_edges_gen'] else 'black'
                        G.add_edge(u, v, color = edge_color, style = 'solid')
                for (u, v) in self.diff['missing_edges_the']:
                    G.add_edge(u, v, color = 'green', style = 'solid')

                pos = nx.spring_layout(G)
                nx.draw_networkx_nodes(
                    G, pos,
                    node_size = 1500,
                    node_color = [G.nodes[n]['color'] for n in G.nodes()],
                    ax = doc_graph
                )
                nx.draw_networkx_labels(G, pos, font_size = 9, font_color = 'white', ax = doc_graph)
                for u, v, attr in G.edges(data = True):
                    nx.draw_networkx_edges(
                        G, pos, edgelist = [(u, v)],
                        style = attr['style'],
                        edge_color = attr['color'],
                        arrowsize = 30, width = 3,
                        ax = doc_graph
                    )

                pdf.savefig(pag1, bbox_inches = 'tight')
                plt.close(pag1)


                # ------PAG.2------           
                tests = self.test_results
                pag2 = plt.figure(figsize = page_size)

                nrows = 1 + len(tests)
                height_ratios = [0.1] + [0.9 / len(tests)] * len(tests)
                gs_p2 = gridspec.GridSpec(
                    nrows = nrows, ncols = 1,
                    height_ratios = height_ratios,
                    hspace = 0.0, wspace = 0.0
                )

                doc_tests = pag2.add_subplot(gs_p2[0, 0])
                doc_tests.axis('off')
                doc_tests.text(0.0, 0.8, "Test results: ", fontsize = 20, va = 'top')

                for i, (ttype, data) in enumerate(tests, start = 1):
                    doc_tests_test = pag2.add_subplot(gs_p2[i, 0])
                    doc_tests_test.axis('off')

                    if ttype == "TCT":
                        nodes, trans = data
                        nodes_text = "\n".join(sorted(nodes)) if nodes else "None"
                        transitions_text = "\n".join(f"{u} → {v}" for u, v in sorted(trans)) if trans else "None"
                        text = (
                            "Total Coverage Test:\n\n"
                            f"Visited nodes:\n{nodes_text}\n\n"
                            f"Visited transitions:\n{transitions_text}"
                        )
                        doc_tests_test.text(0.0, 0.8, text, fontsize=10, va='top')

                    elif ttype == "SLT":
                        result = data
                        if not result or all(len(s) == 0 for s in result):
                            text = "Self Loop Test:\n\nNo nodes with self loops found."
                        else:
                            text = "Self Loop Test:\n\n" + "\n".join(result[0])
                        doc_tests_test.text(0.0, 0.8, text, fontsize = 10, va='top')

                    elif ttype == "PPCT":
                        result = data
                        if not result or len(result[0]) == 0:
                            text = "Prime Path Coverage Test:\n\nNo prime paths found."
                        else:
                            text = "Prime Path Coverage Test:\n\n" + "\n".join(result[0])
                        doc_tests_test.text(0.0, 0.8, text, fontsize = 10, va = 'top')

                    elif ttype == "EPCT":
                        result = data
                        if not result or all(len(s) == 0 for s in result):
                            text = "Edge Pair Coverage Test:\n\nNo edge pairs found."
                        else:
                            pairs = result[0]
                            text = "Edge Pair Coverage Test:\n\n" + "\n".join(f"From '{u}' to '{v}'" for u, v in sorted(pairs))
                        doc_tests_test.text(0.0, 0.8, text, fontsize = 10, va = 'top')

                pdf.savefig(pag2, bbox_inches='tight')
                plt.close(pag2)
            
            print(f"[INFO] Report PDF done in {output_pdf_path}")
        except Exception as e:
            print(f"[ERROR] Error while doing the PDF: {e}")
