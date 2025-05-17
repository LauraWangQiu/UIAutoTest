# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import threading
import math
import time
import inspect
import importlib.util
import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from test import Test
from graphsDef import Graph, Transition
from actionTypes import ActionType
import graphIO as _graph_io_module
GraphIO = _graph_io_module.GraphIO
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class App(ctk.CTk):
    """
        Constructor for the App class

        Args:
            window_name (str): The title of the application window
            window_size (str): The size of the application window (e.g., "800x600")
            tests_directory (str): The directory where test files are located
            headless (bool): Whether the application is running in headless mode
    """
    def __init__(self,
                java_path, jython_jar, sikulix_jar,
                sikuli_script,
                window_name, window_size,
                images_dir, tests_dir, 
                theorical_graph_file,
                practical_graph_file,
                generate_graph,
                selected_executable,
                executable_delay,
                debug_images,
                timeout,
                initial_similarity,
                min_similarity,
                similarity_step,
                retries,
                state_reset_method,
                internal_reset_script,
                tests_to_run,
                solution_file,
                headless=False):
        self.java_path = java_path                                      # Path to Java executable
        self.jython_jar = jython_jar                                    # Path to Jython jar file
        self.sikulix_jar = sikulix_jar                                  # Path to SikuliX jar file
        self.sikuli_script = sikuli_script                              # Path to Sikuli script
        self.jython_process = None                                      # Jython process
        self.jython_thread = None                                       # Jython thread
            
        self.graph_io = GraphIO()                                       # GraphIO instance
        self.graph = Graph()                                            # Theorical graph
        self.generated_graph = None                                     # Practical graph
        self.theorical_graph_file   = theorical_graph_file              # Theoretical graph file
        self.practical_graph_file   = practical_graph_file              # Practical graph file
        self.generate_graph         = generate_graph                    # Flag to generate graph
        self.images_dir             = images_dir                        # Directory of images
        self.tests_dir              = tests_dir                         # Directory of tests
        self.test_classes           = None                              # List of test classes        
        self.selected_executable    = selected_executable               # Selected executable path
        self.executable_delay       = executable_delay                  # Delay for the executable to start
        self.debug_images           = debug_images                      # Flag to show debug images when generating the graph
        self.timeout                = timeout                           # Timeout for SikuliX
        self.initial_similarity     = initial_similarity                # Initial similarity for SikuliX
        self.min_similarity         = min_similarity                    # Minimum similarity for SikuliX
        self.similarity_step        = similarity_step                   # Similarity step for SikuliX
        self.retries                = retries                           # Number of retries for SikuliX
        self.state_reset_method     = state_reset_method                # State reset method
        self.internal_reset_script  = internal_reset_script             # Internal reset script
        self.tests_to_run           = tests_to_run                      # List of tests to run
        self.solution_file          = solution_file                     # Test solution file
        self.headless               = headless                          # Store the headless mode flag

        self.graphDiff_PDF_route = "graphDiff.pdf"
        self.diff = {
            'missing_nodes_prac': set(),
            'missing_nodes_theo': set(),
            'missing_edges_gen': set(),
            'missing_edges_the': set(),
        }
        
        self.test_checkboxes = {}
        self.test_output_widgets = {}

        if self.headless:
            print("[INFO] Application initialized in headless mode")
            self.load_graph_from_file(self.theorical_graph_file)
            self.test_classes = self.get_test_classes()
            if self.generate_graph:
                self.generate_graph_from_executable()
                while self.jython_thread.is_alive():
                    time.sleep(0.1)
            self.run_tests()
            self.compare()
            self.create_PDF(self.graphDiff_PDF_route)
        else: 
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

    """
        Load theorical graph from a file using GraphIO
    """
    def load_graph_from_file(self, file_name):
        try:
            self.graph = self.graph_io.load_graph(file_name, self.images_dir)
            print("[INFO] Graph successfully loaded")
        except FileNotFoundError:
            print("[ERROR] File " + file_name + " not found")
        except Exception as e:
            print("[ERROR] An error occurred while loading the graph: " + str(e))

    """
        Configure the grid layout of the main window
    """
    def configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
   
    """
        Create the tabs: States and Tests
        The Tests tab is created dynamically based on the test classes found in the specified directory
    """
    def create_tabs(self):
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[20, 10])
        style.configure("TNotebook", tabposition="nw")

        self.tabs_to_keep = {"States", "Generate, Run & Compare", "Settings", "Terminal"}

        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=0, column=0, sticky="nsew")

        # States tab
        self.states_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(self.states_tab, text="States")
        self.configure_states_tab()

        # Test Runner tab
        self.add_test_runner_tab()

        # Settings tab
        self.add_settings_tab()

        # Output tab
        self.add_terminal_tab()

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
            
    # ==============================================================================================
    # LEFT PANEL
    # ==============================================================================================
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
        Clear the entire graph and all nodes
    """
    def clear_graph(self):
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
        Handle mouse wheel scrolling for the canvas
    """
    def update_scroll_region(self, event=None):
        self.nodes_canvas.configure(scrollregion=self.nodes_canvas.bbox("all"))

    """
        Handle mouse wheel scrolling for the canvas
    """
    def on_mouse_wheel(self, event):
        self.nodes_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    # ==============================================================================================
    # RIGHT PANEL
    # ==============================================================================================
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

    # ==============================================================================================
    # TESTS RUNNER & COMPARISON TAB
    # ==============================================================================================
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
        generate_graph_button = ctk.CTkButton(scrollable_frame, text="Generate Graph from Executable", command=self.generate_graph_from_executable)
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
        self.selected_practical_graph_var = ctk.StringVar(value=self.theorical_graph_file)
        self.selected_practical_graph_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.selected_practical_graph_var, state="readonly", font=ctk.CTkFont(size=12))
        self.selected_practical_graph_entry.pack(fill="x", padx=10, pady=5)

        select_practical_graph_button = ctk.CTkButton(
            scrollable_frame,
            text="Select Practical Graph File",
            command=self.select_practical_graph_file
        )
        select_practical_graph_button.pack(padx=10, pady=5, anchor="w")

        # Run tests button
        run_button = ctk.CTkButton(scrollable_frame, text="Run Tests", command=self.run_tests)
        run_button.pack(fill="x", padx=10, pady=5)

        # Compare button
        compare_button = ctk.CTkButton(scrollable_frame, text="Compare Graphs", command=self.compare)
        compare_button.pack(fill="x", padx=10, pady=5)

    def select_tests_dir(self):
        directory_path = filedialog.askdirectory(
            title="Select Tests Directory"
        )
        if directory_path:
            self.tests_dir = directory_path
            self.tests_dir_var.set(self.tests_dir)
            print(f"Selected tests directory: {self.tests_dir}")
            self.test_classes = self.get_test_classes()
            self.populate_test_list()
            self.reload_test_tabs()

    def reload_test_tabs(self):
        for i in reversed(range(self.tab_control.index("end"))):
            tab_text = self.tab_control.tab(i, "text")
            if tab_text not in self.tabs_to_keep:
                self.tab_control.forget(i)
        # Add new tests
        for test_class_name, test_class_ref in self.test_classes:
            self.add_test_tab(test_class_name, test_class_ref)

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
    def select_practical_graph_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Practical Graph File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_practical_graph_file = file_path
            self.selected_practical_graph_var.set(file_path)
            print(f"[INFO] Practical graph file for tests set to: {file_path}")

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
        Generate the graph from the selected executable calling the Jython script
    """
    def generate_graph_from_executable(self):
        if not self.selected_executable:
            print("[ERROR] No executable selected. Please select an executable first.")
            return
        
        self.run_jython()

    """
        Run the selected tests.
    """
    def run_tests(self):
        # If headless mode, then run tests specified from file
        # else, run tests from the GUI
        selected_test_classes = []

        if self.headless and self.test_classes is not None:
            available_test_classes = {name: ref for name, ref in self.test_classes}
            for test_name in self.tests_to_run:
                if test_name in available_test_classes:
                    selected_test_classes.append(available_test_classes[test_name])
                else:
                    print(f"[ERROR] Test class '{test_name}' not found in available test classes.")
        else:
            selected_test_classes = [
                test_class_ref for test_class_name, (var, test_class_ref) in self.test_checkboxes.items() if var.get()
            ]

        if selected_test_classes:
            self.execute_selected_tests(selected_test_classes)
        else:
            print("[ERROR] No tests selected.")

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
                    "--delay", str(self.executable_delay),
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
                    "--internal_reset_script", str(self.internal_reset_script),
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
            test_instances.append((test_class_name, test_instance))

    """
        Compare the generated graph with specified graph
    """
    def compare(self):
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
                differences_found += self.compare_aux(self.generated_graph, self.graph, f, "diff_in_gen")
                print("[INFO] Comparing given graph with generated graph...")
                f.write("[COMPARING GIVEN GRAPH vs GENERATED GRAPH]\n")
                differences_found += self.compare_aux(self.graph, self.generated_graph, f, "diff_in_the")
                if differences_found == 0:
                    f.write("[NO DIFFERENCES FOUND]\n")
            print("[INFO] Comparison finished. No differences found." if differences_found == 0 else f"[INFO] Comparison finished. {differences_found} differences found.")
        except Exception as e:
            print(f"[ERROR] Exception during comparison: {e}")

    def compare_aux(self, graph1:Graph, graph2:Graph, file_output, diff_to):
        differences_found = 0
        for node1 in graph1.nodes:
            print("[INFO] Comparing node: " + node1.name)
            node2 = graph2.get_node_image(node1.image)
            if node2 is None: # Node is not in generated graph
                print("[INFO] Node not found: " + node1.name)
                file_output.write("[MISSING NODE] " + node1.name + " not in graph2\n")
                # Saves the diffs to the PDF.
                if diff_to == "diff_in_gen":
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
                            # Saves the diffs to the PDF.
                            if diff_to == "diff_in_gen":
                                self.diff['missing_edges_the'].add((node1.name, trans1.destination.name))                         
                            else:
                                self.diff['missing_edges_gen'].add((node1.name, trans1.destination.name))
                            differences_found += 1
                        found = True
                        continue
                if not found:
                    print("[INFO] Transition not found: " + trans1.image)
                    file_output.write("[MISSING TRANSITION] " + node1.name + " -/-> " + trans1.destination.name + " " + trans1.image + "\n")
                    file_output.write("[MISSING TRANSITION] " + node1.name + " -/-> " + trans1.destination.name + "\n")
                    # Saves the diffs to the PDF.
                    if diff_to == "diff_in_gen":
                        self.diff['missing_edges_the'].add((node1.name, trans1.destination.name))
                    else:
                        self.diff['missing_edges_gen'].add((node1.name, trans1.destination.name))
                    differences_found += 1
            return differences_found

    # ==============================================================================================
    # SETTINGS TAB
    # ==============================================================================================
    def add_settings_tab(self):
        settings_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(settings_tab, text="Settings")

        # Java Path
        java_label = ctk.CTkLabel(settings_tab, text="Java Path:", font=ctk.CTkFont(size=12))
        java_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.java_path_var = ctk.StringVar(value=self.java_path if self.java_path else "java")
        java_entry = ctk.CTkEntry(settings_tab, textvariable=self.java_path_var, width=400)
        java_entry.pack(fill="x", padx=10, pady=2)
        java_button = ctk.CTkButton(settings_tab, text="Select Java Executable", command=self.select_java_path)
        java_button.pack(padx=10, pady=5, anchor="w")

        # SikuliX Path
        sikulix_label = ctk.CTkLabel(settings_tab, text="SikuliX API Jar Path:", font=ctk.CTkFont(size=12))
        sikulix_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.sikulix_jar_var = ctk.StringVar(value=self.sikulix_jar)
        sikulix_entry = ctk.CTkEntry(settings_tab, textvariable=self.sikulix_jar_var, width=400)
        sikulix_entry.pack(fill="x", padx=10, pady=2)
        sikulix_button = ctk.CTkButton(settings_tab, text="Select SikuliX Jar", command=self.select_sikulix_jar)
        sikulix_button.pack(padx=10, pady=5, anchor="w")

        # Jython Path
        jython_label = ctk.CTkLabel(settings_tab, text="Jython Jar Path:", font=ctk.CTkFont(size=12))
        jython_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.jython_jar_var = ctk.StringVar(value=self.jython_jar)
        jython_entry = ctk.CTkEntry(settings_tab, textvariable=self.jython_jar_var, width=400)
        jython_entry.pack(fill="x", padx=10, pady=2)
        jython_button = ctk.CTkButton(settings_tab, text="Select Jython Jar", command=self.select_jython_jar)
        jython_button.pack(padx=10, pady=5, anchor="w")

        # Name of the practical graph file to export
        practical_graph_label = ctk.CTkLabel(settings_tab, text="Practical Graph File to Export:", font=ctk.CTkFont(size=12))
        practical_graph_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.export_practical_graph_var = ctk.StringVar(value=self.practical_graph_file if self.practical_graph_file else "")
        self.export_practical_graph_entry = ctk.CTkEntry(settings_tab, textvariable=self.export_practical_graph_var, width=400)
        self.export_practical_graph_entry.pack(fill="x", padx=10, pady=2)
        def on_export_practical_graph_change(*args):
            self.export_practical_graph_file = self.export_practical_graph_var.get()
        self.export_practical_graph_var.trace_add("write", lambda *args: on_export_practical_graph_change())

        # Name of the solution file
        solution_label = ctk.CTkLabel(settings_tab, text="Solution File:", font=ctk.CTkFont(size=12))
        solution_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.solution_var = ctk.StringVar(value=self.solution_file if self.solution_file else "")
        self.solution_entry = ctk.CTkEntry(settings_tab, textvariable=self.solution_var, width=400)
        self.solution_entry.pack(fill="x", padx=10, pady=2)
        def on_solution_change(*args):
            self.solution_file = self.solution_var.get()
        self.solution_var.trace_add("write", lambda *args: on_solution_change())

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

    # ==============================================================================================
    # TERMINAL TAB
    # ==============================================================================================
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
            self.quit()
        except Exception as e:
            print(f"[WARNING] Failed to quit mainloop: {e}")

        self.destroy()

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
        Creates a PDF with the diff graph after the comparison.
    """ 
    def create_PDF(self, output_pdf_path: str):
        all_nodes = set()
        for n in self.graph.nodes:
            all_nodes.add(n.name)
        for n2 in self.generated_graph.nodes:
            all_nodes.add(n2.name)

        G = nx.DiGraph()
        # Set the colour of the nodes depending in where they are.
        for name in all_nodes:
            if name in self.diff['missing_nodes_prac']:
                color = 'red'
            elif name in self.diff['missing_nodes_theo']:
                color = 'green'
            else:
                color = 'black'
            G.add_node(name, color = color)
        
        # Set the transitions missing in generated graph in green
        for n in self.graph.nodes:
            for t in n.transitions:
                u = n.name
                v = t.destination.name
                if (u, v) in self.diff['missing_edges_gen']:
                    edge_color = 'red'
                    style = 'solid'
                else:
                    edge_color = 'black'
                    style = 'solid'
                G.add_edge(u, v, color = edge_color, style=style)
        # Set the transitions missing in theorical graph in green
        for (u, v) in self.diff['missing_edges_the']:
            G.add_edge(u, v, color = 'green', style = 'solid')

        plt.figure(figsize = (12, 8))
        pos = nx.spring_layout(G)

        # Draw the nodes.
        node_colors = []
        for node in G.nodes():
            node_colors.append(G.nodes[node]['color'])
        nx.draw_networkx_nodes(G, pos, node_size = 1500, node_color = node_colors)

        # Draw nodes names.
        nx.draw_networkx_labels(G, pos, font_size = 9, font_color='white')

        # Draw the transitions.
        for u, v, attr in G.edges(data=True):
            nx.draw_networkx_edges(
                G, pos,
                edgelist = [(u, v)],
                style=attr['style'],
                edge_color = attr['color'],
                arrowsize = 30,
                width = 3
            )


        # Caption of the document
        black_node = mpatches.Patch(color = 'black', label = 'In boths grphs')
        red_node   = mpatches.Patch(color = 'red',   label = 'Not in generated graph.')
        green_node = mpatches.Patch(color = 'green', label = 'Not in theorical graph.')
       
        caption = [black_node, red_node, green_node]
        plt.legend(handles = caption, loc = 'upper right', fontsize = 10, frameon = True, labelcolor = "orange")


        plt.axis('off')
        plt.tight_layout()
        try:
            plt.savefig(output_pdf_path, format = 'pdf', bbox_inches = 'tight')
            print(f"[INFO] DiffGraph PDF done in: {output_pdf_path}")
        except Exception as e:
            print(f"[ERROR] Erro while doing the PDF: {e}")
        finally:
            plt.close()