import pandas as pd
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt

def read_csv_file(filename):
    try:
        data = pd.read_csv(filename)
        return data
    except FileNotFoundError as exception:
        print(f"Error: {exception}")
        return None

def display_data(data):
    if data is not None:
        print(data)
        # Use matplotlib to display data in a text-based format
        plt.table(cellText=data.values, colLabels=data.columns, cellLoc='center', loc='center')
        plt.axis('off')
        plt.show()
    else:
        print("No data to display.")

def on_drop(event):
    filename = event.data
    data = read_csv_file(filename)
    display_data(data)

def choose_csv_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        data = read_csv_file(file_path)
        display_data(data)

def main():
    """
    This is the main function to create the Tkinter application.
    """
    try:
        root = tk.Tk()
        root.title("CSV File Reader")

        label = tk.Label(root, text="Select a CSV file:")
        label.pack(pady=10)

        choose_button = tk.Button(root, text="Choose CSV File", command=choose_csv_file)
        choose_button.pack(pady=5)

        root.drop_target_register('<<Drop>>')
        root.dnd_bind('<<Drop>>', on_drop)

        root.mainloop()
    except tk.TclError:
        print("Error: Tkinter cannot find a display.")
        print("If you are running this in a headless environment, consider using a display server like X11.")

if __name__ == "__main__":
    main()
