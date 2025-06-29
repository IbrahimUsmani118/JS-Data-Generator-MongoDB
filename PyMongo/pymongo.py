#!/usr/bin/env python3
"""
MongoDB Data Import Tool - Optimized Version
A modern GUI application for importing CSV data into MongoDB with validation and error handling.
"""

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, BulkWriteError
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging


class MongoDBManager:
    """Manages MongoDB connections and operations with improved error handling."""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None
        self.connection_status = False
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('mongodb_import.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def test_connection(self, host: str, port: int, timeout: int = 5000) -> bool:
        """Test MongoDB connection with timeout."""
        try:
            connection_string = f"mongodb://{host}:{port}"
            test_client = MongoClient(connection_string, serverSelectionTimeoutMS=timeout)
            
            # Test the connection
            test_client.admin.command('ping')
            test_client.close()
            
            self.logger.info(f"Connection test successful: {host}:{port}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during connection test: {e}")
            return False
    
    def create_connection(self, host: str, port: int, db_name: str, collection_name: str) -> bool:
        """Create MongoDB connection with validation."""
        try:
            if not self.test_connection(host, port):
                return False
            
            connection_string = f"mongodb://{host}:{port}"
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            
            # Test database access
            self.db.list_collection_names()
            
            self.connection_status = True
            self.logger.info(f"Connected to MongoDB: {host}:{port}/{db_name}/{collection_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create connection: {e}")
            self.connection_status = False
            return False
    
    def validate_csv_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate CSV data before import."""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': df.isnull().sum().sum(),
                'duplicate_rows': df.duplicated().sum()
            }
        }
        
        # Check for empty dataframe
        if df.empty:
            validation_result['valid'] = False
            validation_result['errors'].append("CSV file is empty")
            return validation_result
        
        # Check for too many columns (MongoDB document size limit)
        if len(df.columns) > 100:
            validation_result['warnings'].append("Large number of columns detected (>100)")
        
        # Check for very large data
        if len(df) > 100000:
            validation_result['warnings'].append("Large dataset detected (>100k rows)")
        
        # Check column names for MongoDB compatibility
        invalid_columns = []
        for col in df.columns:
            if col.startswith('$') or '.' in col:
                invalid_columns.append(col)
        
        if invalid_columns:
            validation_result['warnings'].append(f"Columns with MongoDB-incompatible names: {invalid_columns}")
        
        return validation_result
    
    def insert_data(self, df: pd.DataFrame, batch_size: int = 1000) -> Dict[str, Any]:
        """Insert data into MongoDB with batch processing and error handling."""
        if not self.connection_status:
            return {'success': False, 'error': 'Not connected to MongoDB'}
        
        try:
            # Convert DataFrame to list of dictionaries
            data = df.to_dict('records')
            total_records = len(data)
            inserted_count = 0
            error_count = 0
            errors = []
            
            self.logger.info(f"Starting import of {total_records} records")
            
            # Process in batches
            for i in range(0, total_records, batch_size):
                batch = data[i:i + batch_size]
                
                try:
                    result = self.collection.insert_many(batch, ordered=False)
                    inserted_count += len(result.inserted_ids)
                    self.logger.info(f"Inserted batch {i//batch_size + 1}: {len(result.inserted_ids)} records")
                    
                except BulkWriteError as e:
                    # Handle partial batch failures
                    inserted_count += len(e.details['insertedIds'])
                    error_count += len(e.details['writeErrors'])
                    
                    for error in e.details['writeErrors']:
                        errors.append(f"Row {error['index']}: {error['errmsg']}")
                    
                    self.logger.warning(f"Batch {i//batch_size + 1} had {len(e.details['writeErrors'])} errors")
                
                except Exception as e:
                    error_count += len(batch)
                    errors.append(f"Batch {i//batch_size + 1}: {str(e)}")
                    self.logger.error(f"Batch {i//batch_size + 1} failed: {e}")
            
            result = {
                'success': True,
                'total_records': total_records,
                'inserted_count': inserted_count,
                'error_count': error_count,
                'errors': errors
            }
            
            self.logger.info(f"Import completed: {inserted_count}/{total_records} records inserted")
            return result
            
        except Exception as e:
            self.logger.error(f"Import failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        if not self.connection_status:
            return {}
        
        try:
            stats = self.db.command('collStats', self.collection.name)
            return {
                'count': stats.get('count', 0),
                'size': stats.get('size', 0),
                'avgObjSize': stats.get('avgObjSize', 0),
                'storageSize': stats.get('storageSize', 0),
                'indexes': stats.get('nindexes', 0)
            }
        except Exception as e:
            self.logger.error(f"Failed to get collection stats: {e}")
            return {}
    
    def close_connection(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.connection_status = False
            self.logger.info("MongoDB connection closed")


class ModernGUI:
    """Modern GUI application with improved user experience."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MongoDB CSV Import Tool")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f8fafc')
        
        # Initialize MongoDB manager
        self.mongodb_manager = MongoDBManager()
        
        # Data storage
        self.csv_data: Optional[pd.DataFrame] = None
        self.csv_file_path: Optional[str] = None
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def setup_styles(self):
        """Configure modern styling."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors and fonts
        style.configure('Title.TLabel', font=('Inter', 16, 'bold'), foreground='#1e293b')
        style.configure('Header.TLabel', font=('Inter', 12, 'bold'), foreground='#334155')
        style.configure('Success.TLabel', foreground='#10b981')
        style.configure('Error.TLabel', foreground='#ef4444')
        style.configure('Warning.TLabel', foreground='#f59e0b')
        
        # Configure buttons
        style.configure('Primary.TButton', font=('Inter', 10, 'bold'))
        style.configure('Success.TButton', font=('Inter', 10, 'bold'))
        style.configure('Warning.TButton', font=('Inter', 10, 'bold'))
    
    def create_widgets(self):
        """Create all UI widgets."""
        # Header
        self.create_header()
        
        # Main content area
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create application header."""
        header_frame = ttk.Frame(self.root, padding="20")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        
        title_label = ttk.Label(header_frame, text="MongoDB CSV Import Tool", style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Import CSV data into MongoDB with validation and monitoring", 
                                  style='Header.TLabel')
        subtitle_label.pack()
    
    def create_main_content(self):
        """Create main content area with notebook."""
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self.create_connection_tab()
        self.create_import_tab()
        self.create_monitoring_tab()
    
    def create_connection_tab(self):
        """Create connection configuration tab."""
        connection_frame = ttk.Frame(self.notebook)
        self.notebook.add(connection_frame, text="Connection")
        
        # Connection form
        form_frame = ttk.LabelFrame(connection_frame, text="MongoDB Connection", padding="20")
        form_frame.pack(fill="x", padx=20, pady=20)
        
        # Host and Port
        host_frame = ttk.Frame(form_frame)
        host_frame.pack(fill="x", pady=10)
        
        ttk.Label(host_frame, text="Host:").pack(side="left")
        self.host_entry = ttk.Entry(host_frame, width=30)
        self.host_entry.pack(side="left", padx=(10, 0))
        self.host_entry.insert(0, "localhost")
        
        ttk.Label(host_frame, text="Port:").pack(side="left", padx=(20, 0))
        self.port_entry = ttk.Entry(host_frame, width=10)
        self.port_entry.pack(side="left", padx=(10, 0))
        self.port_entry.insert(0, "27017")
        
        # Database and Collection
        db_frame = ttk.Frame(form_frame)
        db_frame.pack(fill="x", pady=10)
        
        ttk.Label(db_frame, text="Database:").pack(side="left")
        self.db_entry = ttk.Entry(db_frame, width=30)
        self.db_entry.pack(side="left", padx=(10, 0))
        
        ttk.Label(db_frame, text="Collection:").pack(side="left", padx=(20, 0))
        self.collection_entry = ttk.Entry(db_frame, width=30)
        self.collection_entry.pack(side="left", padx=(10, 0))
        
        # Connection buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=20)
        
        self.test_btn = ttk.Button(button_frame, text="Test Connection", 
                                  command=self.test_connection, style='Primary.TButton')
        self.test_btn.pack(side="left", padx=(0, 10))
        
        self.connect_btn = ttk.Button(button_frame, text="Connect", 
                                     command=self.connect_to_mongodb, style='Success.TButton')
        self.connect_btn.pack(side="left")
        
        # Connection status
        self.connection_status_label = ttk.Label(form_frame, text="Not connected", style='Error.TLabel')
        self.connection_status_label.pack(pady=10)
    
    def create_import_tab(self):
        """Create data import tab."""
        import_frame = ttk.Frame(self.notebook)
        self.notebook.add(import_frame, text="Import")
        
        # File selection
        file_frame = ttk.LabelFrame(import_frame, text="CSV File Selection", padding="20")
        file_frame.pack(fill="x", padx=20, pady=20)
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill="x", pady=10)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, width=60)
        file_entry.pack(side="left", padx=(0, 10))
        
        browse_btn = ttk.Button(file_select_frame, text="Browse CSV", 
                               command=self.browse_csv_file, style='Primary.TButton')
        browse_btn.pack(side="left", padx=(0, 10))
        
        load_btn = ttk.Button(file_select_frame, text="Load & Validate", 
                             command=self.load_and_validate_csv, style='Success.TButton')
        load_btn.pack(side="left")
        
        # Data preview
        preview_frame = ttk.LabelFrame(import_frame, text="Data Preview", padding="20")
        preview_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create Treeview for data preview
        self.tree = ttk.Treeview(preview_frame, height=10)
        tree_scroll_y = ttk.Scrollbar(preview_frame, orient="vertical", command=self.tree.yview)
        tree_scroll_x = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")
        
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Import controls
        import_controls_frame = ttk.Frame(import_frame)
        import_controls_frame.pack(fill="x", padx=20, pady=20)
        
        self.import_btn = ttk.Button(import_controls_frame, text="Import to MongoDB", 
                                    command=self.import_to_mongodb, style='Success.TButton')
        self.import_btn.pack(side="left")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(import_controls_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.pack(side="left", padx=(20, 0))
    
    def create_monitoring_tab(self):
        """Create monitoring and logs tab."""
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="Monitoring")
        
        # Logs area
        logs_frame = ttk.LabelFrame(monitoring_frame, text="Application Logs", padding="20")
        logs_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=20, width=80)
        self.logs_text.pack(fill="both", expand=True)
        
        # Collection stats
        stats_frame = ttk.LabelFrame(monitoring_frame, text="Collection Statistics", padding="20")
        stats_frame.pack(fill="x", padx=20, pady=20)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=8, width=80)
        self.stats_text.pack(fill="both", expand=True)
        
        # Refresh button
        refresh_btn = ttk.Button(stats_frame, text="Refresh Stats", 
                                command=self.refresh_stats, style='Primary.TButton')
        refresh_btn.pack(pady=10)
    
    def create_status_bar(self):
        """Create status bar."""
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", style='Header.TLabel')
        self.status_label.pack(side="left")
    
    def setup_layout(self):
        """Setup the layout grid."""
        pass  # Already configured in create_widgets
    
    def browse_csv_file(self):
        """Open file dialog to select CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.csv_file_path = file_path
            self.update_status(f"CSV file selected: {os.path.basename(file_path)}")
    
    def load_and_validate_csv(self):
        """Load and validate CSV data."""
        if not self.csv_file_path or not os.path.exists(self.csv_file_path):
            messagebox.showerror("Error", "Please select a valid CSV file.")
            return
        
        try:
            self.csv_data = pd.read_csv(self.csv_file_path)
            self.display_data_preview()
            
            # Validate data
            validation = self.mongodb_manager.validate_csv_data(self.csv_data)
            self.show_validation_results(validation)
            
            self.update_status(f"CSV loaded: {len(self.csv_data)} rows, {len(self.csv_data.columns)} columns")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file:\n{str(e)}")
            self.update_status("Error loading CSV file")
    
    def display_data_preview(self):
        """Display data preview in treeview."""
        if self.csv_data is None:
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Configure columns
        columns = list(self.csv_data.columns)
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'
        
        # Set column headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, minwidth=50)
        
        # Add data rows (limit to first 100 rows for performance)
        for i, row in self.csv_data.head(100).iterrows():
            values = [str(val) if pd.notna(val) else "" for val in row]
            self.tree.insert("", "end", values=values)
    
    def show_validation_results(self, validation: Dict[str, Any]):
        """Show validation results to user."""
        message = f"Validation Results:\n"
        message += f"✓ Total rows: {validation['stats']['total_rows']}\n"
        message += f"✓ Total columns: {validation['stats']['total_columns']}\n"
        message += f"⚠ Missing values: {validation['stats']['missing_values']}\n"
        message += f"⚠ Duplicate rows: {validation['stats']['duplicate_rows']}\n"
        
        if validation['warnings']:
            message += f"\nWarnings:\n"
            for warning in validation['warnings']:
                message += f"⚠ {warning}\n"
        
        if validation['errors']:
            message += f"\nErrors:\n"
            for error in validation['errors']:
                message += f"✗ {error}\n"
        
        messagebox.showinfo("Data Validation", message)
    
    def test_connection(self):
        """Test MongoDB connection."""
        host = self.host_entry.get().strip()
        port_str = self.port_entry.get().strip()
        
        if not host or not port_str:
            messagebox.showerror("Error", "Please enter host and port.")
            return
        
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number.")
            return
        
        self.update_status("Testing connection...")
        
        # Run in thread to avoid blocking UI
        def test_connection_thread():
            success = self.mongodb_manager.test_connection(host, port)
            
            def update_ui():
                if success:
                    messagebox.showinfo("Success", "Connection test successful!")
                    self.update_status("Connection test successful")
                else:
                    messagebox.showerror("Error", "Connection test failed. Please check your settings.")
                    self.update_status("Connection test failed")
            
            self.root.after(0, update_ui)
        
        threading.Thread(target=test_connection_thread, daemon=True).start()
    
    def connect_to_mongodb(self):
        """Connect to MongoDB."""
        host = self.host_entry.get().strip()
        port_str = self.port_entry.get().strip()
        db_name = self.db_entry.get().strip()
        collection_name = self.collection_entry.get().strip()
        
        if not all([host, port_str, db_name, collection_name]):
            messagebox.showerror("Error", "Please fill in all connection fields.")
            return
        
        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number.")
            return
        
        self.update_status("Connecting to MongoDB...")
        
        # Run in thread to avoid blocking UI
        def connect_thread():
            success = self.mongodb_manager.create_connection(host, port, db_name, collection_name)
            
            def update_ui():
                if success:
                    self.connection_status_label.config(text="Connected", style='Success.TLabel')
                    self.update_status("Connected to MongoDB")
                    self.refresh_stats()
                else:
                    self.connection_status_label.config(text="Connection failed", style='Error.TLabel')
                    self.update_status("Connection failed")
            
            self.root.after(0, update_ui)
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def import_to_mongodb(self):
        """Import CSV data to MongoDB."""
        if not self.mongodb_manager.connection_status:
            messagebox.showerror("Error", "Please connect to MongoDB first.")
            return
        
        if self.csv_data is None:
            messagebox.showerror("Error", "Please load CSV data first.")
            return
        
        # Confirm import
        response = messagebox.askyesno("Confirm Import", 
                                     f"Import {len(self.csv_data)} records to MongoDB?\n"
                                     f"Database: {self.db_entry.get()}\n"
                                     f"Collection: {self.collection_entry.get()}")
        if not response:
            return
        
        self.update_status("Importing data...")
        self.progress_var.set(0)
        
        # Run import in thread
        def import_thread():
            result = self.mongodb_manager.insert_data(self.csv_data)
            
            def update_ui():
                if result['success']:
                    message = f"Import completed!\n"
                    message += f"Total records: {result['total_records']}\n"
                    message += f"Inserted: {result['inserted_count']}\n"
                    message += f"Errors: {result['error_count']}"
                    
                    if result['errors']:
                        message += f"\n\nFirst few errors:\n"
                        for error in result['errors'][:5]:
                            message += f"• {error}\n"
                    
                    messagebox.showinfo("Import Complete", message)
                    self.progress_var.set(100)
                    self.update_status(f"Import completed: {result['inserted_count']} records")
                    self.refresh_stats()
                else:
                    messagebox.showerror("Import Failed", f"Import failed: {result['error']}")
                    self.update_status("Import failed")
            
            self.root.after(0, update_ui)
        
        threading.Thread(target=import_thread, daemon=True).start()
    
    def refresh_stats(self):
        """Refresh collection statistics."""
        if not self.mongodb_manager.connection_status:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, "Not connected to MongoDB")
            return
        
        stats = self.mongodb_manager.get_collection_stats()
        
        if stats:
            stats_text = "Collection Statistics:\n\n"
            stats_text += f"Document Count: {stats.get('count', 0):,}\n"
            stats_text += f"Collection Size: {stats.get('size', 0):,} bytes\n"
            stats_text += f"Average Document Size: {stats.get('avgObjSize', 0):.2f} bytes\n"
            stats_text += f"Storage Size: {stats.get('storageSize', 0):,} bytes\n"
            stats_text += f"Indexes: {stats.get('indexes', 0)}\n"
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
        else:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, "Failed to retrieve statistics")
    
    def update_status(self, message: str):
        """Update status bar message."""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Start the application."""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            self.mongodb_manager.close_connection()


def main():
    """Main function to run the MongoDB Import Tool."""
    try:
        app = ModernGUI()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")


if __name__ == "__main__":
    main()
