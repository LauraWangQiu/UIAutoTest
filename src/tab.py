import customtkinter as ctk
from tkinter import filedialog, messagebox

class Tabs:
    def __init__(self, parent, app_reference):
        self.parent = parent
        self.app = app_reference  # app_reference -> principal instance

        self.tab = ctk.CTkFrame(self.parent)

        self.addTab()

    def addTab(self):
        pass