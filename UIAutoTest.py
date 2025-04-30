import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Directed Graph Visualizer")

        self.label = tk.Label(root, text="Adjacency list (node: neighbor1, neighbor2):")
        self.label.pack(pady=(10, 0))

        self.textbox = tk.Text(root, height=6, width=50)
        self.textbox.pack()

        self.draw_button = tk.Button(root, text="Apply", command=self.draw_graph)
        self.draw_button.pack(pady=10)

        self.figure = plt.Figure(figsize=(6, 5))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def parse_adjacency_list(self, raw_text):
        graph_dict = {}
        lines = raw_text.strip().splitlines()
        for line in lines:
            if ":" not in line:
                continue
            node, neighbors = line.split(":")
            node = node.strip()
            neighbors = [n.strip() for n in neighbors.split(",") if n.strip()]
            graph_dict[node] = neighbors
        return graph_dict

    def draw_graph(self):
        raw_text = self.textbox.get("1.0", tk.END)
        try:
            graph_data = self.parse_adjacency_list(raw_text)

            G = nx.DiGraph()
            for node, neighbors in graph_data.items():
                for neighbor in neighbors:
                    G.add_edge(node, neighbor)

            pos = nx.spring_layout(G)
            nx.draw(G, pos, ax=self.ax, with_labels=True, arrows=True,
                    node_color="lightgreen", node_size=2000, font_size=10)

            self.ax.set_title("Directed Graph")
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", f"Could not draw the graph:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
