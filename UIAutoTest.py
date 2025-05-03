import customtkinter 
from pathlib import Path 
from src.graphsDef import Graph  
import math 
from src.graphsDef import Transition  

class App(customtkinter.CTk):  
    def __init__(self):  # constructor of the App class
        super().__init__()  # calls the constructor of the base class
        
        self.graph = Graph() # creates an empty graph
        self.selected_node = None  
        self.configure_grid()
        self.left_panel()
        self.right_panel()
        self.after(100, self.draw_graph)  # calls the draw_graph method after 100 ms to ensure the canva is ready

    def configure_grid(self):
        self.title("UI Auto Test")  # name of the window
        self.geometry("800x600")  # size of the window

        # layout configuration: 1 row and 2 columns
        self.grid_columnconfigure(0, weight=1)  #the weight affects how much space this column takes relative to others
        self.grid_columnconfigure(1, weight=3)  
        self.grid_rowconfigure(0, weight=1)

   
    def left_panel(self): 
        # create a container for the left panel that will only have one column
        self.info = customtkinter.CTkFrame(self)  
        self.info.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # add margins to the sides and make it expand to occupy height and width
        self.info.grid_columnconfigure(0, weight=1) 
       
        # panel title
        self.info_label = customtkinter.CTkLabel(self.info, text="States", font=customtkinter.CTkFont(size=16, weight="bold")) 
        self.info_label.grid(row=0, column=0, padx=10, pady=5, sticky="ew")  # centered

        # button to add nodes
        self.add_node_button = customtkinter.CTkButton(self.info, text="Add State", command=self.add_node)  
        self.add_node_button.grid(row=1, column=0, padx=10, pady=0, sticky="ew")  

        # button to remove nodes
        self.remove_node_button = customtkinter.CTkButton(self.info, text="Remove State", command=self.remove_selected_node)  
        self.remove_node_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew") 
       
        self.node_frames = [] 

    def right_panel(self):  
       # create a container for the right panel that will only have one column
        self.graph_frame = customtkinter.CTkFrame(self)  
        self.graph_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")  
        self.graph_frame.grid_columnconfigure(0, weight=1) 
        self.graph_frame.grid_rowconfigure(0, weight=1)  
        # create a canva with white background
        self.canva = customtkinter.CTkCanvas(self.graph_frame, bg="white")  
        self.canva.pack(fill="both", expand=True, padx=10, pady=10) 
        
    def add_node(self): 
        #graph node
        node_name = f"State {len(self.graph.nodes) + 1}"  
        
        new_node = self.graph.add_node(node_name, Path("imgs/image.png")) 
        # cisual node 
        self.create_node_frame(new_node, len(self.graph.nodes) - 1)  
        self.draw_graph() 

    def remove_selected_node(self): 
        #remove a node from the graph
        #right now does not work because there is no selected node!!!!!!!!!!!!!!!!!!!!!!!
        if self.selected_node: 
            self.graph.remove_node(self.selected_node)  
            self.selected_node = None 
            self.draw_graph()  

    def create_node_frame(self, node, index):  
        frame = customtkinter.CTkFrame(self.info, corner_radius=10)  
        # row +3 (title, add, remove)
        frame.grid(row=index + 3, column=0, padx=10, pady=5, sticky="ew")  

        # Button to select the node that toggles the content visibility
        button = customtkinter.CTkButton(frame, text=node.name, command=lambda n=node: self.toggle_node_frame(n, frame)) 
        button.pack(fill="x", padx=5, pady=5)  

        # Container for the node content
        edit_frame = customtkinter.CTkFrame(frame, corner_radius=10)  
        edit_frame.pack(fill="x", padx=5, pady=5)  
        edit_frame.grid_columnconfigure(0, weight=1)  

        # Field to change the node name
        name_label = customtkinter.CTkLabel(edit_frame, text="Name:")  
        name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")  
        name_entry = customtkinter.CTkEntry(edit_frame) 
        name_entry.insert(0, node.name)  
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")  
        name_entry.bind("<KeyRelease>", lambda e, n=node: self.update_node_name(n, name_entry.get()))  # Bind the text change event to the update_node_name method

        # List of connections
        connections_label = customtkinter.CTkLabel(edit_frame, text="Transitions:") 
        connections_label.grid(row=1, column=0, padx=5, pady=5, sticky="w") 

        # Frame for connection buttons
        connections_frame = customtkinter.CTkFrame(edit_frame) 
        connections_frame.grid(row=1, column=1, padx=5, pady=5, sticky="ew") 

        # Button to add a connection
        add_button = customtkinter.CTkButton(connections_frame, text="+", width=30, command=lambda n=node: self.add_connection(n))  
        add_button.pack(side="left", padx=5)  

        # Button to remove a connection
        remove_button = customtkinter.CTkButton(connections_frame, text="-", width=30, command=lambda n=node: self.remove_connection(n))  
        remove_button.pack(side="left", padx=5)  

       
        self.toggle_node_frame(node, frame)

        # Save references
        self.node_frames.append((frame, edit_frame))  # Save the frame and the edit frame in the list of frames

    def add_connection(self, node):
        
        menu = customtkinter.CTkOptionMenu(self, values=[n.name for n in self.graph.nodes if n != node],
                                           command=lambda selected: self.add_connection_to_node(node, selected))
        menu.place(relx=0.5, rely=0.5, anchor="center")

    def add_connection_to_node(self, node, selected_name):
       
        for n in self.graph.nodes:
            if n.name == selected_name:
                node.add_transition(Transition(n, lambda: True))
                break
        self.draw_graph()

    def remove_connection(self, node):
       
        menu = customtkinter.CTkOptionMenu(self, values=[t.destination.name for t in node.transitions],
                                           command=lambda selected: self.remove_connection_from_node(node, selected))
        menu.place(relx=0.5, rely=0.5, anchor="center")

    def remove_connection_from_node(self, node, selected_name):
        
        node.transitions = [t for t in node.transitions if t.destination.name != selected_name]
        self.draw_graph()


    def toggle_node_frame(self, node, frame):
       
        for f, edit_frame in self.node_frames:
            if f == frame:
                if edit_frame.winfo_ismapped():
                    edit_frame.pack_forget()
                else:
                    edit_frame.pack(fill="x", padx=5, pady=5)
            else:
                edit_frame.pack_forget()

    def update_node_name(self, node, new_name):
        if self.graph.update_node_name(node, new_name):
            self.draw_graph()


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
            angle = (2 * math.pi / num_nodes) * i  # Angle to distribute nodes in a circle
            x = center_x + int(radius * 0.8 * math.cos(angle))
            y = center_y + int(radius * 0.8 * math.sin(angle))
            node_positions[node] = (x, y)
        # Draw nodes
        node_radius = 20
        for node, (x, y) in node_positions.items():
            
            self.canva.create_oval(x - node_radius, y - node_radius, x + node_radius, y + node_radius, fill="lightblue", outline="black", width=2, tags=node.name)
            self.canva.create_text(x, y, text=node.name, font=("Arial", 12), tags=node.name)
        
        # Draw transitions
        for node in self.graph.nodes:
            x1, y1 = node_positions[node]  # Get the position of the current node
            for transition in node.transitions:
              
                x2, y2 = node_positions[transition.destination]  # Get the position of the destination node

                # Calculate the angle of the line
                dx = x2 - x1
                dy = y2 - y1
                distance = math.sqrt(dx**2 + dy**2)

                # Adjust the end of the line to stop at the edge of the destination node
                x2_adjusted = x2 - (dx / distance) * node_radius
                y2_adjusted = y2 - (dy / distance) * node_radius

                # Adjust the start of the line to start at the edge of the source node
                x1_adjusted = x1 + (dx / distance) * node_radius
                y1_adjusted = y1 + (dy / distance) * node_radius

                # Draw the line with the adjusted coordinates
                self.canva.create_line(
                    x1_adjusted, y1_adjusted, x2_adjusted, y2_adjusted, arrow="last", fill="black"
                )
        


if __name__ == "__main__":
     
   #Start the application and main loop
    app = App()  
    app.mainloop()