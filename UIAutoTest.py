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
    SIKULIX_SCRIPT  = "src/generateGraph.py"
    WINDOW_NAME     = "UIAutoTest"
    WINDOW_SIZE     = "800x600"

    JAVA_DEFAULT_PATH               = "java"
    JYTHON_DEFAULT_JAR              = "jython-standalone-2.7.4.jar"
    SIKULIX_DEFAULT_JAR             = "sikulixapi-2.0.5.jar"
    IMAGES_DEFAULT_DIR              = None
    TESTS_DEFAULT_DIR               = "tests"
    THEORICAL_GRAPH_DEFAULT_FILE    = None
    PRACTICAL_GRAPH_DEFAULT_FILE    = "output_graph.txt"
    GENERATE_GRAPH_DEFAULT          = True
    SELECTED_EXECUTABLE_DEFAULT     = None
    EXECUTABLE_DELAY_DEFAULT        = 5
    TRANSITION_DELAY_DEFAULT        = 2
    DEBUG_IMAGES_DEFAULT            = False
    TIMEOUT_DEFAULT                 = 2
    INITIAL_SIMILARITY_DEFAULT      = 0.99
    MIN_SIMILARITY_DEFAULT          = 0.85
    SIMILARITY_STEP_DEFAULT         = 0.01
    RETRIES_DEFAULT                 = 8
    STATE_RESET_METHOD_DEFAULT      = StateResetMethod.NONE
    EXTERNAL_RESET_SCRIPT_DEFAULT   = None
    TESTS_TO_RUN_DEFAULT            = ["EdgePairCovTest", "PrimePathCovTest", "SelfLoopTest", "TotalConnectTest"]
    PDF_FILE_DEFAULT                = "report.pdf"
    SOLUTION_FILE_DEFAULT           = "solution.txt"

    config_file = None
    if len(sys.argv) > 1 and sys.argv[1].endswith(".json"):
        config_file = sys.argv[1]

    config = {}
    if config_file:
        config = load_config(config_file)
    
    java_path            = config.get("java_path",              JAVA_DEFAULT_PATH)
    jython_jar           = config.get("jython_jar",             JYTHON_DEFAULT_JAR)
    sikulix_jar          = config.get("sikulix_jar",            SIKULIX_DEFAULT_JAR)
    images_dir           = config.get("images_dir",             IMAGES_DEFAULT_DIR)
    tests_dir            = config.get("tests_dir",              TESTS_DEFAULT_DIR)
    theorical_graph_file = config.get("theorical_graph_file",   THEORICAL_GRAPH_DEFAULT_FILE)
    practical_graph_file = config.get("practical_graph_file",   PRACTICAL_GRAPH_DEFAULT_FILE)
    generate_graph       = config.get("generate_graph",         GENERATE_GRAPH_DEFAULT)
    selected_executable  = config.get("selected_executable",    SELECTED_EXECUTABLE_DEFAULT)
    executable_delay     = config.get("executable_delay",       EXECUTABLE_DELAY_DEFAULT)
    transition_delay     = config.get("transition_delay",       TRANSITION_DELAY_DEFAULT)
    debug_images         = config.get("debug_images",           DEBUG_IMAGES_DEFAULT)
    timeout              = config.get("timeout",                TIMEOUT_DEFAULT)
    initial_similarity   = config.get("initial_similarity",     INITIAL_SIMILARITY_DEFAULT)

    if initial_similarity < 0.0 or initial_similarity > 1.0:
        print(f"[ERROR] Invalid initial similarity: {initial_similarity}. Setting to default {INITIAL_SIMILARITY_DEFAULT}.")
        initial_similarity = INITIAL_SIMILARITY_DEFAULT
    min_similarity =        config.get("min_similarity", MIN_SIMILARITY_DEFAULT)
    if min_similarity < 0.0 or min_similarity > 1.0:
        print(f"[ERROR] Invalid minimum similarity: {min_similarity}. Setting to default {MIN_SIMILARITY_DEFAULT}.")
        min_similarity = MIN_SIMILARITY_DEFAULT
    similarity_step =       config.get("similarity_step", SIMILARITY_STEP_DEFAULT)
    if similarity_step < 0.0 or similarity_step > 1.0:
        print(f"[ERROR] Invalid similarity step: {similarity_step}. Setting to default {SIMILARITY_STEP_DEFAULT}.")
        similarity_step = SIMILARITY_STEP_DEFAULT
    retries =               config.get("retries", RETRIES_DEFAULT)
    if retries < 0:
        print(f"[ERROR] Invalid number of retries: {retries}. Setting to default {RETRIES_DEFAULT}.")
        retries = RETRIES_DEFAULT
    state_reset_method =    config.get("state_reset_method", STATE_RESET_METHOD_DEFAULT)
    if state_reset_method not in StateResetMethod.values():
        print(f"[ERROR] Invalid state reset method: {state_reset_method}. Setting to default {StateResetMethod.NONE}.")
        state_reset_method = StateResetMethod.NONE
    external_reset_script = config.get("external_reset_script", EXTERNAL_RESET_SCRIPT_DEFAULT)
    if state_reset_method == StateResetMethod.EXTERNAL_RESET and external_reset_script and not os.path.isfile(external_reset_script):
        print(f"[ERROR] External reset script {external_reset_script} not found.")
        sys.exit(1)
    tests_to_run  = config.get("tests_to_run", TESTS_TO_RUN_DEFAULT)
    pdf_file      = config.get("pdf_file", PDF_FILE_DEFAULT)
    solution_file = config.get("solution_file", SOLUTION_FILE_DEFAULT)

    headless = True if config_file else False

    if headless:
        app = Console(
            java_path=java_path,
            sikulix_jar=sikulix_jar,
            sikuli_script=SIKULIX_SCRIPT,
            images_dir=images_dir,
            tests_dir=tests_dir,
            theorical_graph_file=theorical_graph_file,
            practical_graph_file=practical_graph_file,
            selected_executable=selected_executable,
            generate_graph=generate_graph,
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
            sikulix_jar=sikulix_jar,
            sikuli_script=SIKULIX_SCRIPT,
            window_name=WINDOW_NAME,
            window_size=WINDOW_SIZE,
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
