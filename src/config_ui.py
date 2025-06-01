import os
from tkinter import Tk, Label, Entry, Button, messagebox
from dotenv import dotenv_values, set_key
import pyodbc

env_path = os.path.join("..", ".env")

def load_env():
    return dotenv_values(env_path)

def save_env(values):
    for key, val in values.items():
        set_key(env_path, key, val)

def test_connection(values):
    try:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={values['SQL_SERVER']};"
            f"DATABASE={values['SQL_DATABASE']};"
            f"UID={values['SQL_USER']};"
            f"PWD={values['SQL_PASSWORD']}"
        )
        conn = pyodbc.connect(conn_str, timeout=5)
        conn.close()
        messagebox.showinfo("Success", "Connected to SQL Server successfully.")
    except Exception as e:
        messagebox.showerror("Connection Failed", str(e))

def run_ui():
    env = load_env()

    root = Tk()
    root.title("Holiday Sync Config")

    labels = ["SQL_SERVER", "SQL_DATABASE", "SQL_USER", "SQL_PASSWORD"]
    entries = {}

    for i, key in enumerate(labels):
        Label(root, text=key).grid(row=i, column=0, padx=10, pady=5, sticky="w")
        ent = Entry(root, width=40)
        ent.insert(0, env.get(key, ""))
        ent.grid(row=i, column=1, padx=10, pady=5)
        entries[key] = ent

    def save():
        updated = {k: entries[k].get().strip() for k in entries}
        save_env(updated)
        messagebox.showinfo("Saved", ".env file updated successfully.")

    Button(root, text="Save", command=save).grid(row=len(labels), column=0, padx=10, pady=10)
    Button(root, text="Test Connection", command=lambda: test_connection({k: entries[k].get().strip() for k in entries})).grid(row=len(labels), column=1, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_ui()
