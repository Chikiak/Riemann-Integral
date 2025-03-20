import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors
import colorsys

def plot_function_with_darboux_sums(ax, func, points, lower_sum, upper_sum):
    """
    Create a visualization of a function with its Darboux sums.
    
    :param ax: Matplotlib axes to plot on
    :param func: The function to visualize
    :param points: The partition points
    :param lower_sum: Current lower Darboux sum
    :param upper_sum: Current upper Darboux sum
    """
    # Clear the previous plot
    ax.clear()

    # Calculate the range for plotting
    x_min, x_max = min(points), max(points)
    x_padding = 0.05 * (x_max - x_min)
    x_plot = np.linspace(x_min - x_padding, x_max + x_padding, 1000)

    # Calculate y range for better plotting
    y_plot = func(x_plot)
    y_min, y_max = min(min(y_plot), 0), max(y_plot)  # Ensure 0 is included for better visualization
    y_padding = 0.1 * (y_max - y_min)

    # Set fixed colors for lower and upper rectangles - using solid colors now
    lower_color = '#00C4CC'  
    upper_color = '#2A0944'  

    # Draw rectangles for each subinterval with proper stacking
    for i in range(len(points) - 1):
        a, b = points[i], points[i+1]
        delta_x = b - a

        # Calculate min and max values in this subinterval
        x_values = np.linspace(a, b, 100)
        y_values = func(x_values)
        min_val = np.min(y_values)
        max_val = np.max(y_values)

        # Determine the drawing order based on whether the function is positive or negative
        if min_val >= 0:  # Function is positive
            # Draw upper rectangle first (will be underneath)
            upper_rect = Rectangle(
                (a, 0), delta_x, max_val,
                alpha=1.0, color=upper_color,  # Solid color (alpha=1.0)
                edgecolor='black', linewidth=1,
                label='Upper Sum' if i == 0 else ""
            )
            ax.add_patch(upper_rect)

            # Draw lower rectangle second (will be on top)
            lower_rect = Rectangle(
                (a, 0), delta_x, min_val,
                alpha=1.0, color=lower_color,  # Solid color
                edgecolor='black', linewidth=1,
                label='Lower Sum' if i == 0 else ""
            )
            ax.add_patch(lower_rect)
        elif max_val <= 0:  # Function is negative
            # Draw lower rectangle first (will be underneath)
            lower_rect = Rectangle(
                (a, 0), delta_x, min_val,
                alpha=1.0, color=lower_color,  # Solid color
                edgecolor='black', linewidth=1,
                label='Lower Sum' if i == 0 else ""
            )
            ax.add_patch(lower_rect)

            # Draw upper rectangle second (will be on top)
            upper_rect = Rectangle(
                (a, 0), delta_x, max_val,
                alpha=1.0, color=upper_color,  # Solid color
                edgecolor='black', linewidth=1,
                label='Upper Sum' if i == 0 else ""
            )
            ax.add_patch(upper_rect)
        else:  # Function crosses zero
            # For negative part
            upper_rect_neg = Rectangle(
                (a, 0), delta_x, max_val if max_val <= 0 else 0,
                alpha=1.0, color=upper_color,
                edgecolor='black', linewidth=1,
                label='Upper Sum' if i == 0 else ""
            )
            lower_rect_neg = Rectangle(
                (a, 0), delta_x, min_val,
                alpha=1.0, color=lower_color,
                edgecolor='black', linewidth=1,
                label='Lower Sum' if i == 0 else ""
            )

            # For positive part
            upper_rect_pos = Rectangle(
                (a, 0), delta_x, max_val,
                alpha=1.0, color=upper_color,
                edgecolor='black', linewidth=1
            )
            lower_rect_pos = Rectangle(
                (a, 0), delta_x, min_val if min_val >= 0 else 0,
                alpha=1.0, color=lower_color,
                edgecolor='black', linewidth=1
            )

            # Add in correct order
            if max_val > 0:
                ax.add_patch(upper_rect_pos)
            if min_val < 0:
                ax.add_patch(lower_rect_neg)
                ax.add_patch(upper_rect_neg)
            if min_val >= 0:
                ax.add_patch(lower_rect_pos)

    # Plot the function on top of the rectangles
    ax.plot(x_plot, y_plot, color='#3a86ff', label='f(x)', linewidth=2.5)

    # Plot the partition points
    ax.plot(points, [0] * len(points), 'o', color='#ffd166', markersize=7)

    # Set plot limits and labels
    ax.set_xlim(x_min - x_padding, x_max + x_padding)
    ax.set_ylim(min(0, y_min - y_padding), y_max + y_padding)

    ax.set_title('Darboux Sums Visualization', color='white', fontsize=16)
    ax.set_xlabel('x', color='white', fontsize=12)
    ax.set_ylabel('f(x)', color='white', fontsize=12)

    # Add legend with custom styling
    legend = ax.legend(loc='upper right', framealpha=0.8)
    plt.setp(legend.get_texts(), color='white')

    # Add text showing current sums with improved styling
    info_text = (
        f'Points: {len(points)}\n'
        f'Lower Sum: {lower_sum:.6f}\n'
        f'Upper Sum: {upper_sum:.6f}\n'
        f'Difference: {upper_sum - lower_sum:.6f}'
    )

    text_box = ax.text(
        0.02, 0.95, info_text,
        transform=ax.transAxes,
        bbox=dict(facecolor='#2b2b2b', alpha=0.9, boxstyle='round,pad=0.5',
                  edgecolor='#3a86ff', linewidth=2),
        color='white',
        fontsize=10,
        verticalalignment='top',
        fontweight='bold'
    )

    # Draw vertical lines at partition points
    for point in points:
        ax.axvline(x=point, color='gray', linestyle='--', alpha=0.4)

    # Customize ticks
    ax.tick_params(colors='white')

    # Customize spines
    for spine in ax.spines.values():
        spine.set_color('gray')

    # Add grid
    ax.grid(True, alpha=0.3, color='gray')

def update_plot(ax, func, points, lower_sum, upper_sum):
    """
    Update the existing plot with new partition data.
    
    :param ax: Matplotlib axes to update
    :param func: The function being visualized
    :param points: Updated partition points
    :param lower_sum: Updated lower Darboux sum
    :param upper_sum: Updated upper Darboux sum
    """
    # Reuse the same plotting function for consistency
    plot_function_with_darboux_sums(ax, func, points, lower_sum, upper_sum)