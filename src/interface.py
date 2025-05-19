from app import App

import sys

import customtkinter as ctk
import tkinter.ttk as ttk
import threading

from tabs.testRunnerTab import TestRunnerTab
from tabs.settingsTab import SettingsTab
from tabs.outputTab import OutputTab
from tabs.statesTab import StatesTab

class Interface(App, ctk.CTk):
    def __init__(self,
                java_path, sikulix_jar,
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
                pdf_file,
                window_name, window_size):
        
        # ------Parameters.
        self.test_checkboxes = {}
        self.test_output_widgets = {} 
        self.jython_process = None # Jython process
        
        ctk.CTk.__init__(self)
        App.__init__(self=self,
            java_path=java_path,
            sikulix_jar=sikulix_jar,
            sikuli_script=sikuli_script,
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

        print("[INFO] Application initialized in window")
        self.stop_event = threading.Event()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.title(window_name)
        self.geometry(window_size)
        self.configure_grid()
        self.after_ids = []
        self.delay_ms_tabs = 100
        self.delay_ms_executable = 1000
        self.after_ids.append(self.after(self.delay_ms_tabs, self.create_tabs))
        self.mainloop()
 
    # ==============================================================================================
    # GENERAL
    # ==============================================================================================
         
    """
       Configure the grid layout of the main window
    """
    def configure_grid(self):
        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure(0, weight = 1)
        
    """
       Create the tabs: States and Tests
       The Tests tab is created dynamically based on the test classes found in the specified directory
    """
    def create_tabs(self):
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding = [20, 10])
        style.configure("TNotebook", tabposition = "nw")

        self.tabs_to_keep = {"States", "Generate, Run & Compare", "Settings", "Terminal"}

        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row = 0, column = 0, sticky = "nsew")

        # States tab
        self.states_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(self.states_tab, text = "States")
        #self.configure_states_tab()
        self.states_tab = StatesTab(self.states_tab, self)

        # Test Runner tab
        self.test_runner_tab = TestRunnerTab(self.tab_control, self)

        # Settings tab
        self.setting_tab = SettingsTab(self.tab_control, self)

        # Output tab
        self.output_tab = OutputTab(self.tab_control, self)

    # ==============================================================================================
    # TEST TAB
    # ==============================================================================================
 
    """
        Add a new tab for the test class
        The tab will contain a button to run the test and the needed arguments
    """
    def add_test_tab(self, test_class_name, test_class_ref):

        test_instance = test_class_ref()
        tab_name = getattr(test_instance, "name", test_class_name)
        self.test_output_widgets[tab_name] = {}

        new_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(new_tab, text=tab_name)

        label = ctk.CTkLabel(new_tab, text=f"Attributes for {tab_name}", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=10)

        attributes_frame = ctk.CTkFrame(new_tab)
        attributes_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Show the attributes of the test class
        for attr_name, attr_value in vars(test_instance).items():
            if attr_name.startswith("_"):
                continue

            # Show sets as a listbox
            if isinstance(attr_value, set):
                attr_label = ctk.CTkLabel(attributes_frame, text=f"{attr_name}:", font=ctk.CTkFont(size=12))
                attr_label.pack(anchor="w", padx=5, pady=2)
                attr_value = list(attr_value)
                attr_listbox = ctk.CTkTextbox(attributes_frame, height=100)
                attr_listbox.insert("1.0", "\n".join(map(str, attr_value)))
                attr_listbox.configure(state="disabled")
                attr_listbox.pack(fill="x", padx=5, pady=2)

                self.test_output_widgets[tab_name][attr_name] = attr_listbox
            # TODO: Add the needed arguments to run the test
            # elif isinstance(attr_value, list):
 

    # ==============================================================================================
    # TESTS RUNNER & COMPARISON TAB
    # ==============================================================================================
    
    def select_tests_dir(self, directory_path):
        self.tests_dir = directory_path
        self.test_classes = self.get_test_classes()
  
    """
        Select the images directory using a file dialog and update the entry field with the selected path
    """
    def set_images_dir(self, path):
        self.images_dir = path        
            
    """
        Returns the selected test classes for run the test.
    """
    def get_selected_test_classes(self):
        selected_test_classes = []
        if self.test_classes is not None:
            selected_test_classes = [
                test_class_ref for test_class_name, (var, test_class_ref) in self.test_checkboxes.items() if var.get()
            ]
        return selected_test_classes      

    """
        Restore the original stdout when the application is closed
    """
    def on_close(self):
        print("[INFO] Stopping all threads...")
        self.stop_event.set()

        for after_id in self.after_ids:
            try:
                self.after_cancel(after_id)
            except Exception as e:
                print(f"[WARNING] Failed to cancel event {after_id}: {e}")

        if hasattr(self, "jython_process") and self.jython_process is not None:
            print("[INFO] Terminating Jython process...")
            self.jython_process.terminate()
            self.jython_process.wait()
            print("[INFO] Jython process terminated.")

        threading.Event().wait(0.5)

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        try:
            print("[INFO] All ok, closing.")
            self.quit()
        except Exception as e:
            print(f"[WARNING] Failed to quit mainloop: {e}")

        self.destroy()
