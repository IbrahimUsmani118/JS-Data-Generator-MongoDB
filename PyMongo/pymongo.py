import pymongo
from pymongo import MongoClient
import pandas as pd
import tkinter as tk
from tkinter import filedialog

class MongoDB(object):
    def __init__(self, host=None, port=None):
        self.host = host
        self.port = port

    def create_connection(self, dbName, collectionName):
        connection_string = f"mongodb://{self.host}:{self.port}/{dbName}"
        self.client = MongoClient(connection_string)
        self.DB = self.client[dbName]
        self.collection = self.DB[collectionName]

    def InsertData(self, path=None):
        try:
            df = pd.read_csv(path)
            data = df.to_dict('records')

            self.collection.insert_many(data, ordered=False)
            print("All the data has been exported to the MongoDB server... ")
        except Exception as e:
            print("An error occurred during data insertion:", e)

def select_csv_file():
    file_path = filedialog.askopenfilename(title="Select a CSV file")
    if file_path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, file_path)

def import_to_mongodb():
    host = host_entry.get()
    port = int(port_entry.get())
    dbName = db_entry.get()
    collectionName = collection_entry.get()
    csv_file_path = csv_entry.get()
    
    if host and port and dbName and collectionName and csv_file_path:
        mongodb = MongoDB(host=host, port=port)
        mongodb.create_connection(dbName, collectionName)
        mongodb.InsertData(path=csv_file_path)
    else:
        print("Please fill in all the required fields.")

# Create the GUI window
window = tk.Tk()
window.title("CSV to MongoDB Import")

# Host and Port Input
host_label = tk.Label(window, text="MongoDB Host:")
host_label.pack()
host_entry = tk.Entry(window)
host_entry.pack()

port_label = tk.Label(window, text="MongoDB Port:")
port_label.pack()
port_entry = tk.Entry(window)
port_entry.pack()

# Database and Collection Input
db_label = tk.Label(window, text="Database Name:")
db_label.pack()
db_entry = tk.Entry(window)
db_entry.pack()

collection_label = tk.Label(window, text="Collection Name:")
collection_label.pack()
collection_entry = tk.Entry(window)
collection_entry.pack()

# CSV File Selection
csv_label = tk.Label(window, text="Select CSV File:")
csv_label.pack()
csv_entry = tk.Entry(window)
csv_entry.pack()
csv_button = tk.Button(window, text="Browse", command=select_csv_file)
csv_button.pack()

# Import Button
import_button = tk.Button(window, text="Import to MongoDB", command=import_to_mongodb)
import_button.pack()

window.mainloop()
