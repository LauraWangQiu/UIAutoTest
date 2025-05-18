import os
import sys
import math

import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import graphsDef
import threading
from actionTypes import ActionType

class interface(ctk.CTk):
     
     
     
    def __init__(self, 
                  window_name, window_size,):
          
          
         super().__init__()
         self.stop_event = threading.Event()
         self.protocol("WM_DELETE_WINDOW", self.on_close)
         self.title(window_name)
         self.geometry(window_size)
         self.configure_grid()
         self.after_ids = []
         self.selected_nodes = []
         self.node_frames = []
         self.node_frames_index = 1
         self.delay_ms_tabs = 100
         self.delay_ms_executable = 1000
         self.after_ids.append(self.after(self.delay_ms_tabs, self.create_tabs))
         self.mainloop()
         
         # ------Parameters.
         self.test_checkboxes = {}
         self.test_output_widgets = {} 
         
         
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
        self.configure_states_tab()

        # Test Runner tab
        self.add_test_runner_tab()

        # Settings tab
        self.add_settings_tab()

        # Output tab
        self.add_terminal_tab()
        
        
        
    #------Creates the differents tabs:
    """
       Configure the States tab layout
    """
    def configure_states_tab(self):
        self.states_tab.grid_columnconfigure(0, weight=1)
        self.states_tab.grid_rowconfigure(0, weight=1)

        self.split_frame = ctk.CTkFrame(self.states_tab)
        self.split_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.split_frame.grid_columnconfigure(0, weight=1, minsize=300)  # left panel
        self.split_frame.grid_columnconfigure(1, weight=3)               # right panel
        self.split_frame.grid_rowconfigure(0, weight=1)

        # Left panel
        self.left_panel = ctk.CTkFrame(self.split_frame)
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_panel.grid_rowconfigure(6, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        # Left panel: title
        title_label = ctk.CTkLabel(self.left_panel, text="States Configuration", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        # Left panel: save graph button
        save_graph_button = ctk.CTkButton(
            self.left_panel, 
            text="Save Graph", 
            command=self.save_graph_to_file)
        save_graph_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        # Left panel: load graph button
        load_graph_button = ctk.CTkButton(
            self.left_panel, 
            text="Load Graph", 
            command=self.load_graph_from_dialog)
        load_graph_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        # Left panel: button to add nodes
        add_node_button = ctk.CTkButton(self.left_panel, text="Add State", command=self.add_node)
        add_node_button.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        # Left panel: button to remove nodes
        remove_node_button = ctk.CTkButton(self.left_panel, text="Remove Selected State(s)", command=self.remove_selected_nodes)
        remove_node_button.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        # Left panel: Clear button
        clear_button = ctk.CTkButton(
            self.left_panel,
            text="Clear",
            command=self.clear_graph_with_confirmation
        )
        clear_button.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        # Left panel: subpanel to show all existing nodes with scrollbar
        self.nodes_canvas = ctk.CTkCanvas(self.left_panel, bg="#2b2b2b", highlightthickness=0)
        self.nodes_canvas.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")
        self.nodes_scrollbar = ctk.CTkScrollbar(self.left_panel, orientation="vertical", command=self.nodes_canvas.yview)
        self.nodes_scrollbar.grid(row=6, column=1, sticky="ns", padx=(0, 10))
        self.nodes_canvas.configure(yscrollcommand=self.nodes_scrollbar.set)
        self.nodes_frame = ctk.CTkFrame(self.nodes_canvas)
        self.nodes_frame_id = self.nodes_canvas.create_window((0, 0), window=self.nodes_frame, anchor="nw")
        self.nodes_frame.grid_columnconfigure(0, weight=1)
        self.nodes_canvas.bind(
            "<Configure>",
            lambda e: self.nodes_canvas.itemconfig(self.nodes_frame_id, width=self.nodes_canvas.winfo_width())
        )
        self.nodes_frame.bind("<Configure>", self.update_scroll_region)
        self.nodes_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.nodes_canvas.grid_remove()
        self.nodes_scrollbar.grid_remove()

        # Right panel
        self.right_panel = ctk.CTkFrame(self.split_frame)
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        # Right panel: canvas to draw graph
        self.canva = ctk.CTkCanvas(self.right_panel, bg="white", height=400)
        self.canva.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.canva.bind("<Configure>", lambda event: self.on_canvas_resize(event)) # Resize

        self.draw_graph()
        
    """
        Select tests to run and compare results
    """  
    def add_test_runner_tab(self):
        test_runner_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(test_runner_tab, text="Generate, Run & Compare")

        # --- SCROLLABLE AREA ---
        canvas = ctk.CTkCanvas(test_runner_tab, borderwidth=0, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(test_runner_tab, orientation="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scrollable_frame = ctk.CTkFrame(canvas)
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)

        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # --- END SCROLLABLE AREA ---

        # Label for the selected executable
        exec_label = ctk.CTkLabel(scrollable_frame, text="Selected Executable:", font=ctk.CTkFont(size=12))
        exec_label.pack(anchor="w", padx=10, pady=(10, 2))

        # Entry to display the selected executable path
        self.executable_entry = ctk.CTkEntry(scrollable_frame, state="readonly", font=ctk.CTkFont(size=12))
        self.executable_entry.insert(0, "Executable: None")
        self.executable_entry.pack(fill="x", padx=10, pady=5)

        # Button to select executable
        select_executable_button = ctk.CTkButton(scrollable_frame, text="Select Executable", command=self.select_executable)
        select_executable_button.pack(padx=10, pady=5, anchor="w")

        # Label for the selected images directory
        images_label = ctk.CTkLabel(scrollable_frame, text="Selected Images Directory:", font=ctk.CTkFont(size=12))
        images_label.pack(anchor="w", padx=10, pady=(10, 2))

        # Entry to display the selected images directory
        self.images_dir_var = ctk.StringVar(value=self.images_dir)
        self.images_dir_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.images_dir_var, state="readonly", font=ctk.CTkFont(size=12))
        self.images_dir_entry.pack(fill="x", padx=10, pady=5)

        # Button to select images directory
        select_images_dir_button = ctk.CTkButton(scrollable_frame, text="Select Images Directory", command=self.select_images_dir)
        select_images_dir_button.pack(padx=10, pady=5, anchor="w")

        # Button to generate the graph from executable
        generate_graph_button = ctk.CTkButton(scrollable_frame, text="Generate Graph from Executable", command=self.generate_graph_from_executable) # TODO ES COMUN
        generate_graph_button.pack(fill="x", padx=10, pady=5)

        # Label for the selected tests directory
        tests_label = ctk.CTkLabel(scrollable_frame, text="Selected Tests Directory:", font=ctk.CTkFont(size=12))
        tests_label.pack(anchor="w", padx=10, pady=(10, 2))

        # Entry to display the selected tests directory
        self.tests_dir_var = ctk.StringVar(value=self.tests_dir)
        self.tests_dir_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.tests_dir_var, state="readonly", font=ctk.CTkFont(size=12))
        self.tests_dir_entry.pack(fill="x", padx=10, pady=5)

        # Button to select tests directory
        select_tests_dir_button = ctk.CTkButton(
            scrollable_frame,
            text="Select Tests Directory",
            command=self.select_tests_dir
        )
        select_tests_dir_button.pack(padx=10, pady=5, anchor="w")

        # Title
        title_label = ctk.CTkLabel(scrollable_frame, text="Select Tests to Run", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=10)

        # Frame for the list of tests
        self.test_list_frame = ctk.CTkFrame(scrollable_frame)
        self.test_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Label for the selected practical graph file
        practical_graph_label = ctk.CTkLabel(scrollable_frame, text="Selected Practical Graph File:", font=ctk.CTkFont(size=12))
        practical_graph_label.pack(anchor="w", padx=10, pady=(10, 2))

        # Entry to display the selected practical graph file
        self.practical_graph_var = ctk.StringVar(value=self.practical_graph_file)
        self.practical_graph_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.practical_graph_var, state="readonly", font=ctk.CTkFont(size=12))
        self.practical_graph_entry.pack(fill="x", padx=10, pady=5)

        # Button to select practical graph file
        select_practical_graph_button = ctk.CTkButton(
            scrollable_frame,
            text="Select Practical Graph File",
            command=self.select_practical_graph_file
        )
        select_practical_graph_button.pack(padx=10, pady=5, anchor="w")

        # Label for the selected theorical graph file
        theorical_graph_label = ctk.CTkLabel(scrollable_frame, text="Selected Theoretical Graph File:", font=ctk.CTkFont(size=12))
        theorical_graph_label.pack(anchor="w", padx=10, pady=(10, 2))

        # Entry to display the selected theorical graph file
        self.theorical_graph_var = ctk.StringVar(value=self.theorical_graph_file)
        self.theorical_graph_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.theorical_graph_var, state="readonly", font=ctk.CTkFont(size=12))
        self.theorical_graph_entry.pack(fill="x", padx=10, pady=5)

        select_theorical_graph_button = ctk.CTkButton(
            scrollable_frame,
            text="Select Theorical Graph File",
            command=self.select_theorical_graph_file
        )
        select_theorical_graph_button.pack(padx=10, pady=5, anchor="w")

        # Run tests button
        run_button = ctk.CTkButton(scrollable_frame, text="Run Tests", command=self.run_tests) # TODO COMUN
        run_button.pack(fill="x", padx=10, pady=5)

        # Compare button
        compare_button = ctk.CTkButton(scrollable_frame, text="Compare Graphs", command=self.compare) # TODO COMUN
        compare_button.pack(fill="x", padx=10, pady=5)

        # Button to Generate PDF
        generate_pdf_button = ctk.CTkButton(scrollable_frame, text="Generate PDF", command=lambda: self.create_PDF(self.pdf_file)) # TODO COMUN
        generate_pdf_button.pack(fill="x", padx=10, pady=5)
        
    def add_settings_tab(self):
        settings_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(settings_tab, text="Settings")

        # --- SCROLLABLE AREA ---
        canvas = ctk.CTkCanvas(settings_tab, borderwidth=0, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(settings_tab, orientation="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scrollable_frame = ctk.CTkFrame(canvas)
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(window_id, width=event.width)

        scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # --- END SCROLLABLE AREA ---

        # Ahora pon los widgets dentro de scrollable_frame en vez de settings_tab:
        java_label = ctk.CTkLabel(scrollable_frame, text="Java Path:", font=ctk.CTkFont(size=12))
        java_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.java_path_var = ctk.StringVar(value=self.java_path if self.java_path else "java")
        java_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.java_path_var, width=400)
        java_entry.pack(fill="x", padx=10, pady=2)
        java_button = ctk.CTkButton(scrollable_frame, text="Select Java Executable", command=self.select_java_path)
        java_button.pack(padx=10, pady=5, anchor="w")

        sikulix_label = ctk.CTkLabel(scrollable_frame, text="SikuliX API Jar Path:", font=ctk.CTkFont(size=12))
        sikulix_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.sikulix_jar_var = ctk.StringVar(value=self.sikulix_jar)
        sikulix_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.sikulix_jar_var, width=400)
        sikulix_entry.pack(fill="x", padx=10, pady=2)
        sikulix_button = ctk.CTkButton(scrollable_frame, text="Select SikuliX Jar", command=self.select_sikulix_jar)
        sikulix_button.pack(padx=10, pady=5, anchor="w")

        jython_label = ctk.CTkLabel(scrollable_frame, text="Jython Jar Path:", font=ctk.CTkFont(size=12))
        jython_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.jython_jar_var = ctk.StringVar(value=self.jython_jar)
        jython_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.jython_jar_var, width=400)
        jython_entry.pack(fill="x", padx=10, pady=2)
        jython_button = ctk.CTkButton(scrollable_frame, text="Select Jython Jar", command=self.select_jython_jar)
        jython_button.pack(padx=10, pady=5, anchor="w")

        practical_graph_label = ctk.CTkLabel(scrollable_frame, text="Practical Graph File to Export:", font=ctk.CTkFont(size=12))
        practical_graph_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.export_practical_graph_var = ctk.StringVar(value=self.practical_graph_file)
        self.export_practical_graph_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.export_practical_graph_var, width=400)
        self.export_practical_graph_entry.pack(fill="x", padx=10, pady=2)
        def on_export_practical_graph_change(*args):
            self.practical_graph_file = self.export_practical_graph_var.get()
        self.export_practical_graph_var.trace_add("write", lambda *args: on_export_practical_graph_change())

        # Executable Delay
        executable_delay_label = ctk.CTkLabel(scrollable_frame, text="Executable Delay (s):", font=ctk.CTkFont(size=12))
        executable_delay_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.executable_delay_var = ctk.StringVar(value=str(self.executable_delay))
        executable_delay_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.executable_delay_var, width=100)
        executable_delay_entry.pack(fill="x", padx=10, pady=2)
        def on_executable_delay_change(*args):
            value = self.executable_delay_var.get()
            if value.strip() == "":
                return
            try:
                self.executable_delay = int(value)
            except ValueError:
                pass
        self.executable_delay_var.trace_add("write", lambda *args: on_executable_delay_change())

        # Transition Delay
        transition_delay_label = ctk.CTkLabel(scrollable_frame, text="Transition Delay (s):", font=ctk.CTkFont(size=12))
        transition_delay_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.transition_delay_var = ctk.StringVar(value=str(self.transition_delay))
        transition_delay_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.transition_delay_var, width=100)
        transition_delay_entry.pack(fill="x", padx=10, pady=2)
        def on_transition_delay_change(*args):
            value = self.transition_delay_var.get()
            if value.strip() == "":
                return
            try:
                self.transition_delay = int(value)
            except ValueError:
                pass
        self.transition_delay_var.trace_add("write", lambda *args: on_transition_delay_change())

        # Debug Images (checkbox)
        self.debug_images_var = ctk.BooleanVar(value=self.debug_images)
        debug_images_checkbox = ctk.CTkCheckBox(scrollable_frame, text="Enable Debug Images", variable=self.debug_images_var)
        debug_images_checkbox.pack(anchor="w", padx=10, pady=(10, 2))
        def on_debug_images_change(*args):
            self.debug_images = self.debug_images_var.get()
        self.debug_images_var.trace_add("write", lambda *args: on_debug_images_change())

        # Timeout
        timeout_label = ctk.CTkLabel(scrollable_frame, text="Timeout (s):", font=ctk.CTkFont(size=12))
        timeout_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.timeout_var = ctk.StringVar(value=str(self.timeout))
        timeout_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.timeout_var, width=100)
        timeout_entry.pack(fill="x", padx=10, pady=2)
        def on_timeout_change(*args):
            value = self.timeout_var.get()
            if value.strip() == "":
                return
            try:
                self.timeout = int(value)
            except ValueError:
                pass
        self.timeout_var.trace_add("write", lambda *args: on_timeout_change())

        # Initial Similarity
        initial_similarity_label = ctk.CTkLabel(scrollable_frame, text="Initial Similarity (0-1):", font=ctk.CTkFont(size=12))
        initial_similarity_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.initial_similarity_var = ctk.StringVar(value=str(self.initial_similarity))
        initial_similarity_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.initial_similarity_var, width=100)
        initial_similarity_entry.pack(fill="x", padx=10, pady=2)
        def on_initial_similarity_change(*args):
            value = self.initial_similarity_var.get()
            if value.strip() == "":
                return
            try:
                val = float(value)
                if 0 <= val <= 1:
                    self.initial_similarity = val
            except ValueError:
                pass
        self.initial_similarity_var.trace_add("write", lambda *args: on_initial_similarity_change())

        # Min Similarity
        min_similarity_label = ctk.CTkLabel(scrollable_frame, text="Min Similarity (0-1):", font=ctk.CTkFont(size=12))
        min_similarity_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.min_similarity_var = ctk.StringVar(value=str(self.min_similarity))
        min_similarity_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.min_similarity_var, width=100)
        min_similarity_entry.pack(fill="x", padx=10, pady=2)
        def on_min_similarity_change(*args):
            value = self.min_similarity_var.get()
            if value.strip() == "":
                return
            try:
                val = float(value)
                if 0 <= val <= 1:
                    self.min_similarity = val
            except ValueError:
                pass
        self.min_similarity_var.trace_add("write", lambda *args: on_min_similarity_change())

        # Similarity Step
        similarity_step_label = ctk.CTkLabel(scrollable_frame, text="Similarity Step (0-1):", font=ctk.CTkFont(size=12))
        similarity_step_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.similarity_step_var = ctk.StringVar(value=str(self.similarity_step))
        similarity_step_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.similarity_step_var, width=100)
        similarity_step_entry.pack(fill="x", padx=10, pady=2)
        def on_similarity_step_change(*args):
            value = self.similarity_step_var.get()
            if value.strip() == "":
                return
            try:
                val = float(value)
                if 0 <= val <= 1:
                    self.similarity_step = val
            except ValueError:
                pass
        self.similarity_step_var.trace_add("write", lambda *args: on_similarity_step_change())

        # Retries
        retries_label = ctk.CTkLabel(scrollable_frame, text="Retries:", font=ctk.CTkFont(size=12))
        retries_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.retries_var = ctk.StringVar(value=str(self.retries))
        retries_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.retries_var, width=100)
        retries_entry.pack(fill="x", padx=10, pady=2)
        def on_retries_change(*args):
            value = self.retries_var.get()
            if value.strip() == "":
                return
            try:
                self.retries = int(value)
            except ValueError:
                pass
        self.retries_var.trace_add("write", lambda *args: on_retries_change())

        # Solution File
        solution_label = ctk.CTkLabel(scrollable_frame, text="Solution File:", font=ctk.CTkFont(size=12))
        solution_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.solution_var = ctk.StringVar(value=self.solution_file)
        self.solution_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.solution_var, width=400)
        self.solution_entry.pack(fill="x", padx=10, pady=2)
        def on_solution_change(*args):
            self.solution_file = self.solution_var.get()
        self.solution_var.trace_add("write", lambda *args: on_solution_change())

        # PDF Diff Export File Name
        pdf_route_label = ctk.CTkLabel(scrollable_frame, text="PDF Output File:", font=ctk.CTkFont(size=12))
        pdf_route_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.pdf_route_var = ctk.StringVar(value=self.pdf_file)
        self.pdf_route_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.pdf_route_var, width=400)
        self.pdf_route_entry.pack(fill="x", padx=10, pady=2)
        def on_pdf_route_change(*args):
            self.pdf_file = self.pdf_route_var.get()
        self.pdf_route_var.trace_add("write", lambda *args: on_pdf_route_change())
        
        # State Reset Method
        state_reset_label = ctk.CTkLabel(scrollable_frame, text="State Reset Method:", font=ctk.CTkFont(size=12))
        state_reset_label.pack(anchor="w", padx=10, pady=(10, 2))
        reset_methods = [v for k, v in vars(StateResetMethod).items() if isinstance(v, str) and not k.startswith("__")]
        self.state_reset_method_var = ctk.StringVar(value=self.state_reset_method)
        state_reset_menu = ctk.CTkOptionMenu(
            scrollable_frame,
            values=reset_methods,
            variable=self.state_reset_method_var
        )
        state_reset_menu.pack(fill="x", padx=10, pady=2)

        # Space to select the external reset script if the method is EXTERNAL_RESET
        self.external_reset_script_var = ctk.StringVar(value=self.external_reset_script)
        self.external_reset_script_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.external_reset_script_var, width=400)
        def select_external_reset_script():
            file_path = filedialog.askopenfilename(
                title="Select External Reset Script",
                filetypes=[("Executables", "*.exe;*.bat;*.sh;*.py"), ("All Files", "*.*")]
            )
            if file_path:
                self.external_reset_script_var.set(file_path)
                self.external_reset_script = file_path
        self.external_reset_script_button = ctk.CTkButton(scrollable_frame, text="Select External Reset Script", command=select_external_reset_script)

        def update_external_reset_visibility(*args):
            self.state_reset_method = self.state_reset_method_var.get()
            if self.state_reset_method == StateResetMethod.EXTERNAL_RESET:
                self.external_reset_script_entry.pack(fill="x", padx=10, pady=2)
                self.external_reset_script_button.pack(padx=10, pady=2, anchor="w")
            else:
                self.external_reset_script_entry.pack_forget()
                self.external_reset_script_button.pack_forget()
        self.state_reset_method_var.trace_add("write", update_external_reset_visibility)
        self.external_reset_script_var.trace_add("write", lambda *args: setattr(self, "external_reset_script", self.external_reset_script_var.get()))
        update_external_reset_visibility()
        
    """
        Add a terminal tab to display console output.
    """
    def add_terminal_tab(self):
        terminal_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(terminal_tab, text="Terminal")

        # Create a ScrolledText widget for the terminal output
        self.terminal_output = ScrolledText(terminal_tab, wrap="word", state="disabled", height=20)
        self.terminal_output.pack(fill="both", expand=True, padx=10, pady=10)

        # Redirect stdout and stderr to the terminal output
        sys.stdout = self.TextRedirector(self.terminal_output)
        sys.stderr = self.TextRedirector(self.terminal_output)
 
    def save_graph_to_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save graph to file"
        )
        if file_path:
            self.graph_io.write_graph(self.images_dir, file_path, self.graph) 
        
    def load_graph_from_dialog(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Load graph from file"
        )
        if file_path:
            self.clear_graph()
            self.graph = self.graph_io.load_graph(file_path, self.images_dir)
            if self.graph is None:
                print("[ERROR] Graph not loaded.")
                return
            self.node_frames_index = len(self.graph.nodes) + 1
            
            # Create frames for each node in the loaded graph
            for idx, node in enumerate(self.graph.nodes, 1):
                self.create_node_frame(node, idx)
            # Create the transitions list for each node
            for node in self.graph.nodes:
                self.update_transitions_list(node)
            self.draw_graph()
            self.nodes_canvas.grid()
            self.nodes_scrollbar.grid()
            self.update_scroll_region()  
        
    """
        Clear the entire graph and all nodes
    """
    def clear_graph_with_confirmation(self):
        confirm = messagebox.askyesno(
            title="Confirm Deletion",
            message="Are you sure you want to delete the entire graph? This action cannot be undone"
        )
        if confirm:
            self.clear_graph()
            
    """
        Handle mouse wheel scrolling for the canvas
    """
    def update_scroll_region(self, event=None):
        self.nodes_canvas.configure(scrollregion=self.nodes_canvas.bbox("all"))  
            
    """
        Handle mouse wheel scrolling for the canvas
    """
    def on_mouse_wheel(self, event):
        self.nodes_canvas.yview_scroll(-1 * (event.delta // 120), "units")       
            
    """
        Handle the canvas resize event to redraw the graph
    """
    def on_canvas_resize(self, event):
        self.draw_graph()        
            
    """
        Draw the graph on the canvas
        This function calculates the positions of the nodes and draws them along with the transitions
    """
    def draw_graph(self):
        self.canva.delete("all")
        node_positions = {}
        width = self.canva.winfo_width() or 600
        height = self.canva.winfo_height() or 400
    
        num_nodes = len(self.graph.nodes)
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2  
    
        for i, node in enumerate(self.graph.nodes):
            angle = (2 * math.pi / num_nodes) * i
            x = center_x + int(radius * 0.8 * math.cos(angle))
            y = center_y + int(radius * 0.8 * math.sin(angle))
            node_positions[node] = (x, y)
    
        # Draw nodes
        node_radius = 20
        for node, (x, y) in node_positions.items():
            self.draw_node(node, x, y, node_radius)
    
        # Draw transitions
        for node in self.graph.nodes:
            x1, y1 = node_positions[node]
            transition_count = {}
    
            for transition in node.transitions:
                x2, y2 = node_positions[transition.destination]
    
                # Count the number of transitions between the same pair of nodes
                key = (node, transition.destination)
                if key not in transition_count:
                    transition_count[key] = 0
                transition_count[key] += 1
    
                # Offset for multiple edges
                offset = transition_count[key] * 10  # Adjust the offset as needed
    
                # Adjust positions for multiple edges
                if node == transition.destination:  # Self-loop
                    self.draw_transition(x1, y1, x1, y1, transition.action, transition, is_self_loop=True, offset=node_radius + 10)
                else:
                    dx = x2 - x1
                    dy = y2 - y1
                    distance = math.sqrt(dx**2 + dy**2)
    
                    # Perpendicular offset for multiple edges
                    perp_dx = -dy / distance * offset
                    perp_dy = dx / distance * offset
    
                    x1_adjusted = x1 + (dx / distance) * node_radius + perp_dx
                    y1_adjusted = y1 + (dy / distance) * node_radius + perp_dy
                    x2_adjusted = x2 - (dx / distance) * node_radius + perp_dx
                    y2_adjusted = y2 - (dy / distance) * node_radius + perp_dy

                    self.draw_transition(x1_adjusted, y1_adjusted, x2_adjusted, y2_adjusted, transition.action, transition)           
            
    """
        Select an executable file using a file dialog and update the entry field with the selected path
    """
    def select_executable(self):
        file_path = filedialog.askopenfilename(
            title="Select Executable",
            filetypes=[("Executables", "*.exe"), ("All Files", "*.*")]
        )
        if file_path:
            self.selected_executable = file_path
            print(f"Selected executable: {self.selected_executable}")

            self.executable_entry.configure(state="normal")
            self.executable_entry.delete(0, "end")
            self.executable_entry.insert(0, self.selected_executable)
            self.executable_entry.configure(state="readonly")        
            
    """
        Select the images directory using a file dialog and update the entry field with the selected path
    """
    def select_images_dir(self):
        directory_path = filedialog.askdirectory(
            title="Select Images Directory"
        )
        if directory_path:
            self.images_dir = directory_path
            self.images_dir_var.set(self.images_dir)
            print(f"Selected images directory: {self.images_dir}")        
            
    """
        Select the theorical graph file using a file dialog and update the entry field with the selected path
    """
    def select_theorical_graph_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Theoretical Graph File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.theorical_graph_file = file_path
            self.theorical_graph_var.set(self.theorical_graph_file)
            print(f"[INFO] Theoretical graph file set to: {file_path}")        
            
    """
        Select the theorical graph file using a file dialog and update the entry field with the selected path
    """
    def select_practical_graph_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Practical Graph File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.practical_graph_file = file_path
            self.practical_graph_var.set(file_path)
            print(f"[INFO] Practical graph file for tests set to: {file_path}")        
            
            
    def select_tests_dir(self):
        directory_path = filedialog.askdirectory(
            title = "Select Tests Directory"
        )
        if directory_path:
            self.tests_dir = directory_path
            self.tests_dir_var.set(self.tests_dir)
            print(f"Selected tests directory: {self.tests_dir}")
            self.test_classes = self.get_test_classes() # TODO COMUN
            self.populate_test_list()
            self.reload_test_tabs()       
            
    def select_java_path(self):
        file_path = filedialog.askopenfilename(
            title="Select Java Executable",
            filetypes=[("Java Executable", "java.exe;java"), ("All Files", "*.*")]
        )
        if file_path:
            self.java_path_var.set(file_path)
            self.java_path = file_path
            print(f"[INFO] Java path set to: {file_path}")        
            
    def select_sikulix_jar(self):
        file_path = filedialog.askopenfilename(
            title="Select SikuliX API Jar",
            filetypes=[("Jar Files", "*.jar"), ("All Files", "*.*")]
        )
        if file_path:
            self.sikulix_jar_var.set(file_path)
            self.sikulix_jar = file_path
            print(f"[INFO] SikuliX jar path set to: {file_path}")        
            
    def select_jython_jar(self):
        file_path = filedialog.askopenfilename(
            title="Select Jython Jar",
            filetypes=[("Jar Files", "*.jar"), ("All Files", "*.*")]
        )
        if file_path:
            self.jython_jar_var.set(file_path)
            self.jython_jar = file_path
            print(f"[INFO] Jython jar path set to: {file_path}")        
            
    """
    Redirect stdout to a ScrolledText widget
    """
    class TextRedirector:
        def __init__(self, text_widget):
            self.text_widget = text_widget

        """
            Write the message to the ScrolledText widget
        """
        def write(self, message):
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", message)
            self.text_widget.configure(state="disabled")
            self.text_widget.see("end")

            sys.__stdout__.write(message)

        """
            Flush the output buffer
        """
        def flush(self):
            pass        
            
    """
        Clear the entire graph and all nodes
    """
    def clear_graph(self):
        if self.graph is None:
            print("[INFO] No graph to clear")
            return
        
        self.graph.clear()
        for frame, edit_frame in self.node_frames:
            frame.destroy()
            if edit_frame:
                edit_frame.destroy()
        self.node_frames.clear()

        self.nodes_canvas.grid_remove()
        self.nodes_scrollbar.grid_remove()

        self.node_frames_index = 1

        self.draw_graph()        
      
    """
        Create a frame for each node in the graph

        Atributes:
            node (Node): The node to create the frame for
            index (int): The index of the node in the graph
    """      
    def create_node_frame(self, node, index):
        frame = ctk.CTkFrame(self.nodes_frame, corner_radius=10)
        frame.grid(row=index, column=0, padx=10, pady=5, sticky="ew")
        frame._name = str(id(node))
        
        header_frame = ctk.CTkFrame(frame, corner_radius=0)
        header_frame.pack(fill="x", padx=5, pady=5)

        node.checkbox_var = ctk.BooleanVar(value=False)

        def on_checkbox_change():
            if node.checkbox_var.get():
                if node not in self.selected_nodes:
                    self.selected_nodes.append(node)
                    print("[INFO] Node " + node.name + " added to selected_nodes")
            else:
                if node in self.selected_nodes:
                    self.selected_nodes.remove(node)
                    print("[INFO] Node " + node.name + " removed from selected_nodes")

        checkbox = ctk.CTkCheckBox(header_frame, variable=node.checkbox_var, text="", command=on_checkbox_change)
        checkbox.pack(side="left", padx=5)
        
        name_label = ctk.CTkLabel(header_frame, text=node.name, font=ctk.CTkFont(size=14))
        name_label.pack(side="left", padx=5)

        name_label.bind("<Button-1>", lambda e: self.make_label_editable(name_label, node))

        toggle_button = ctk.CTkButton(
            header_frame, text="▼", width=30, command=lambda: self.toggle_node_frame(frame, toggle_button)
        )
        toggle_button.pack(side="right", padx=5)

        edit_frame = ctk.CTkFrame(frame, corner_radius=10)
        edit_frame.pack(fill="x", padx=5, pady=5)
        edit_frame.grid_columnconfigure(0, weight=1)
        edit_frame.pack_forget()

        connections_label = ctk.CTkLabel(edit_frame, text="Transitions:")
        connections_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        transitions_list_frame = ctk.CTkFrame(edit_frame)
        transitions_list_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        transitions_list_frame.grid_columnconfigure(0, weight=1)
        transitions_list_frame.grid_remove()

        node.transitions_list_frame = transitions_list_frame

        # Add "+" button
        add_button = ctk.CTkButton(edit_frame, text="+", width=30, command=lambda n=node: self.add_connection(n))
        add_button.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        # Add "-" button
        remove_button = ctk.CTkButton(edit_frame, text="-", width=30, command=lambda n=node: self.delete_last_transition(node))
        remove_button.grid(row=3, column=1, padx=5, pady=5, sticky="e")

        # Add "Select Image" button
        select_image_button = ctk.CTkButton(edit_frame, text="Select Image", command=lambda n=node: self.select_image_for_node(n))
        select_image_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Label to display the selected image path
        image_label_text = f"Image: {os.path.basename(node.image)}" if hasattr(node, "image") and node.image else "No image selected"
        node.image_label = ctk.CTkLabel(edit_frame, text=image_label_text, font=ctk.CTkFont(size=12))
        node.image_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.node_frames.append((frame, edit_frame))

        self.update_transitions_list(node)        
            
    """
        Update the transitions list for a given node

        Atributes:
            node (Node): The node whose transitions list needs to be updated
    """
    def update_transitions_list(self, node):
        for widget in node.transitions_list_frame.winfo_children():
            widget.destroy()

        for i, transition in enumerate(node.transitions):
            transition_frame = ctk.CTkFrame(node.transitions_list_frame)
            transition_frame.pack(fill="x", padx=5, pady=2)

            transition_label = ctk.CTkLabel(transition_frame, text=f"→ {transition.destination.name}")
            transition_label.pack(side="left", padx=5, pady=2)

            if i > 0:
                move_up_button = ctk.CTkButton(
                    transition_frame, text="↑", width=30,
                    command=lambda idx=i: self.move_transition_up(node, idx)
                )
                move_up_button.pack(side="right", padx=2)

            if i < len(node.transitions) - 1:
                move_down_button = ctk.CTkButton(
                    transition_frame, text="↓", width=30,
                    command=lambda idx=i: self.move_transition_down(node, idx)
                )
                move_down_button.pack(side="right", padx=2)

        if node.transitions:
            node.transitions_list_frame.grid()
        else:
            node.transitions_list_frame.grid_remove()                      
            
    """
        Draws a transition with text and images
    """
    def draw_transition(self, x1, y1, x2, y2, action_text, transition, is_self_loop=False, offset=0):
        if is_self_loop:
            self.canva.create_arc(
                x1 - offset, y1 - offset, x1 + offset, y1 + offset,
                start=0, extent=300, style="arc", outline="black", width=2
            )
            text_x, text_y = x1, y1 - offset - 20
        else:
            self.canva.create_line(x1, y1, x2, y2, arrow="last", fill="black")
            text_x, text_y = (x1 + x2) // 2, (y1 + y2) // 2

        self.canva.create_text(text_x, text_y, text=action_text, font=("Arial", 10), fill="black")

        if action_text == "DRAG_AND_DROP":
            transition.drag_image_tk = self.draw_image(transition.drag_image, text_x - 15, text_y - 20)
            transition.drop_image_tk = self.draw_image(transition.drop_image, text_x + 15, text_y - 20)
        elif action_text in ["CLICK", "DOUBLE_CLICK", "CLICK_AND_TYPE"]:
            transition.tk_image = self.draw_image(transition.image, text_x, text_y - 20)        
            
    """
        Populate the test list with checkboxes for each test class found in the specified directory
        Each checkbox is associated with a test class reference
    """
    def populate_test_list(self):
        for widget in self.test_list_frame.winfo_children():
            widget.destroy()

        # Add each test as a checkbox
        for test_class_name, test_class_ref in self.test_classes:
            var = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(self.test_list_frame, text=test_class_name, variable=var)
            checkbox.pack(anchor="w", padx=5, pady=2)
            self.test_checkboxes[test_class_name] = (var, test_class_ref)        
            
    def reload_test_tabs(self):
        for i in reversed(range(self.tab_control.index("end"))):
            tab_text = self.tab_control.tab(i, "text")
            if tab_text not in self.tabs_to_keep:
                self.tab_control.forget(i)
        # Add new tests
        for test_class_name, test_class_ref in self.test_classes:
            self.add_test_tab(test_class_name, test_class_ref)        
            
    """
        Make the label editable by replacing it with an entry field
        When the user presses Enter or clicks outside the entry, the new text is saved and the label is updated
        The entry field is destroyed after saving the text
    """
    def make_label_editable(self, label, node):
        current_text = label.cget("text")

        entry = ctk.CTkEntry(label.master, font=label.cget("font"))
        entry.insert(0, current_text)
        entry.pack(fill="x", padx=5, pady=5)

        label.pack_forget()

        def save_text(event=None):
            new_text = entry.get()
            if new_text.strip():
                label.configure(text=new_text)
                self.update_node_name(node, new_text)
            entry.destroy()
            label.pack(fill="x", padx=5, pady=5)

        entry.bind("<Return>", save_text)
        entry.bind("<FocusOut>", save_text)
        entry.focus_set()        
            
    """
        Toggle the visibility of the node frame and update the button text accordingly

        Atributes:
            frame (CTkFrame): The frame to toggle.
            toggle_button (CTkButton): The button that toggles the frame visibility
    """
    def toggle_node_frame(self, frame, toggle_button):
        for f, edit_frame in self.node_frames:
            if f == frame:
                if edit_frame.winfo_ismapped():
                    edit_frame.pack_forget()
                    toggle_button.configure(text="▼")
                else:
                    edit_frame.pack(fill="x", padx=5, pady=5)
                    toggle_button.configure(text="▲")        

    """
        Add a connection to a node by creating a dropdown menu with available nodes
        The user can select a node from the menu to create a transition
        If the node already has a menu, it prompts the user to select a transition from the current menu before adding a new one

        Atributes:
            node (Node): The node to which the transition is being added
    """
    def add_connection(self, node):
        if hasattr(node, "add_transition_menu"):
            print("[INFO] Please select a transition from the current menu before adding a new one")
            return

        for transition in node.transitions:
            if not ActionType.is_valid_action(transition.action):
                print("[INFO] Please select a valid action type for all transitions before adding a new one.")
                return
            if ActionType.requires_image(transition.action) and not transition.image:
                print(f"[INFO] Please select an image for the {transition.action} transition before adding a new one.")
                return
            if ActionType.requires_drag_and_drop_images(transition.action) and (
                not transition.drag_image or not transition.drop_image
            ):
                print("[INFO] Please select both drag and drop images for the DRAG_AND_DROP transition before adding a new one.")
                return
        
        available_nodes = [n.name for n in self.graph.nodes]
        if not available_nodes:
            print("[INFO] No available nodes to connect")
            return

        node.transitions_list_frame.grid()

        add_transition_menu = ctk.CTkOptionMenu(
            node.transitions_list_frame,
            values=available_nodes,
            command=lambda selected: self.add_connection_to_node(node, selected)
        )
        add_transition_menu.pack(fill="x", padx=5, pady=5)

        node.add_transition_menu = add_transition_menu

    """
        Delete the last transition from the list of transitions for a given node
        If the node has no transitions left, the transitions list frame is hidden
        If the node has an add transition menu, it is destroyed
        If the node has transitions, it deletes the last one and updates the transitions list
    """
    def delete_last_transition(self, node):
        if hasattr(node, "add_transition_menu"):
            node.add_transition_menu.destroy()
            delattr(node, "add_transition_menu")

            if not node.transitions:
                node.transitions_list_frame.grid_remove()

            return

        if node.transitions:
            node.transitions.pop()
            self.update_transitions_list(node)

            if not node.transitions:
                node.transitions_list_frame.grid_remove()

        self.draw_graph()

    """
        Select an image for the node using a file dialog
    """
    def select_image_for_node(self, node):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")]
        )
        if file_path:
            node.image = file_path
            print(f"[INFO] Selected image for node {node.name}: {file_path}")
            node.image_label.configure(text=f"Image: {os.path.basename(file_path)}")

            self.draw_graph()

    """
        Move a transition up in the list of transitions for a given node
        This function swaps the transition with the one above it in the list

        Atributes:
            node (Node): The node whose transition list needs to be updated
            index (int): The index of the transition to move up
    """
    def move_transition_up(self, node, index):
        if index > 0:
            node.transitions[index], node.transitions[index - 1] = node.transitions[index - 1], node.transitions[index]
            self.update_transitions_list(node)
            self.draw_graph()

    """
        Move a transition down in the list of transitions for a given node
        This function swaps the transition with the one below it in the list
        
        Atributes:
            node (Node): The node whose transition list needs to be updated
            index (int): The index of the transition to move down
    """
    def move_transition_down(self, node, index):
        if index < len(node.transitions) - 1:
            node.transitions[index], node.transitions[index + 1] = node.transitions[index + 1], node.transitions[index]
            self.update_transitions_list(node)
            self.draw_graph()

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

    """
        Update the name of a node in the graph and redraw the graph

        Atributes:
            node (Node): The node to update
            new_name (str): The new name for the node
        If the new name is empty, it does not update the node name
    """
    def update_node_name(self, node, new_name):
        if self.graph.update_node_name(node, new_name):
            self.draw_graph()

    """
        Select images for the transition based on the selected action type
    """
    def select_images_for_transition(self, transition):
        if transition.action == "NONE" or not transition.action:
            print("[INFO] Please select a valid action type before selecting images.")
            return
        
        if ActionType.requires_image(transition.action):
            file_path = filedialog.askopenfilename(
                title=f"Select Image for {transition.action}",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")]
            )
            if file_path:
                transition.image = file_path
                print(f"[INFO] Image for {transition.action} set to: {file_path}")
            else:
                print(f"[INFO] No image selected for {transition.action} transition.")
                return

        elif ActionType.requires_drag_and_drop_images(transition.action):
            drag_image_path = filedialog.askopenfilename(
                title="Select Drag Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")]
            )
            if drag_image_path:
                transition.drag_image = drag_image_path
                print(f"[INFO] Drag Image set to: {drag_image_path}")
            else:
                print("[INFO] No drag image selected for DRAG_AND_DROP transition.")
                return

            drop_image_path = filedialog.askopenfilename(
                title="Select Drop Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"), ("All Files", "*.*")]
            )
            if drop_image_path:
                transition.drop_image = drop_image_path
                print(f"[INFO] Drop Image set to: {drop_image_path}")
            else:
                print("[INFO] No drop image selected for DRAG_AND_DROP transition.")
                return
        
        if hasattr(transition, "input_type_frame"):
            transition.input_type_frame.destroy()
            del transition.input_type_frame

        self.draw_graph()

    """
    """
    def create_input_type_menu(self, node, transition):
        input_type_frame = ctk.CTkFrame(node.transitions_list_frame)
        input_type_frame.pack(fill="x", padx=5, pady=5)

        transition.input_type_frame = input_type_frame

        input_types = [
            value for name, value in vars(ActionType).items()
            if not name.startswith("__") and not callable(value)
        ]

        input_type_menu = ctk.CTkOptionMenu(
            input_type_frame,
            values=input_types,
            command=lambda selected: self.on_input_type_selected(transition, selected)
        )
        input_type_menu.pack(side="left", padx=5, pady=5)

        select_images_button = ctk.CTkButton(
            input_type_frame,
            text="Select Images",
            command=lambda: self.select_images_for_transition(transition)
        )
        select_images_button.pack(side="right", padx=5, pady=5)

    """
        Select the input type for a transition
    """
    def on_input_type_selected(self, transition, selected_input_type):
        transition.action = selected_input_type
        print(f"[INFO] Transition action set to: {selected_input_type}")

    """
        Draw an image on the canvas at the specified coordinates
    """
    def draw_image(self, image_path, x, y, size=(20, 20)):
        try:
            if os.path.exists(image_path):
                image = Image.open(image_path)
                resized_image = image.resize(size, Image.Resampling.LANCZOS)
                image_tk = ImageTk.PhotoImage(resized_image)
                self.canva.create_image(x, y, image=image_tk)
                return image_tk
        except Exception as e:
            print(f"[WARNING] Could not load image {image_path}: {e}")
        return None

    """
        Draw a node with an image or a circle
    """
    def draw_node(self, node, x, y, radius):
        if hasattr(node, "image") and node.image:
            node.tk_image = self.draw_image(node.image, x, y, size=(radius * 2, radius * 2))
        else:
            self.canva.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill="lightblue", outline="black", width=2, tags=node.name
            )
        self.canva.create_text(x, y, text=node.name, font=("Arial", 12), tags=node.name)

    """
        Remove the selected nodes from the graph and update the graph
    """
    def remove_selected_nodes(self):
        nodes_to_remove = [node for node in self.graph.nodes if getattr(node, "checkbox_var", None) and node.checkbox_var.get()]
        
        if not nodes_to_remove:
            print("[INFO] No states selected for removal")
            return

        for node in nodes_to_remove:
            self.graph.remove_node(node)
            print(f"[INFO] Removed node: {node.name}")

            for frame, edit_frame in self.node_frames:
                if frame._name == str(id(node)):
                    frame.destroy()
                    if edit_frame:
                        edit_frame.destroy()

        self.node_frames = [(frame, edit_frame) for frame, edit_frame in self.node_frames if frame.winfo_exists()]
        self.selected_nodes = [node for node in self.selected_nodes if node not in nodes_to_remove]

        for node in self.graph.nodes:
            node.transitions = [t for t in node.transitions if t.destination not in nodes_to_remove]
            self.update_transitions_list(node)

            if not node.transitions:
                node.transitions_list_frame.grid_remove()

        if len(self.graph.nodes) == 0:
            self.nodes_canvas.grid_remove()
            self.nodes_scrollbar.grid_remove()
            self.node_frames_index = 1

        self.draw_graph()

    """
        Add a connection to a node by creating a transition to the selected node
        This function is called when the user selects a node from the dropdown menu

        Atributes:
            node (Node): The node to which the transition is being added
            selected_name (str): The name of the selected node from the dropdown menu
        If the selected node already has a transition to the current node, it does not add it again
    """
    def add_connection_to_node(self, node, selected_name):
        for n in self.graph.nodes:
            if n.name == selected_name:
                new_transition = Transition(n)
                node.add_transition(new_transition)
                break

        self.update_transitions_list(node)

        if hasattr(node, "add_transition_menu"):
            node.add_transition_menu.destroy()
            delattr(node, "add_transition_menu")

        self.create_input_type_menu(node, new_transition)

        self.draw_graph()        

    """
        Add a new node to the graph and create its corresponding UI elements
    """
    def add_node(self):
        node_name = "State " + str(self.node_frames_index)
        new_node = self.graph.add_node(node_name)
        print("[INFO] Added node: " + node_name + ".")
        self.create_node_frame(new_node, self.node_frames_index)
        self.node_frames_index += 1
        self.draw_graph()

        self.nodes_canvas.grid()
        self.nodes_scrollbar.grid()

        for node in self.graph.nodes:
            if hasattr(node, "add_transition_menu"):
                available_nodes = [n.name for n in self.graph.nodes if n != node]
                node.add_transition_menu.configure(values=available_nodes)

        self.update_scroll_region()










    # ==============================================================================================
    # RIGHT PANEL
    # ==============================================================================================
    
    # ==============================================================================================
    # SETTINGS TAB
    # ==============================================================================================
      
    # ==============================================================================================
    # TESTS RUNNER & COMPARISON TAB
    # ==============================================================================================
    
    # ==============================================================================================
    # TERMINAL TAB
    # ==============================================================================================

    # ==============================================================================================
    # LEFT PANEL
    # ==============================================================================================