# -*- coding: utf-8 -*-
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
    
from stateResetMethod import StateResetMethod
from interface import Interface
from console import Console

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
    images_dir =            config.get("images_dir", None)
    tests_dir =             config.get("tests_dir", "tests")
    theorical_graph_file =  config.get("theorical_graph_file", None)
    practical_graph_file =  config.get("practical_graph_file", "output_graph.txt")
    generate_graph =        config.get("generate_graph", True)
    selected_executable =   config.get("selected_executable", None)
    executable_delay =      config.get("executable_delay", "5")
    transition_delay =      config.get("transition_delay", "2")
    debug_images =          config.get("debug_images", False)
    timeout =               config.get("timeout", 2)
    initial_similarity =    config.get("initial_similarity", 0.99)
    min_similarity =        config.get("min_similarity", 0.85)
    similarity_step =       config.get("similarity_step", 0.01)
    retries =               config.get("retries", 8)
    state_reset_method =    config.get("state_reset_method", StateResetMethod.NONE)
    if state_reset_method not in StateResetMethod.values():
        print(f"[ERROR] Invalid state reset method: {state_reset_method}. Setting to default {StateResetMethod.NONE}.")
        state_reset_method = StateResetMethod.NONE
    external_reset_script = config.get("external_reset_script", None)
    tests_to_run =          config.get("tests_to_run", [])
    pdf_file =              config.get("pdf_file", "report.pdf")
    solution_file =         config.get("solution_file", "solution.txt")

    headless = True if config_file else False
    
    if headless:
        app = Console(
            java_path=java_path,
            jython_jar=jython_jar,
            sikulix_jar=sikulix_jar,
            sikuli_script="src/generateGraph.py",
            images_dir=images_dir,
            tests_dir=tests_dir,
            theorical_graph_file=theorical_graph_file,
            practical_graph_file=practical_graph_file,
            generate_graph=generate_graph,
            selected_executable=selected_executable,
            executable_delay=executable_delay,
            transition_delay=transition_delay,
            debug_images=debug_images,
            timeout=timeout,
            initial_similarity=initial_similarity,
            min_similarity=min_similarity,
            similarity_step=similarity_step,
            retries=retries,
            state_reset_method=state_reset_method,
            external_reset_script=external_reset_script,
            tests_to_run=tests_to_run,
            solution_file=solution_file,
            pdf_file=pdf_file)
    else:
        interface = Interface(
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
            selected_executable=selected_executable,
            executable_delay=executable_delay,
            transition_delay=transition_delay,
            debug_images=debug_images,
            timeout=timeout,
            initial_similarity=initial_similarity,
            min_similarity=min_similarity,
            similarity_step=similarity_step,
            retries=retries,
            state_reset_method=state_reset_method,
            external_reset_script=external_reset_script,
            tests_to_run=tests_to_run,
            solution_file=solution_file,
            pdf_file=pdf_file)