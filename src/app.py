# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import threading
import math
import inspect
import importlib.util
import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
from test import Test
from graphsDef import Graph, Transition
import GraphIO as _graph_io_module
GraphIO = _graph_io_module.GraphIO

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
                selected_executable,
                executable_delay,
                tests_to_run,
                headless=False):
        self.java_path = java_path                          # Path to Java executable
        self.jython_jar = jython_jar                        # Path to Jython jar file
        self.sikulix_jar = sikulix_jar                      # Path to SikuliX jar file
        self.sikuli_script = sikuli_script                  # Path to Sikuli script
        self.jython_process = None                          # Jython process
        self.jython_thread = None                           # Jython thread

        self.graph_io = GraphIO()                           # GraphIO instance
        self.graph = Graph()                                # Theorical graph
        self.graph_exe = Graph()                            # Practical graph
        self.theorical_graph_file   = theorical_graph_file  # Theoretical graph file
        self.practical_graph_file   = practical_graph_file  # Practical graph file
        self.images_dir             = images_dir            # Directory of images
        self.tests_dir              = tests_dir             # Directory of tests
        self.test_classes = self.get_test_classes()
        self.selected_executable    = selected_executable   # Selected executable path
        self.executable_delay       = executable_delay      # Delay for the executable to start
        self.tests_to_run           = tests_to_run          # List of tests to run
        self.headless               = headless              # Store the headless mode flag

        if self.headless:
            print("[INFO] Application initialized in headless mode")
            self.load_graph_from_file(self.theorical_graph_file)
            self.generate_graph_from_executable()
            self.run_tests()
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
            self.graph = self.graph_io.load_graph(file_name, "imgs")
            print("[INFO] Graph successfully loaded")
            #self.graph_io.write_graph("mi_graph.txt", self.graph)
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

        self.tab_control = ttk.Notebook(self)
        self.tab_control.grid(row=0, column=0, sticky="nsew")

        # States tab
        self.states_tab = ctk.CTkFrame(self.tab_control)
        self.tab_control.add(self.states_tab, text="States")
        self.configure_states_tab()

        # Tests tabs
        for test_class_name, test_class_ref in self.test_classes:
            self.add_test_tab(test_class_name, test_class_ref)

        # Test Runner tab
        self.add_test_runner_tab()

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
            self.graph_io.write_graph(file_path, self.graph)

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
                node.add_transition(Transition(n, lambda: True))
                break

        self.update_transitions_list(node)

        if hasattr(node, "add_transition_menu"):
            node.add_transition_menu.destroy()
            delattr(node, "add_transition_menu")

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
            if hasattr(node, "image") and node.image:
                try:
                    original_image = Image.open(node.image)
                    resized_image = original_image.resize((node_radius * 2, node_radius * 2), Image.Resampling.LANCZOS)
                    image = ImageTk.PhotoImage(resized_image)

                    node.tk_image = image
                    self.canva.create_image(x, y, image=image, tags=node.name)
                except Exception as e:
                    print(f"[WARNING] Could not load image for node {node.name}: {e}")
                    self.canva.create_oval(
                        x - node_radius, y - node_radius, x + node_radius, y + node_radius,
                        fill="lightblue", outline="black", width=2, tags=node.name
                    )
            else:
                self.canva.create_oval(
                    x - node_radius, y - node_radius, x + node_radius, y + node_radius,
                    fill="lightblue", outline="black", width=2, tags=node.name
                )
            self.canva.create_text(x, y, text=node.name, font=("Arial", 12), tags=node.name)
    
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
                    self.canva.create_arc(
                        x1 - node_radius - offset, y1 - node_radius - offset,
                        x1 + node_radius + offset, y1 + node_radius + offset,
                        start=0, extent=300, style="arc", outline="black", width=2
                    )
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
    
                    # Draw line with arrow
                    self.canva.create_line(
                        x1_adjusted, y1_adjusted, x2_adjusted, y2_adjusted, arrow="last", fill="black"
                    )

                    mid_x = (x1_adjusted + x2_adjusted) // 2
                    mid_y = (y1_adjusted + y2_adjusted) // 2

                    action_text = transition.action.name if hasattr(transition.action, "name") else str(transition.action)
                    self.canva.create_text(mid_x, mid_y, text=action_text, font=("Arial", 10), fill="blue")

                    try:
                        if os.path.exists(transition.image):
                            button_image = Image.open(transition.image)
                            resized_button_image = button_image.resize((20, 20), Image.Resampling.LANCZOS)
                            button_image_tk = ImageTk.PhotoImage(resized_button_image)

                            self.canva.create_image(mid_x + 30, mid_y, image=button_image_tk)
                            transition.tk_image = button_image_tk
                    except Exception as e:
                        print(f"[WARNING] Could not load button image for transition {node.name} to {transition.destination.name}: {e}")

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
            # TODO: Add the needed arguments to run the test
            # elif isinstance(attr_value, list):

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

        # Entry to display the selected executable path
        self.executable_entry = ctk.CTkEntry(test_runner_tab, state="readonly", font=ctk.CTkFont(size=12))
        self.executable_entry.insert(0, "Executable: None")
        self.executable_entry.pack(fill="x", padx=10, pady=5)

        # Button to select executable
        select_executable_button = ctk.CTkButton(test_runner_tab, text="Select Executable", command=self.select_executable)
        select_executable_button.pack(fill="x", padx=10, pady=5)

        # Entry to display the selected images directory
        self.images_dir_entry = ctk.CTkEntry(test_runner_tab, state="readonly", font=ctk.CTkFont(size=12))
        self.images_dir_entry.insert(0, "Images Directory: None")
        self.images_dir_entry.pack(fill="x", padx=10, pady=5)

        # Button to select images directory
        select_images_dir_button = ctk.CTkButton(test_runner_tab, text="Select Images Directory", command=self.select_images_dir)
        select_images_dir_button.pack(fill="x", padx=10, pady=5)

        # Button to generate the graph from executable
        generate_graph_button = ctk.CTkButton(test_runner_tab, text="Generate Graph from Executable", command=self.generate_graph_from_executable)
        generate_graph_button.pack(fill="x", padx=10, pady=5)

        # Title
        title_label = ctk.CTkLabel(test_runner_tab, text="Select Tests to Run", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(pady=10)

        # Frame for the list of tests
        self.test_list_frame = ctk.CTkFrame(test_runner_tab)
        self.test_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Populate the list of tests
        self.populate_test_list()

        # Run tests button
        run_button = ctk.CTkButton(test_runner_tab, text="Run Tests", command=self.run_tests)
        run_button.pack(pady=10)

        # Compare button
        compare_button = ctk.CTkButton(test_runner_tab, text="Compare Results", command=self.compare)
        compare_button.pack(pady=10)

    """
        Populate the test list with checkboxes for each test class found in the specified directory
        Each checkbox is associated with a test class reference
    """
    def populate_test_list(self):
        for widget in self.test_list_frame.winfo_children():
            widget.destroy()

        # Add each test as a checkbox
        self.test_checkboxes = {}
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
            print(f"Selected images directory: {self.images_dir}")

            self.images_dir_entry.configure(state="normal")
            self.images_dir_entry.delete(0, "end")
            self.images_dir_entry.insert(0, self.images_dir)
            self.images_dir_entry.configure(state="readonly")

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

        if self.headless:
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

        if not selected_test_classes:
            print("[INFO] No tests selected")
            return
        
        self.check_jython_thread(selected_test_classes)

    """
        Run the Jython script to generate the graph
    """
    def run_jython(self):
        def execute_command():
            try:
                self.command = [
                    self.java_path,
                    "-cp",
                    f"{self.jython_jar};{self.sikulix_jar}",
                    "org.python.util.jython",
                    self.sikuli_script,
                    "--images_dir", self.images_dir,
                    "--practical_graph_file", self.practical_graph_file,
                    "--selected_executable", self.selected_executable,
                    "--delay", self.executable_delay
                ]
                if any(arg is None for arg in self.command):
                    raise ValueError("[ERROR] One or more arguments in the Jython command are None.")
                print("[INFO] Running Jython script: " + " ".join(self.command) + "\n")

                with subprocess.Popen(
                    self.command,
                    stdout=sys.__stdout__,
                    stderr=sys.__stderr__,
                    text=True,
                    shell=True
                ) as process:
                    while process.poll() is None:
                        if self.stop_event.is_set():
                            process.terminate()
                            print("[INFO] Jython script terminated.")
                            return
                        threading.Event().wait(0.1)

            except Exception as e:
                print("[ERROR] Failed to run Jython script: " + str(e) + "\n")
            finally:
                self.jython_process = None

        self.jython_thread = threading.Thread(target=execute_command, daemon=True)
        self.jython_thread.start()

    def check_jython_thread(self, selected_test_classes):
        def _check():
            if self.jython_thread.is_alive():
                try:
                    if hasattr(self, "tk") and self.tk is not None:
                        after_id = self.after(1000, _check)
                        if hasattr(self, "after_ids"):
                            self.after_ids.append(after_id)
                    else:
                        raise RuntimeError("Tkinter not initalized")
                except Exception as e:
                    threading.Timer(1.0, _check).start()
            else:
                print("[INFO] Jython thread finished.")
                self.execute_tests(selected_test_classes)

        _check()

    """
        Execute the selected tests
    """
    def execute_tests(self, selected_test_classes):
        for test_class_ref in selected_test_classes:
            test_instance = test_class_ref(self.graph_io.load_graph(self.practical_graph_file, self.images_dir))
            test_instance.run()
            # TODO: Do something with the tests results
        
        # Directly compare the generated graph with the expected graph
        if self.headless:
            self.compare()

    """
        Compare the generated graph with specified graph
    """
    def compare(self):
        # TODO: Get the file generated and the expected graph and compare them
        # Also, save the generated results of the tests
        print("Comparing results...")

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

        # Redirect stdout to the terminal output
        sys.stdout = self.TextRedirector(self.terminal_output)

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