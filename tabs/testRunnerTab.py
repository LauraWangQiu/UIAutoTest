import customtkinter as ctk
from tkinter import filedialog, messagebox

from tab import Tabs

class TestRunnerTab(Tabs):

    def __init__(self, parent, app_reference):
        super().__init__(parent, app_reference)
        

    def addTab(self):
        test_runner_tab = ctk.CTkFrame(self.app.tab_control)
        self.app.tab_control.add(test_runner_tab, text="Generate, Run & Compare")

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
        self.images_dir_var = ctk.StringVar(value=self.app.images_dir)
        self.images_dir_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.images_dir_var, state="readonly", font=ctk.CTkFont(size=12))
        self.images_dir_entry.pack(fill="x", padx=10, pady=5)

        # Button to select images directory
        select_images_dir_button = ctk.CTkButton(scrollable_frame, text="Select Images Directory", command=self.select_images_dir)
        select_images_dir_button.pack(padx=10, pady=5, anchor="w")

        # Button to generate the graph from executable
        generate_graph_button = ctk.CTkButton(scrollable_frame, text="Generate Graph from Executable", command=self.app.generate_graph_from_executable) # TODO ES COMUN
        generate_graph_button.pack(fill="x", padx=10, pady=5)

        # Label for the selected tests directory
        tests_label = ctk.CTkLabel(scrollable_frame, text="Selected Tests Directory:", font=ctk.CTkFont(size=12))
        tests_label.pack(anchor="w", padx=10, pady=(10, 2))

        # Entry to display the selected tests directory
        self.tests_dir_var = ctk.StringVar(value=self.app.tests_dir)
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
        self.app.test_list_frame = ctk.CTkFrame(scrollable_frame)
        self.app.test_list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Label for the selected practical graph file
        practical_graph_label = ctk.CTkLabel(scrollable_frame, text="Selected Practical Graph File:", font=ctk.CTkFont(size=12))
        practical_graph_label.pack(anchor="w", padx=10, pady=(10, 2))

        # Entry to display the selected practical graph file
        self.practical_graph_var = ctk.StringVar(value=self.app.practical_graph_file)
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
        self.theorical_graph_var = ctk.StringVar(value=self.app.theorical_graph_file)
        self.theorical_graph_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.theorical_graph_var, state="readonly", font=ctk.CTkFont(size=12))
        self.theorical_graph_entry.pack(fill="x", padx=10, pady=5)

        select_theorical_graph_button = ctk.CTkButton(
            scrollable_frame,
            text="Select Theorical Graph File",
            command=self.select_theorical_graph_file
        )
        select_theorical_graph_button.pack(padx=10, pady=5, anchor="w")

        # Run tests button
        run_button = ctk.CTkButton(scrollable_frame, text="Run Tests", command=self.app.run_tests) # TODO COMUN
        run_button.pack(fill="x", padx=10, pady=5)

        # Compare button
        compare_button = ctk.CTkButton(scrollable_frame, text="Compare Graphs", command=self.app.compare) # TODO COMUN
        compare_button.pack(fill="x", padx=10, pady=5)

        # Button to Generate PDF
        generate_pdf_button = ctk.CTkButton(scrollable_frame, text="Generate PDF", command=lambda: self.app.create_PDF(self.app.pdf_file)) # TODO COMUN
        generate_pdf_button.pack(fill="x", padx=10, pady=5)

        """
        Select an executable file using a file dialog and update the entry field with the selected path
    """
    def select_executable(self):
        file_path = filedialog.askopenfilename(
            title="Select Executable",
            filetypes=[("Executables", "*.exe"), ("All Files", "*.*")]
        )
        if file_path:
            self.app.selected_executable = file_path
            print(f"Selected executable: {self.app.selected_executable}")

            self.executable_entry.configure(state="normal")
            self.executable_entry.delete(0, "end")
            self.executable_entry.insert(0, self.app.selected_executable)
            self.executable_entry.configure(state="readonly")    

    """
        Select the images directory using a file dialog and update the entry field with the selected path
    """
    def select_images_dir(self):
        directory_path = filedialog.askdirectory(
            title="Select Images Directory"
        )
        if directory_path:
            self.app.set_images_dir(directory_path)
            self.images_dir_var.set(directory_path)
            print(f"Selected images directory: {directory_path}")  

    def select_tests_dir(self):
        directory_path = filedialog.askdirectory(
            title = "Select Tests Directory"
        )
        if directory_path:
            self.tests_dir_var.set(directory_path)
            print(f"Selected tests directory: {directory_path}")

            self.app.select_tests_dir(directory_path)
            self.populate_test_list()
            self.reload_test_tabs() 

    """
    Select the theorical graph file using a file dialog and update the entry field with the selected path
    """
    def select_practical_graph_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Practical Graph File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.practical_graph_var.set(file_path)
            self.app.practical_graph_file = file_path
            print(f"[INFO] practical graph file set to: {file_path}")
            
            

    """
    Select the theorical graph file using a file dialog and update the entry field with the selected path
    """
    def select_theorical_graph_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Theoretical Graph File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.theorical_graph_var.set(file_path)
            self.app.theorical_graph_file = file_path 
            print(f"[INFO] Theoretical graph file set to: {file_path}")
            

    def reload_test_tabs(self):
        for i in reversed(range(self.app.tab_control.index("end"))):
            tab_text = self.app.tab_control.tab(i, "text")
            if tab_text not in self.app.tabs_to_keep:
                self.app.tab_control.forget(i)
        # Add new tests
        for test_class_name, test_class_ref in self.app.test_classes:
            self.app.add_test_tab(test_class_name, test_class_ref) 
 
    """
        Populate the test list with checkboxes for each test class found in the specified directory
        Each checkbox is associated with a test class reference
    """
    def populate_test_list(self):
        for widget in self.app.test_list_frame.winfo_children():
            widget.destroy()

        # Add each test as a checkbox
        for test_class_name, test_class_ref in self.app.test_classes:
            var = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(self.app.test_list_frame, text=test_class_name, variable=var)
            checkbox.pack(anchor="w", padx=5, pady=2)
            self.app.test_checkboxes[test_class_name] = (var, test_class_ref)

