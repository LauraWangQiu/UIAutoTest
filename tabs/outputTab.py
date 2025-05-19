import sys
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from tab import Tabs

class OutputTab(Tabs):
    def __init__(self, parent, app_reference):
        super().__init__(parent, app_reference)

    """
    Add a terminal tab to display console output.
    """
    def addTab(self):
        terminal_tab = ctk.CTkFrame(self.app.tab_control)
        self.app.tab_control.add(terminal_tab, text="Terminal")

        # Create a ScrolledText widget for the terminal output
        self.terminal_output = ScrolledText(terminal_tab, wrap="word", state="disabled", height=20)
        self.terminal_output.pack(fill="both", expand=True, padx=10, pady=10)

        # Redirect stdout and stderr to the terminal output
        sys.stdout = self.TextRedirector(self.terminal_output)
        sys.stderr = self.TextRedirector(self.terminal_output)

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