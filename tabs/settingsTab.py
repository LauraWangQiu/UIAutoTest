from tab import Tabs

import customtkinter as ctk
from tkinter import filedialog
from stateResetMethod import StateResetMethod

class SettingsTab(Tabs):
    def __init__(self, parent, app_reference):
        super().__init__(parent, app_reference)

    def addTab(self):
        settings_tab = ctk.CTkFrame(self.app.tab_control)
        self.app.tab_control.add(settings_tab, text="Settings")

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
        self.java_path_var = ctk.StringVar(value=self.app.java_path if self.app.java_path else "java")
        java_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.java_path_var, width=400)
        java_entry.pack(fill="x", padx=10, pady=2)
        java_button = ctk.CTkButton(scrollable_frame, text="Select Java Executable", command=self.select_java_path)
        java_button.pack(padx=10, pady=5, anchor="w")

        sikulix_label = ctk.CTkLabel(scrollable_frame, text="SikuliX API Jar Path:", font=ctk.CTkFont(size=12))
        sikulix_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.sikulix_jar_var = ctk.StringVar(value=self.app.sikulix_jar)
        sikulix_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.sikulix_jar_var, width=400)
        sikulix_entry.pack(fill="x", padx=10, pady=2)
        sikulix_button = ctk.CTkButton(scrollable_frame, text="Select SikuliX Jar", command=self.select_sikulix_jar)
        sikulix_button.pack(padx=10, pady=5, anchor="w")

        practical_graph_label = ctk.CTkLabel(scrollable_frame, text="Practical Graph File to Export:", font=ctk.CTkFont(size=12))
        practical_graph_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.export_practical_graph_var = ctk.StringVar(value=self.app.practical_graph_file)
        self.export_practical_graph_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.export_practical_graph_var, width=400)
        self.export_practical_graph_entry.pack(fill="x", padx=10, pady=2)
        def on_export_practical_graph_change(*args):
            self.practical_graph_file = self.app.export_practical_graph_var.get()
        self.export_practical_graph_var.trace_add("write", lambda *args: on_export_practical_graph_change())

        # Executable Delay
        executable_delay_label = ctk.CTkLabel(scrollable_frame, text="Executable Delay (s):", font=ctk.CTkFont(size=12))
        executable_delay_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.executable_delay_var = ctk.StringVar(value=str(self.app.executable_delay))
        executable_delay_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.executable_delay_var, width=100)
        executable_delay_entry.pack(fill="x", padx=10, pady=2)
        def on_executable_delay_change(*args):
            value = self.executable_delay_var.get()
            if value.strip() == "":
                return
            try:
                self.app.executable_delay = int(value)
            except ValueError:
                pass
        self.executable_delay_var.trace_add("write", lambda *args: on_executable_delay_change())

        # Transition Delay
        transition_delay_label = ctk.CTkLabel(scrollable_frame, text="Transition Delay (s):", font=ctk.CTkFont(size=12))
        transition_delay_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.transition_delay_var = ctk.StringVar(value=str(self.app.transition_delay))
        transition_delay_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.transition_delay_var, width=100)
        transition_delay_entry.pack(fill="x", padx=10, pady=2)
        def on_transition_delay_change(*args):
            value = self.transition_delay_var.get()
            if value.strip() == "":
                return
            try:
                self.app.transition_delay = int(value)
            except ValueError:
                pass
        self.transition_delay_var.trace_add("write", lambda *args: on_transition_delay_change())

        # Debug Images (checkbox)
        self.debug_images_var = ctk.BooleanVar(value=self.app.debug_images)
        debug_images_checkbox = ctk.CTkCheckBox(scrollable_frame, text="Enable Debug Images", variable=self.debug_images_var)
        debug_images_checkbox.pack(anchor="w", padx=10, pady=(10, 2))
        def on_debug_images_change(*args):
            self.app.debug_images = self.debug_images_var.get()
        self.debug_images_var.trace_add("write", lambda *args: on_debug_images_change())

        # Timeout
        timeout_label = ctk.CTkLabel(scrollable_frame, text="Timeout (s):", font=ctk.CTkFont(size=12))
        timeout_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.timeout_var = ctk.StringVar(value=str(self.app.timeout))
        timeout_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.timeout_var, width=100)
        timeout_entry.pack(fill="x", padx=10, pady=2)
        def on_timeout_change(*args):
            value = self.timeout_var.get()
            if value.strip() == "":
                return
            try:
                self.app.timeout = int(value)
            except ValueError:
                pass
        self.timeout_var.trace_add("write", lambda *args: on_timeout_change())

        # Initial Similarity
        initial_similarity_label = ctk.CTkLabel(scrollable_frame, text="Initial Similarity (0-1):", font=ctk.CTkFont(size=12))
        initial_similarity_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.initial_similarity_var = ctk.StringVar(value=str(self.app.initial_similarity))
        initial_similarity_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.initial_similarity_var, width=100)
        initial_similarity_entry.pack(fill="x", padx=10, pady=2)
        def on_initial_similarity_change(*args):
            value = self.initial_similarity_var.get()
            if value.strip() == "":
                return
            try:
                val = float(value)
                if 0 <= val <= 1:
                    self.app.initial_similarity = val
            except ValueError:
                pass
        self.initial_similarity_var.trace_add("write", lambda *args: on_initial_similarity_change())

        # Min Similarity
        min_similarity_label = ctk.CTkLabel(scrollable_frame, text="Min Similarity (0-1):", font=ctk.CTkFont(size=12))
        min_similarity_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.min_similarity_var = ctk.StringVar(value=str(self.app.min_similarity))
        min_similarity_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.min_similarity_var, width=100)
        min_similarity_entry.pack(fill="x", padx=10, pady=2)
        def on_min_similarity_change(*args):
            value = self.min_similarity_var.get()
            if value.strip() == "":
                return
            try:
                val = float(value)
                if 0 <= val <= 1:
                    self.app.min_similarity = val
            except ValueError:
                pass
        self.min_similarity_var.trace_add("write", lambda *args: on_min_similarity_change())

        # Similarity Step
        similarity_step_label = ctk.CTkLabel(scrollable_frame, text="Similarity Step (0-1):", font=ctk.CTkFont(size=12))
        similarity_step_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.similarity_step_var = ctk.StringVar(value=str(self.app.similarity_step))
        similarity_step_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.similarity_step_var, width=100)
        similarity_step_entry.pack(fill="x", padx=10, pady=2)
        def on_similarity_step_change(*args):
            value = self.similarity_step_var.get()
            if value.strip() == "":
                return
            try:
                val = float(value)
                if 0 <= val <= 1:
                    self.app.similarity_step = val
            except ValueError:
                pass
        self.similarity_step_var.trace_add("write", lambda *args: on_similarity_step_change())

        # Retries
        retries_label = ctk.CTkLabel(scrollable_frame, text="Retries:", font=ctk.CTkFont(size=12))
        retries_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.retries_var = ctk.StringVar(value=str(self.app.retries))
        retries_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.retries_var, width=100)
        retries_entry.pack(fill="x", padx=10, pady=2)
        def on_retries_change(*args):
            value = self.retries_var.get()
            if value.strip() == "":
                return
            try:
                self.app.retries = int(value)
            except ValueError:
                pass
        self.retries_var.trace_add("write", lambda *args: on_retries_change())

        # Solution File
        solution_label = ctk.CTkLabel(scrollable_frame, text="Solution File:", font=ctk.CTkFont(size=12))
        solution_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.solution_var = ctk.StringVar(value=self.app.solution_file)
        self.solution_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.solution_var, width=400)
        self.solution_entry.pack(fill="x", padx=10, pady=2)
        def on_solution_change(*args):
            self.app.solution_file = self.solution_var.get()
        self.solution_var.trace_add("write", lambda *args: on_solution_change())

        # PDF Diff Export File Name
        pdf_route_label = ctk.CTkLabel(scrollable_frame, text="PDF Output File:", font=ctk.CTkFont(size=12))
        pdf_route_label.pack(anchor="w", padx=10, pady=(10, 2))
        self.pdf_route_var = ctk.StringVar(value=self.app.pdf_file)
        self.pdf_route_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.pdf_route_var, width=400)
        self.pdf_route_entry.pack(fill="x", padx=10, pady=2)
        def on_pdf_route_change(*args):
            self.app.pdf_file = self.pdf_route_var.get()
        self.pdf_route_var.trace_add("write", lambda *args: on_pdf_route_change())
        
        # State Reset Method
        state_reset_label = ctk.CTkLabel(scrollable_frame, text="State Reset Method:", font=ctk.CTkFont(size=12))
        state_reset_label.pack(anchor="w", padx=10, pady=(10, 2))
        reset_methods = [v for k, v in vars(StateResetMethod).items() if isinstance(v, str) and not k.startswith("__")]
        self.state_reset_method_var = ctk.StringVar(value=self.app.state_reset_method)
        state_reset_menu = ctk.CTkOptionMenu(
            scrollable_frame,
            values=reset_methods,
            variable=self.state_reset_method_var
        )
        state_reset_menu.pack(fill="x", padx=10, pady=2)

        # Space to select the external reset script if the method is EXTERNAL_RESET
        self.external_reset_script_var = ctk.StringVar(value=self.app.external_reset_script)
        self.external_reset_script_entry = ctk.CTkEntry(scrollable_frame, textvariable=self.external_reset_script_var, width=400)
        def select_external_reset_script():
            file_path = filedialog.askopenfilename(
                title="Select External Reset Script",
                filetypes=[("Executables", "*.exe;*.bat;*.sh;*.py"), ("All Files", "*.*")]
            )
            if file_path:
                self.external_reset_script_var.set(file_path)
                self.app.external_reset_script = file_path
        self.external_reset_script_button = ctk.CTkButton(scrollable_frame, text="Select External Reset Script", command=select_external_reset_script)

        def update_external_reset_visibility(*args):
            self.app.state_reset_method = self.state_reset_method_var.get()
            if self.app.state_reset_method == StateResetMethod.EXTERNAL_RESET:
                self.external_reset_script_entry.pack(fill="x", padx=10, pady=2)
                self.external_reset_script_button.pack(padx=10, pady=2, anchor="w")
            else:
                self.external_reset_script_entry.pack_forget()
                self.external_reset_script_button.pack_forget()
        self.state_reset_method_var.trace_add("write", update_external_reset_visibility)
        self.external_reset_script_var.trace_add("write", lambda *args: setattr(self, "external_reset_script", self.external_reset_script_var.get()))
        update_external_reset_visibility()

    def select_java_path(self):
        file_path = filedialog.askopenfilename(
            title="Select Java Executable",
            filetypes=[("Java Executable", "java.exe;java"), ("All Files", "*.*")]
        )
        if file_path:
            self.java_path_var.set(file_path)
            self.app.java_path = file_path
            print(f"[INFO] Java path set to: {file_path}")

            
    def select_sikulix_jar(self):
        file_path = filedialog.askopenfilename(
            title="Select SikuliX API Jar",
            filetypes=[("Jar Files", "*.jar"), ("All Files", "*.*")]
        )
        if file_path:
            self.sikulix_jar_var.set(file_path)
            self.app.sikulix_jar = file_path
            print(f"[INFO] SikuliX jar path set to: {file_path}")        
            
    def select_jython_jar(self):
        file_path = filedialog.askopenfilename(
            title="Select Jython Jar",
            filetypes=[("Jar Files", "*.jar"), ("All Files", "*.*")]
        )
        if file_path:
            self.jython_jar_var.set(file_path)
            self.app.jython_jar = file_path
            print(f"[INFO] Jython jar path set to: {file_path}")        