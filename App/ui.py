﻿import customtkinter as ctk
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

        # Available functions - easy to modify
        self.functions = {
            "f(x) = x²": lambda x: x**2,
            "f(x) = sin(x)": lambda x: np.sin(x),
            "f(x) = e^x": lambda x: np.exp(x),
            "f(x) = 1/x": lambda x: 1/x,
            "f(x) = x³ - 2x² + 2": lambda x: x**3 - 2*x**2 + 2
        }

        # Configure grid layout
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

        # Initialize with default function after everything is created
        self.on_function_select(list(self.functions.keys())[0])

    def create_control_panel(self):
        """Create the left control panel with all the UI elements."""
        # Control panel frame
        self.control_frame = ctk.CTkFrame(self.root)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Title
        ctk.CTkLabel(self.control_frame, text="Darboux Sums", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)

        # Function selection
        ctk.CTkLabel(self.control_frame, text="Select Function:", font=ctk.CTkFont(size=16)).pack(pady=(10, 5))
        self.function_var = ctk.StringVar(value=list(self.functions.keys())[0])
        self.function_menu = ctk.CTkOptionMenu(
            self.control_frame,
            values=list(self.functions.keys()),
            variable=self.function_var,
            command=self.on_function_select,
            font=ctk.CTkFont(size=14)
        )
        self.function_menu.pack(pady=(0, 10), fill="x", padx=20)

        # Interval settings
        interval_frame = ctk.CTkFrame(self.control_frame)
        interval_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(interval_frame, text="Interval:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=5, pady=5)

        # Lower bound
        ctk.CTkLabel(interval_frame, text="a =", font=ctk.CTkFont(size=14)).grid(row=0, column=1, padx=5, pady=5)
        self.a_entry = ctk.CTkEntry(interval_frame, width=60, font=ctk.CTkFont(size=14))
        self.a_entry.insert(0, "0")
        self.a_entry.grid(row=0, column=2, padx=5, pady=5)

        # Upper bound
        ctk.CTkLabel(interval_frame, text="b =", font=ctk.CTkFont(size=14)).grid(row=0, column=3, padx=5, pady=5)
        self.b_entry = ctk.CTkEntry(interval_frame, width=60, font=ctk.CTkFont(size=14))
        self.b_entry.insert(0, "1")
        self.b_entry.grid(row=0, column=4, padx=5, pady=5)

        # Max points setting
        ctk.CTkLabel(self.control_frame, text="Maximum Number of Points:", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        self.max_points_entry = ctk.CTkEntry(self.control_frame, width=100, font=ctk.CTkFont(size=14))
        self.max_points_entry.insert(0, "15")
        self.max_points_entry.pack(pady=(0, 10))

        # Animation speed
        ctk.CTkLabel(self.control_frame, text="Animation Speed:", font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        self.speed_slider = ctk.CTkSlider(
            self.control_frame,
            from_=100,
            to=2000,
            number_of_steps=19,
            command=self.on_speed_change
        )
        self.speed_slider.set(500)  # Default speed
        self.speed_slider.pack(pady=(0, 10), fill="x", padx=20)

        # Speed label
        self.speed_label = ctk.CTkLabel(self.control_frame, text="500 ms", font=ctk.CTkFont(size=14))
        self.speed_label.pack(pady=(0, 10))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.control_frame)
        buttons_frame.pack(fill="x", pady=10, padx=20)

        # Start button
        self.start_button = ctk.CTkButton(
            buttons_frame,
            text="Start Animation",
            command=self.start_visualization,
            font=ctk.CTkFont(size=14),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        # Reset button
        self.reset_button = ctk.CTkButton(
            buttons_frame,
            text="Reset",
            command=self.reset_visualization,
            font=ctk.CTkFont(size=14),
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.reset_button.grid(row=0, column=1, padx=5, pady=5)

        # Results display
        self.results_frame = ctk.CTkFrame(self.control_frame, corner_radius=10)
        self.results_frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(self.results_frame, text="Results", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 15))

        # Create a results display frame
        results_display = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        results_display.pack(fill="x", padx=15, pady=(0, 15))

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

        # Configure grid to make labels align properly
        results_display.grid_columnconfigure(0, weight=1)
        results_display.grid_columnconfigure(1, weight=1)

    def create_graph_panel(self):
        """Create the right panel with the matplotlib graph."""
        # Graph panel frame
        self.graph_frame = ctk.CTkFrame(self.root)
        self.graph_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Create canvas using the previously initialized figure
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)

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

        # Center the window
        error_window.update_idletasks()
        width = error_window.winfo_width()
        height = error_window.winfo_height()
        x = (error_window.winfo_screenwidth() // 2) - (width // 2)
        y = (error_window.winfo_screenheight() // 2) - (height // 2)
        error_window.geometry(f'{width}x{height}+{x}+{y}')

    def animation_step(self, max_points):
        """Perform one step of the animation."""
        if not self.animation_running:
            return

        # Add a new point
        self.current_points, self.details = calculate_add_point(
            self.current_points,
            self.selected_function,
            self.details
        )

        # Update the plot
        update_plot(
            self.ax,
            self.selected_function,
            self.current_points,
            self.details['lower_sum'],
            self.details['upper_sum']
        )
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