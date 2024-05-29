import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

def select_file():
    global filepath
    filepath = filedialog.askopenfilename(filetypes=[("STL Files", "*.stl")])
    if filepath:
        file_label.config(text=f"Selected file: {os.path.basename(filepath)}")
    else:
        file_label.config(text="No file selected")

def rotate_model(axis, direction):
    global rotations
    if axis not in rotations:
        rotations[axis] = 0
    rotations[axis] += 90 * direction
    success_label.config(text=f"Rotated {axis.upper()} by {90 * direction} degrees.", fg="blue")

def reset_rotation():
    global rotations
    rotations = {'x': 0, 'y': 0, 'z': 0}
    success_label.config(text="Rotations reset to default (0 degrees for all axes).", fg="blue")

def update_quality_mode(*args):
    quality_mode = quality_mode_var.get()
    if quality_mode == "Draft":
        layer_height_entry.delete(0, tk.END)
        layer_height_entry.insert(0, "0.3")
        infill_density_entry.delete(0, tk.END)
        infill_density_entry.insert(0, "10")
        print_speed_entry.delete(0, tk.END)
        print_speed_entry.insert(0, "80")
    elif quality_mode == "Normal":
        layer_height_entry.delete(0, tk.END)
        layer_height_entry.insert(0, "0.2")
        infill_density_entry.delete(0, tk.END)
        infill_density_entry.insert(0, "20")
        print_speed_entry.delete(0, tk.END)
        print_speed_entry.insert(0, "60")
    elif quality_mode == "High Quality":
        layer_height_entry.delete(0, tk.END)
        layer_height_entry.insert(0, "0.1")
        infill_density_entry.delete(0, tk.END)
        infill_density_entry.insert(0, "30")
        print_speed_entry.delete(0, tk.END)
        print_speed_entry.insert(0, "40")

def slice_model():
    if not filepath:
        success_label.config(text="Please select an STL file first.", fg="red")
        return

    try:
        layer_height = float(layer_height_entry.get())
        infill_density = int(infill_density_entry.get())
        print_speed = float(print_speed_entry.get())

        if not (0 <= infill_density <= 100):
            raise ValueError("Infill density out of range")
    except ValueError as e:
        success_label.config(text=f"Invalid input: {e}. Please enter valid numbers within the acceptable range.", fg="red")
        return

    output_file = filedialog.asksaveasfilename(defaultextension=".gcode", filetypes=[("G-code Files", "*.gcode")])
    if not output_file:
        success_label.config(text="Slicing canceled.", fg="red")
        return

    prusa_slicer_path = "C:\\Users\\91700\\Desktop\\PrusaSlicer-2.7.4+win64-202404050928\\prusa-slicer.exe"
    config_file_path = "C:\\Users\\91700\\Desktop\\Kreator3D Assignment\\my_config.ini"

    with open(config_file_path, 'w') as config_file:
        config_file.write(f"layer_height = {layer_height}\n")
        config_file.write(f"fill_density = {infill_density}%\n")
        config_file.write(f"speed_print = {print_speed}\n")
        for axis, angle in rotations.items():
            config_file.write(f"rotate_{axis} = {angle}\n")

    with open(config_file_path, 'r') as config_file:
        print("Configuration file contents:")
        print(config_file.read())

    prusa_command = f"\"{prusa_slicer_path}\" --slice --export-gcode --load \"{config_file_path}\" \"{filepath}\" --output \"{output_file}\""
    try:
        subprocess.run(prusa_command, shell=True, check=True)
        success_label.config(text=f"Slicing completed! G-code saved as {os.path.basename(output_file)}.", fg="green")
    except subprocess.CalledProcessError as e:
        success_label.config(text="Error during slicing. Please check the console for details.", fg="red")
        print(f"Error: {e}")

# Create Tkinter window
root = tk.Tk()
root.title("Automated Slicing Tool")
root.geometry("500x600")
root.configure(bg='#f7f7f7')

# Global variables to store the selected file path and rotations
filepath = None
rotations = {'x': 0, 'y': 0, 'z': 0}

# Create a frame for the file selection
frame_file = tk.Frame(root, bg='#e0e0e0', pady=10, padx=10, bd=2, relief="groove")
frame_file.pack(fill='x', pady=10, padx=10)

file_button = tk.Button(frame_file, text="Select 3D Model", command=select_file, bg='#007acc', fg='white', relief='flat')
file_button.pack(side='left')
file_label = tk.Label(frame_file, text="No file selected", bg='#e0e0e0')
file_label.pack(side='left', padx=10)

# Create a frame for the slicing parameters
frame_params = tk.Frame(root, bg='#f0f0f0', pady=10, padx=10, bd=2, relief="groove")
frame_params.pack(fill='x', pady=10, padx=10)

layer_height_label = tk.Label(frame_params, text="Layer Height (mm):", bg='#f0f0f0')
layer_height_label.grid(row=0, column=0, pady=5, sticky='e')
layer_height_entry = tk.Entry(frame_params)
layer_height_entry.insert(0, "0.2")  # Default value
layer_height_entry.grid(row=0, column=1, pady=5, padx=5)

infill_density_label = tk.Label(frame_params, text="Infill Density (%):", bg='#f0f0f0')
infill_density_label.grid(row=1, column=0, pady=5, sticky='e')
infill_density_entry = tk.Entry(frame_params)
infill_density_entry.insert(0, "20")  # Default value
infill_density_entry.grid(row=1, column=1, pady=5, padx=5)

print_speed_label = tk.Label(frame_params, text="Print Speed (mm/s):", bg='#f0f0f0')
print_speed_label.grid(row=2, column=0, pady=5, sticky='e')
print_speed_entry = tk.Entry(frame_params)
print_speed_entry.insert(0, "60")  # Default value
print_speed_entry.grid(row=2, column=1, pady=5, padx=5)

quality_mode_label = tk.Label(frame_params, text="Print Quality Mode:", bg='#f0f0f0')
quality_mode_label.grid(row=3, column=0, pady=5, sticky='e')
quality_mode_var = tk.StringVar(value="Custom")
quality_mode_var.trace("w", update_quality_mode)
quality_mode_menu = tk.OptionMenu(frame_params, quality_mode_var, "Custom", "Draft", "Normal", "High Quality")
quality_mode_menu.grid(row=3, column=1, pady=5, padx=5)

# Create a frame for model orientation controls
frame_orientation = tk.Frame(root, bg='#f0f0f0', pady=10, padx=10, bd=2, relief="groove")
frame_orientation.pack(fill='x', pady=10, padx=10)

rotate_label = tk.Label(frame_orientation, text="Rotate Model:", bg='#f0f0f0')
rotate_label.grid(row=0, column=0, columnspan=2, pady=5)

rotate_x_cw_button = tk.Button(frame_orientation, text="Rotate X CW", command=lambda: rotate_model('x', 1), bg='#4CAF50', fg='white', relief='flat')
rotate_x_ccw_button = tk.Button(frame_orientation, text="Rotate X CCW", command=lambda: rotate_model('x', -1), bg='#4CAF50', fg='white', relief='flat')
rotate_y_cw_button = tk.Button(frame_orientation, text="Rotate Y CW", command=lambda: rotate_model('y', 1), bg='#4CAF50', fg='white', relief='flat')
rotate_y_ccw_button = tk.Button(frame_orientation, text="Rotate Y CCW", command=lambda: rotate_model('y', -1), bg='#4CAF50', fg='white', relief='flat')
rotate_z_cw_button = tk.Button(frame_orientation, text="Rotate Z CW", command=lambda: rotate_model('z', 1), bg='#4CAF50', fg='white', relief='flat')
rotate_z_ccw_button = tk.Button(frame_orientation, text="Rotate Z CCW", command=lambda: rotate_model('z', -1), bg='#4CAF50', fg='white', relief='flat')
reset_button = tk.Button(frame_orientation, text="Reset Rotations", command=reset_rotation, bg='#f44336', fg='white', relief='flat')

rotate_x_cw_button.grid(row=1, column=0, padx=5, pady=5)
rotate_x_ccw_button.grid(row=1, column=1, padx=5, pady=5)
rotate_y_cw_button.grid(row=2, column=0, padx=5, pady=5)
rotate_y_ccw_button.grid(row=2, column=1, padx=5, pady=5)
rotate_z_cw_button.grid(row=3, column=0, padx=5, pady=5)
rotate_z_ccw_button.grid(row=3, column=1, padx=5, pady=5)
reset_button.grid(row=4, column=0, columnspan=2, pady=10)

# Create a frame for the slice button and success message
frame_actions = tk.Frame(root, bg='#f0f0f0', pady=10, padx=10, bd=2, relief="groove")
frame_actions.pack(fill='x', pady=10, padx=10)

slice_button = tk.Button(frame_actions, text="Slice Model", command=slice_model, bg='#28a745', fg='white', relief='flat')
slice_button.pack(pady=5)

success_label = tk.Label(frame_actions, text="", bg='#f0f0f0', fg='green')
success_label.pack()

root.mainloop()
