#!/usr/bin/env python3
"""
CSV Data Reader and Visualizer - Optimized version
Provides a modern GUI for reading, displaying, and analyzing CSV data.
"""

import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from typing import Optional, Dict, Any
import os
import json
from datetime import datetime


class CSVDataReader:
    """A modern CSV data reader with visualization capabilities."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CSV Data Reader & Analyzer")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.current_data: Optional[pd.DataFrame] = None
        self.file_path: Optional[str] = None
        
        # Configure style
        self.setup_styles()
        
        # Create UI
        self.create_widgets()
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def setup_styles(self):
        """Configure modern styling for the application."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Success.TLabel', foreground='#27ae60')
        style.configure('Error.TLabel', foreground='#e74c3c')
        
        # Configure buttons
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
        style.configure('Primary.TButton', background='#3498db', foreground='white')
    
    def create_widgets(self):
        """Create and arrange all UI widgets."""
        # Header frame
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        title_label = ttk.Label(header_frame, text="CSV Data Reader & Analyzer", style='Title.TLabel')
        title_label.pack()
        
        # Control frame
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # File selection
        file_frame = ttk.LabelFrame(control_frame, text="File Selection", padding="10")
        file_frame.pack(fill="x", pady=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        file_entry.pack(side="left", padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse CSV", command=self.choose_csv_file, style='Action.TButton')
        browse_btn.pack(side="left", padx=(0, 10))
        
        load_btn = ttk.Button(file_frame, text="Load Data", command=self.load_data, style='Primary.TButton')
        load_btn.pack(side="left")
        
        # Status frame
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(fill="x", pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready to load CSV file", style='Header.TLabel')
        self.status_label.pack(side="left")
        
        # Main content area with notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        # Data view tab
        self.create_data_view_tab()
        
        # Statistics tab
        self.create_stats_tab()
        
        # Visualization tab
        self.create_viz_tab()
        
        # Export tab
        self.create_export_tab()
    
    def create_data_view_tab(self):
        """Create the data viewing tab."""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Data View")
        
        # Data info
        info_frame = ttk.Frame(data_frame)
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.info_label = ttk.Label(info_frame, text="No data loaded", style='Header.TLabel')
        self.info_label.pack(side="left")
        
        # Data table
        table_frame = ttk.Frame(data_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create Treeview for data display
        self.tree = ttk.Treeview(table_frame)
        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def create_stats_tab(self):
        """Create the statistics tab."""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=20, width=80)
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_viz_tab(self):
        """Create the visualization tab."""
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Visualization")
        
        # Control buttons
        viz_controls = ttk.Frame(viz_frame)
        viz_controls.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(viz_controls, text="Bar Chart", command=lambda: self.create_chart('bar')).pack(side="left", padx=5)
        ttk.Button(viz_controls, text="Line Chart", command=lambda: self.create_chart('line')).pack(side="left", padx=5)
        ttk.Button(viz_controls, text="Scatter Plot", command=lambda: self.create_chart('scatter')).pack(side="left", padx=5)
        ttk.Button(viz_controls, text="Histogram", command=lambda: self.create_chart('hist')).pack(side="left", padx=5)
        ttk.Button(viz_controls, text="Correlation Heatmap", command=self.create_heatmap).pack(side="left", padx=5)
        
        # Chart area
        self.chart_frame = ttk.Frame(viz_frame)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    def create_export_tab(self):
        """Create the export tab."""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="Export")
        
        # Export options
        options_frame = ttk.LabelFrame(export_frame, text="Export Options", padding="10")
        options_frame.pack(fill="x", padx=10, pady=10)
        
        self.export_format = tk.StringVar(value="csv")
        ttk.Radiobutton(options_frame, text="CSV", variable=self.export_format, value="csv").pack(anchor="w")
        ttk.Radiobutton(options_frame, text="JSON", variable=self.export_format, value="json").pack(anchor="w")
        ttk.Radiobutton(options_frame, text="Excel", variable=self.export_format, value="excel").pack(anchor="w")
        
        # Export button
        export_btn = ttk.Button(export_frame, text="Export Data", command=self.export_data, style='Primary.TButton')
        export_btn.pack(pady=10)
        
        # Export status
        self.export_status = ttk.Label(export_frame, text="", style='Header.TLabel')
        self.export_status.pack()
    
    def choose_csv_file(self):
        """Open file dialog to select CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.file_path = file_path
            self.status_label.config(text=f"File selected: {os.path.basename(file_path)}")
    
    def load_data(self):
        """Load and display CSV data."""
        if not self.file_path or not os.path.exists(self.file_path):
            messagebox.showerror("Error", "Please select a valid CSV file.")
            return
        
        try:
            self.current_data = pd.read_csv(self.file_path)
            self.display_data()
            self.update_info()
            self.generate_statistics()
            self.status_label.config(text=f"✓ Data loaded successfully: {len(self.current_data)} rows, {len(self.current_data.columns)} columns")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file:\n{str(e)}")
            self.status_label.config(text="✗ Error loading data")
    
    def display_data(self):
        """Display data in the treeview."""
        if self.current_data is None:
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Configure columns
        columns = list(self.current_data.columns)
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)
        
        # Add data rows (limit to first 1000 rows for performance)
        for i, row in self.current_data.head(1000).iterrows():
            values = [str(val) if pd.notna(val) else "" for val in row]
            self.tree.insert("", "end", values=values)
    
    def update_info(self):
        """Update data information display."""
        if self.current_data is None:
            self.info_label.config(text="No data loaded")
            return
        
        info_text = f"Rows: {len(self.current_data):,} | Columns: {len(self.current_data.columns)} | Memory: {self.current_data.memory_usage(deep=True).sum() / 1024:.1f} KB"
        self.info_label.config(text=info_text)
    
    def generate_statistics(self):
        """Generate and display data statistics."""
        if self.current_data is None:
            return
        
        self.stats_text.delete(1.0, tk.END)
        
        stats = []
        stats.append("=== DATA STATISTICS ===\n")
        stats.append(f"Dataset Shape: {self.current_data.shape}")
        stats.append(f"Memory Usage: {self.current_data.memory_usage(deep=True).sum() / 1024:.2f} KB\n")
        
        # Data types
        stats.append("=== DATA TYPES ===")
        stats.append(str(self.current_data.dtypes))
        stats.append("\n")
        
        # Missing values
        stats.append("=== MISSING VALUES ===")
        missing_data = self.current_data.isnull().sum()
        if missing_data.sum() > 0:
            stats.append(str(missing_data[missing_data > 0]))
        else:
            stats.append("No missing values found")
        stats.append("\n")
        
        # Descriptive statistics
        stats.append("=== DESCRIPTIVE STATISTICS ===")
        numeric_cols = self.current_data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats.append(str(self.current_data[numeric_cols].describe()))
        else:
            stats.append("No numeric columns found")
        
        self.stats_text.insert(1.0, "\n".join(stats))
    
    def create_chart(self, chart_type: str):
        """Create various types of charts."""
        if self.current_data is None:
            messagebox.showwarning("Warning", "Please load data first.")
            return
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if chart_type == 'bar':
                # Show first numeric column as bar chart
                numeric_cols = self.current_data.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    col = numeric_cols[0]
                    self.current_data[col].value_counts().head(10).plot(kind='bar', ax=ax)
                    ax.set_title(f'Bar Chart - {col}')
                    ax.set_xlabel(col)
                    ax.set_ylabel('Count')
                else:
                    ax.text(0.5, 0.5, 'No numeric columns found', ha='center', va='center', transform=ax.transAxes)
            
            elif chart_type == 'line':
                numeric_cols = self.current_data.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    col = numeric_cols[0]
                    self.current_data[col].plot(kind='line', ax=ax)
                    ax.set_title(f'Line Chart - {col}')
                    ax.set_xlabel('Index')
                    ax.set_ylabel(col)
                else:
                    ax.text(0.5, 0.5, 'No numeric columns found', ha='center', va='center', transform=ax.transAxes)
            
            elif chart_type == 'scatter':
                numeric_cols = self.current_data.select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 2:
                    ax.scatter(self.current_data[numeric_cols[0]], self.current_data[numeric_cols[1]])
                    ax.set_xlabel(numeric_cols[0])
                    ax.set_ylabel(numeric_cols[1])
                    ax.set_title(f'Scatter Plot - {numeric_cols[0]} vs {numeric_cols[1]}')
                else:
                    ax.text(0.5, 0.5, 'Need at least 2 numeric columns', ha='center', va='center', transform=ax.transAxes)
            
            elif chart_type == 'hist':
                numeric_cols = self.current_data.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    col = numeric_cols[0]
                    self.current_data[col].hist(ax=ax, bins=30)
                    ax.set_title(f'Histogram - {col}')
                    ax.set_xlabel(col)
                    ax.set_ylabel('Frequency')
                else:
                    ax.text(0.5, 0.5, 'No numeric columns found', ha='center', va='center', transform=ax.transAxes)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create chart: {str(e)}")
    
    def create_heatmap(self):
        """Create correlation heatmap."""
        if self.current_data is None:
            messagebox.showwarning("Warning", "Please load data first.")
            return
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        try:
            numeric_data = self.current_data.select_dtypes(include=['number'])
            if len(numeric_data.columns) < 2:
                messagebox.showwarning("Warning", "Need at least 2 numeric columns for correlation heatmap.")
                return
            
            fig, ax = plt.subplots(figsize=(10, 8))
            correlation_matrix = numeric_data.corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
            ax.set_title('Correlation Heatmap')
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create heatmap: {str(e)}")
    
    def export_data(self):
        """Export data to selected format."""
        if self.current_data is None:
            messagebox.showwarning("Warning", "Please load data first.")
            return
        
        try:
            export_format = self.export_format.get()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if export_format == "csv":
                filename = f"exported_data_{timestamp}.csv"
                self.current_data.to_csv(filename, index=False)
            elif export_format == "json":
                filename = f"exported_data_{timestamp}.json"
                self.current_data.to_json(filename, orient='records', indent=2)
            elif export_format == "excel":
                filename = f"exported_data_{timestamp}.xlsx"
                self.current_data.to_excel(filename, index=False)
            
            self.export_status.config(text=f"✓ Data exported to: {filename}")
            messagebox.showinfo("Success", f"Data exported successfully to {filename}")
            
        except Exception as e:
            self.export_status.config(text="✗ Export failed")
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main function to run the CSV Data Reader."""
    try:
        app = CSVDataReader()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")


if __name__ == "__main__":
    main()
