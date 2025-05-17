# -*- coding: utf-8 -*-
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
    
from app import App

"""
    Load configuration from a JSON file if manually specified.
    Otherwise, use default parameters.
"""
def load_config(config_file):
    try:
        with open(config_file, "r") as file:
            config = json.load(file)
        print(f"[INFO] Configuration loaded from {config_file}")
        return config
    except FileNotFoundError:
        print(f"[ERROR] Configuration file {config_file} not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse configuration file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    config_file = None
    if len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
        config_file = sys.argv[1]

    config = {}
    if config_file:
        config = load_config(config_file)
    
    java_path =             config.get("java_path", "java")
    jython_jar =            config.get("jython_jar", "jython-standalone-2.7.4.jar")
    sikulix_jar =           config.get("sikulix_jar", "sikulixapi-2.0.5.jar")
    images_dir =            config.get("images_dir", "imgs")
    tests_dir =             config.get("tests_dir", "tests")
    theorical_graph_file =  config.get("theorical_graph_file", "graph.txt")
    practical_graph_file =  config.get("practical_graph_file", "output_graph.txt")
    generate_graph =        config.get("generate_graph", True)
    selected_executable =   config.get("selected_executable", None)
    executable_delay =      config.get("executable_delay", "5")
    timeout =               config.get("timeout", 2)
    initial_similarity =    config.get("initial_similarity", 0.99)
    min_similarity =        config.get("min_similarity", 0.85)
    similarity_step =       config.get("similarity_step", 0.01)
    tests_to_run =          config.get("tests_to_run", [])
    solution_file =         config.get("solution_file", "solution.txt")

    headless = True if config_file else False
    
    app = App(
        java_path=java_path,
        jython_jar=jython_jar,
        sikulix_jar=sikulix_jar,
        sikuli_script="src/generateGraph.py",
        window_name="UIAutoTest",
        window_size="800x600",
        images_dir=images_dir,
        tests_dir=tests_dir,
        theorical_graph_file=theorical_graph_file,
        practical_graph_file=practical_graph_file,
        generate_graph=generate_graph,
        selected_executable=selected_executable,
        executable_delay=executable_delay,
        timeout=timeout,
        initial_similarity=initial_similarity,
        min_similarity=min_similarity,
        similarity_step=similarity_step,
        tests_to_run=tests_to_run,
        solution_file=solution_file,
        headless=headless
    )
