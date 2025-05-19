import os
import math
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from actionTypes import ActionType
from graphsDef import  Transition

from tab import Tabs

class StatesTab(Tabs):
    def __init__(self, parent, app_reference):
       
        self.selected_nodes = []
        self.node_frames = []
        self.node_frames_index = 1
        super().__init__(parent, app_reference)

    """
       Configure the States tab layout
    """
    def addTab(self):
        self.app.states_tab.grid_columnconfigure(0, weight=1)
        self.app.states_tab.grid_rowconfigure(0, weight=1)

        #self.split_frame = ctk.CTkFrame(self.add.states_tab)
        self.split_frame = ctk.CTkFrame(self.parent)
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
            self.app.graph_io.write_graph(self.app.images_dir, file_path, self.app.graph)  

    def load_graph_from_dialog(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Load graph from file"
        )
        if file_path:
            self.clear_graph()
            self.app.graph = self.app.graph_io.load_graph(file_path, self.app.images_dir)
            if self.app.graph is None:
                print("[ERROR] Graph not loaded.")
                return
            self.node_frames_index = len(self.app.graph.nodes) + 1
            
            # Create frames for each node in the loaded graph
            for idx, node in enumerate(self.app.graph.nodes, 1):
                self.create_node_frame(node, idx)
            # Create the transitions list for each node
            for node in self.app.graph.nodes:
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
        new_node = self.app.graph.add_node(node_name)
        print("[INFO] Added node: " + node_name + ".")
        self.create_node_frame(new_node, self.node_frames_index)
        self.node_frames_index += 1
        self.draw_graph()

        self.nodes_canvas.grid()
        self.nodes_scrollbar.grid()

        for node in self.app.graph.nodes:
            if hasattr(node, "add_transition_menu"):
                available_nodes = [n.name for n in self.app.graph.nodes if n != node]
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
        if self.app.graph.update_node_name(node, new_name):
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
        
        available_nodes = [n.name for n in self.app.graph.nodes]
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
        for n in self.app.graph.nodes:
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
        nodes_to_remove = [node for node in self.app.graph.nodes if getattr(node, "checkbox_var", None) and node.checkbox_var.get()]
        
        if not nodes_to_remove:
            print("[INFO] No states selected for removal")
            return

        for node in nodes_to_remove:
            self.app.graph.remove_node(node)
            print(f"[INFO] Removed node: {node.name}")

            for frame, edit_frame in self.node_frames:
                if frame._name == str(id(node)):
                    frame.destroy()
                    if edit_frame:
                        edit_frame.destroy()

        self.node_frames = [(frame, edit_frame) for frame, edit_frame in self.node_frames if frame.winfo_exists()]
        self.selected_nodes = [node for node in self.selected_nodes if node not in nodes_to_remove]

        for node in self.app.graph.nodes:
            node.transitions = [t for t in node.transitions if t.destination not in nodes_to_remove]
            self.update_transitions_list(node)

            if not node.transitions:
                node.transitions_list_frame.grid_remove()

        if len(self.app.graph.nodes) == 0:
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
        if self.app.graph is None:
            print("[INFO] No graph to clear")
            return
        
        self.app.graph.clear()
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
    
        num_nodes = len(self.app.graph.nodes)
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 2  
    
        for i, node in enumerate(self.app.graph.nodes):
            angle = (2 * math.pi / num_nodes) * i
            x = center_x + int(radius * 0.8 * math.cos(angle))
            y = center_y + int(radius * 0.8 * math.sin(angle))
            node_positions[node] = (x, y)
    
        # Draw nodes
        node_radius = 20
        for node, (x, y) in node_positions.items():
            self.draw_node(node, x, y, node_radius)
    
        # Draw transitions
        for node in self.app.graph.nodes:
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

