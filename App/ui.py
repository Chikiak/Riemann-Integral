import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from calculations import calculate_darboux_sums, calculate_add_point
from visualization import plot_function_with_darboux_sums, update_plot

class InteractiveApp:
    def __init__(self, root):
        """Initialize the application with UI components."""
        self.root = root
        self.root.title("Interactive Darboux Sums Visualizer")
        self.root.geometry("1200x800")

        # Make the app responsive to window resizing
        self.root.minsize(800, 600)  # Minimum window size

        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Set default values
        self.selected_function = None
        self.a_value = 0
        self.b_value = 1
        self.max_points = 15
        self.current_points = []
        self.animation_speed = 500  # milliseconds
        self.details = {}
        self.animation_running = False
        self.partition_type = "random"  # Default partition type

        # Available functions - easy to modify
        self.functions = {
            "f(x) = x²": lambda x: x**2,
            "f(x) = sin(x)": lambda x: np.sin(x),
            "f(x) = e^x * sin(x) + x²": lambda x: np.exp(x) * np.sin(x) + x**2,
            "f(x) = 1/x": lambda x: 1/x,
            "f(x) = x³ - 2x² + 2": lambda x: x**3 - 2*x**2 + 2
        }

        # Configure grid layout with proper weights for responsiveness
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=4)
        self.root.grid_rowconfigure(0, weight=1)

        # Create matplotlib figure and canvas first with dark theme
        plt.style.use('dark_background')
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.figure.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')

        # Create frames
        self.create_control_panel()
        self.create_graph_panel()

        # Configure resize event binding
        self.root.bind("<Configure>", self.on_window_resize)

        # Initialize with default function after everything is created
        self.on_function_select(list(self.functions.keys())[0])

    def on_window_resize(self, event):
        """Handle window resize event"""
        # Only respond if it's the main window being resized
        if event.widget == self.root:
            # Redraw the canvas to adapt to new size
            self.canvas.draw()

            # Adjust font sizes based on window width
            new_window_width = event.width
            if new_window_width < 1000:
                # Smaller fonts for smaller windows
                self.update_font_sizes("small")
            elif new_window_width < 1400:
                # Medium fonts for medium windows
                self.update_font_sizes("medium")
            else:
                # Larger fonts for larger windows
                self.update_font_sizes("large")

    def update_font_sizes(self, size):
        """Update font sizes based on window size"""
        if size == "small":
            title_size = 18
            label_size = 12
            button_size = 12
        elif size == "medium":
            title_size = 20
            label_size = 14
            button_size = 14
        else:  # large
            title_size = 22
            label_size = 16
            button_size = 16
    
        # Update main title font
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text") == "Darboux Sums":
                widget.configure(font=ctk.CTkFont(size=title_size, weight="bold"))
                break

    def create_control_panel(self):
        """Create the left control panel with all the UI elements."""
        # Control panel frame
        self.control_frame = ctk.CTkFrame(self.root)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
        # Configure internal grid for responsiveness
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_rowconfigure(0, weight=1)  # Make the scrollable frame expandable
    
        # Create scrollable frame for all controls
        self.scrollable_frame = ctk.CTkScrollableFrame(self.control_frame)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
    
        # Title
        ctk.CTkLabel(self.scrollable_frame, text="Darboux Sums", font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, pady=10, sticky="ew")
    
        # Function selection
        function_select_frame = ctk.CTkFrame(self.scrollable_frame)
        function_select_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        function_select_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(function_select_frame, text="Select Function:", font=ctk.CTkFont(size=16)).grid(
            row=0, column=0, pady=(5, 0), sticky="w")

        self.function_var = ctk.StringVar(value=list(self.functions.keys())[0])
        self.function_menu = ctk.CTkOptionMenu(
            function_select_frame,
            values=list(self.functions.keys()),
            variable=self.function_var,
            command=self.on_function_select,
            font=ctk.CTkFont(size=14)
        )
        self.function_menu.grid(row=1, column=0, pady=(0, 5), sticky="ew", padx=5)

        # Interval settings
        interval_frame = ctk.CTkFrame(self.scrollable_frame)
        interval_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        interval_frame.grid_columnconfigure(0, weight=1)
        interval_frame.grid_columnconfigure(2, weight=1)
        interval_frame.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(interval_frame, text="Interval:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, columnspan=5, padx=5, pady=5, sticky="w")

        # Lower bound
        ctk.CTkLabel(interval_frame, text="a =", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, padx=5, pady=5, sticky="e")
        self.a_entry = ctk.CTkEntry(interval_frame, width=60, font=ctk.CTkFont(size=14))
        self.a_entry.insert(0, "0")
        self.a_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Upper bound
        ctk.CTkLabel(interval_frame, text="b =", font=ctk.CTkFont(size=14)).grid(
            row=1, column=3, padx=5, pady=5, sticky="e")
        self.b_entry = ctk.CTkEntry(interval_frame, width=60, font=ctk.CTkFont(size=14))
        self.b_entry.insert(0, "1")
        self.b_entry.grid(row=1, column=4, padx=5, pady=5, sticky="w")

        # Partition type selection
        partition_frame = ctk.CTkFrame(self.scrollable_frame)
        partition_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        partition_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(partition_frame, text="Partition Type:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, padx=5, pady=5, sticky="w")

        # Radio buttons for partition type
        self.partition_var = ctk.StringVar(value="random")

        partition_radio_frame = ctk.CTkFrame(partition_frame, fg_color="transparent")
        partition_radio_frame.grid(row=1, column=0, sticky="ew")
        partition_radio_frame.grid_columnconfigure(0, weight=1)
        partition_radio_frame.grid_columnconfigure(1, weight=1)

        random_radio = ctk.CTkRadioButton(
            partition_radio_frame,
            text="Random",
            variable=self.partition_var,
            value="random",
            font=ctk.CTkFont(size=14)
        )
        random_radio.grid(row=0, column=0, padx=20, pady=5, sticky="w")

        equidistant_radio = ctk.CTkRadioButton(
            partition_radio_frame,
            text="Equidistant",
            variable=self.partition_var,
            value="equidistant",
            font=ctk.CTkFont(size=14)
        )
        equidistant_radio.grid(row=0, column=1, padx=20, pady=5, sticky="w")

        # Max points setting
        max_points_frame = ctk.CTkFrame(self.scrollable_frame)
        max_points_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        max_points_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(max_points_frame, text="Maximum Number of Points:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, padx=5, pady=(5, 0), sticky="w")

        self.max_points_entry = ctk.CTkEntry(max_points_frame, width=100, font=ctk.CTkFont(size=14))
        self.max_points_entry.insert(0, "15")
        self.max_points_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Max points hint
        max_points_hint = ctk.CTkLabel(
            max_points_frame,
            text="(Maximum limit: 1000 points)",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        max_points_hint.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="w")

        # Animation speed
        speed_frame = ctk.CTkFrame(self.scrollable_frame)
        speed_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        speed_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(speed_frame, text="Animation Speed:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, padx=5, pady=(5, 0), sticky="w")

        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=2000,  # Inverted range: slow (left) to fast (right)
            to=50,
            number_of_steps=39,
            command=self.on_speed_change
        )
        self.speed_slider.set(500)  # Default speed
        self.speed_slider.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Speed labels
        speed_labels_frame = ctk.CTkFrame(speed_frame, fg_color="transparent")
        speed_labels_frame.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="ew")
        speed_labels_frame.grid_columnconfigure(0, weight=1)
        speed_labels_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(speed_labels_frame, text="Slow", font=ctk.CTkFont(size=12), text_color="gray").grid(
            row=0, column=0, sticky="w")

        self.speed_label = ctk.CTkLabel(speed_labels_frame, text=f"{self.animation_speed} ms", font=ctk.CTkFont(size=12))
        self.speed_label.grid(row=0, column=1)

        ctk.CTkLabel(speed_labels_frame, text="Fast", font=ctk.CTkFont(size=12), text_color="gray").grid(
            row=0, column=2, sticky="e")

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.scrollable_frame)
        buttons_frame.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)

        # Start button
        self.start_button = ctk.CTkButton(
            buttons_frame,
            text="Start Animation",
            command=self.start_visualization,
            font=ctk.CTkFont(size=14),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Reset button
        self.reset_button = ctk.CTkButton(
            buttons_frame,
            text="Reset",
            command=self.reset_visualization,
            font=ctk.CTkFont(size=14),
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.reset_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Results display
        self.results_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=10)
        self.results_frame.grid(row=7, column=0, padx=10, pady=5, sticky="nsew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.results_frame, text="Results", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, pady=(10, 5), sticky="ew")

        # Create a results display frame
        results_display = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        results_display.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        results_display.grid_columnconfigure(0, weight=1)
        results_display.grid_columnconfigure(1, weight=1)

        # Current points count with better styling
        points_label_text = ctk.CTkLabel(results_display, text="Number of Points:",
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         anchor="w")
        points_label_text.grid(row=0, column=0, sticky="w", pady=5)

        self.points_label = ctk.CTkLabel(results_display, text="0",
                                         font=ctk.CTkFont(size=14),
                                         anchor="e")
        self.points_label.grid(row=0, column=1, sticky="e", pady=5)

        # Lower sum with better styling
        lower_label_text = ctk.CTkLabel(results_display, text="Lower Sum:",
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        anchor="w")
        lower_label_text.grid(row=1, column=0, sticky="w", pady=5)

        self.lower_sum_label = ctk.CTkLabel(results_display, text="0.000000",
                                            font=ctk.CTkFont(size=14),
                                            anchor="e")
        self.lower_sum_label.grid(row=1, column=1, sticky="e", pady=5)

        # Upper sum with better styling
        upper_label_text = ctk.CTkLabel(results_display, text="Upper Sum:",
                                        font=ctk.CTkFont(size=14, weight="bold"),
                                        anchor="w")
        upper_label_text.grid(row=2, column=0, sticky="w", pady=5)

        self.upper_sum_label = ctk.CTkLabel(results_display, text="0.000000",
                                            font=ctk.CTkFont(size=14),
                                            anchor="e")
        self.upper_sum_label.grid(row=2, column=1, sticky="e", pady=5)

        # Difference with better styling and highlight
        diff_label_text = ctk.CTkLabel(results_display, text="Difference:",
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       anchor="w")
        diff_label_text.grid(row=3, column=0, sticky="w", pady=5)

        self.diff_label = ctk.CTkLabel(results_display, text="0.000000",
                                       font=ctk.CTkFont(size=14),
                                       text_color="#3a86ff",
                                       anchor="e")
        self.diff_label.grid(row=3, column=1, sticky="e", pady=5)

    def create_graph_panel(self):
        """Create the right panel with the matplotlib graph."""
        # Graph panel frame
        self.graph_frame = ctk.CTkFrame(self.root)
        self.graph_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.graph_frame.grid_columnconfigure(0, weight=1)
        self.graph_frame.grid_rowconfigure(0, weight=1)

        # Create canvas using the previously initialized figure
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Configure tight layout for better responsiveness in the plot
        self.figure.tight_layout()

    def on_function_select(self, function_name):
        """Handle function selection."""
        self.selected_function = self.functions[function_name]
        # If we're not in an animation, update the preview
        if not self.animation_running and hasattr(self, 'ax'):
            try:
                a = float(self.a_entry.get())
                b = float(self.b_entry.get())
                # Just show the function
                self.ax.clear()
                x = np.linspace(a, b, 1000)
                self.ax.plot(x, self.selected_function(x), color='#3a86ff', linewidth=2)
                self.ax.set_title(f"Function: {function_name}", color='white', fontsize=14)
                self.ax.grid(True, alpha=0.3, color='gray')
                self.ax.tick_params(colors='white')
                for spine in self.ax.spines.values():
                    spine.set_color('gray')
                # Use tight layout to ensure proper display
                self.figure.tight_layout()
                self.canvas.draw()
            except (ValueError, AttributeError):
                pass

    def on_speed_change(self, value):
        """Handle animation speed change."""
        self.animation_speed = int(value)
        self.speed_label.configure(text=f"{self.animation_speed} ms")

    def start_visualization(self):
        """Start the Darboux sums visualization."""
        try:
            # Get values from input fields
            a = float(self.a_entry.get())
            b = float(self.b_entry.get())
            max_points = int(self.max_points_entry.get())

            # Enforce maximum point limit
            if max_points > 1000:
                max_points = 1000
                self.max_points_entry.delete(0, 'end')
                self.max_points_entry.insert(0, "1000")

            # Check valid input
            if a >= b:
                self.show_error("Upper bound must be greater than lower bound")
                return

            if max_points < 2:
                self.show_error("Maximum points must be at least 2")
                return

            # Start animation
            self.animation_running = True
            self.start_button.configure(state="disabled")
            self.function_menu.configure(state="disabled")
            self.a_entry.configure(state="disabled")
            self.b_entry.configure(state="disabled")
            self.max_points_entry.configure(state="disabled")

            # Store partition type
            self.partition_type = self.partition_var.get()

            # Initial partition with just end points
            self.current_points = [a, b]
            self.current_points.sort()

            # Calculate initial sums
            self.current_points, self.details = calculate_darboux_sums(self.current_points, self.selected_function)

            # Initial plot
            plot_function_with_darboux_sums(
                self.ax,
                self.selected_function,
                self.current_points,
                self.details['lower_sum'],
                self.details['upper_sum']
            )
            # Use tight layout for proper display
            self.figure.tight_layout()
            self.canvas.draw()

            # Update labels
            self.update_results_display()

            # Schedule next step
            if len(self.current_points) < max_points:
                self.root.after(self.animation_speed, self.animation_step, max_points)
            else:
                self.animation_complete()

        except ValueError as e:
            self.show_error(f"Invalid input: {str(e)}")
            self.animation_running = False
            self.start_button.configure(state="normal")
            self.function_menu.configure(state="normal")
            self.a_entry.configure(state="normal")
            self.b_entry.configure(state="normal")
            self.max_points_entry.configure(state="normal")

    def show_error(self, message):
        """Show an error message box with custom styling."""
        error_window = ctk.CTkToplevel(self.root)
        error_window.title("Error")
        error_window.geometry("400x150")
        error_window.resizable(False, False)

        # Make it modal
        error_window.transient(self.root)
        error_window.grab_set()

        # Center dialog on parent window
        width = 400
        height = 150
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        error_window.geometry(f'{width}x{height}+{x}+{y}')

        # Message
        ctk.CTkLabel(error_window, text=message, font=ctk.CTkFont(size=14)).pack(pady=(20, 10))

        # OK button
        ctk.CTkButton(
            error_window,
            text="OK",
            command=error_window.destroy,
            width=100,
            font=ctk.CTkFont(size=14),
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(pady=(10, 20))

    def animation_step(self, max_points):
        """Perform one step of the animation."""
        if not self.animation_running:
            return

        # Add a new point based on partition type
        if self.partition_type == "random":
            # Random partition - add point to largest subinterval
            self.current_points, self.details = calculate_add_point(
                self.current_points,
                self.selected_function,
                self.details
            )
        else:
            # Equidistant partition
            a = min(self.current_points)
            b = max(self.current_points)
            n = len(self.current_points)
            # Create equidistant points
            equidistant_points = [a + i * (b - a) / (n) for i in range(n + 1)]
            self.current_points = equidistant_points
            # Recalculate the sums
            self.current_points, self.details = calculate_darboux_sums(
                self.current_points,
                self.selected_function
            )

        # Update the plot
        update_plot(
            self.ax,
            self.selected_function,
            self.current_points,
            self.details['lower_sum'],
            self.details['upper_sum']
        )
        # Ensure tight layout on updates
        self.figure.tight_layout()
        self.canvas.draw()

        # Update results display
        self.update_results_display()

        # Schedule next step or finish
        if len(self.current_points) < max_points:
            self.root.after(self.animation_speed, self.animation_step, max_points)
        else:
            self.animation_complete()

    def animation_complete(self):
        """Handle animation completion."""
        self.animation_running = False
        self.start_button.configure(state="normal")
        self.function_menu.configure(state="normal")
        self.a_entry.configure(state="normal")
        self.b_entry.configure(state="normal")
        self.max_points_entry.configure(state="normal")

    def reset_visualization(self):
        """Reset the visualization."""
        if self.animation_running:
            self.animation_running = False

        # Reset UI elements
        self.start_button.configure(state="normal")
        self.function_menu.configure(state="normal")
        self.a_entry.configure(state="normal")
        self.b_entry.configure(state="normal")
        self.max_points_entry.configure(state="normal")

        # Clear graph
        self.ax.clear()
        try:
            a = float(self.a_entry.get())
            b = float(self.b_entry.get())
            x = np.linspace(a, b, 1000)
            self.ax.plot(x, self.selected_function(x), color='#3a86ff', linewidth=2)
            self.ax.set_title(f"Function: {self.function_var.get()}", color='white', fontsize=14)
            self.ax.grid(True, alpha=0.3, color='gray')
            self.ax.tick_params(colors='white')
            for spine in self.ax.spines.values():
                spine.set_color('gray')
            # Apply tight layout on reset
            self.figure.tight_layout()
            self.canvas.draw()
        except ValueError:
            pass

        # Reset data
        self.current_points = []
        self.details = {}

        # Reset result labels
        self.points_label.configure(text="0")
        self.lower_sum_label.configure(text="0.000000")
        self.upper_sum_label.configure(text="0.000000")
        self.diff_label.configure(text="0.000000")

    def update_results_display(self):
        """Update the results display with current values."""
        lower_sum = self.details.get('lower_sum', 0)
        upper_sum = self.details.get('upper_sum', 0)
        diff = upper_sum - lower_sum

        # Update with formatted numbers
        self.points_label.configure(text=f"{len(self.current_points)}")
        self.lower_sum_label.configure(text=f"{lower_sum:.6f}")
        self.upper_sum_label.configure(text=f"{upper_sum:.6f}")
        self.diff_label.configure(text=f"{diff:.6f}")