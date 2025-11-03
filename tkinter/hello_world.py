"""
A minimal Tkinter example that creates a window with a "Hello World!" label
and a "Quit" button to close the application

Usage:
1. Run the script
2. A window will appear with the label and button
3. Click "Quit" to close the window
"""

import tkinter as tk
from tkinter import ttk

"""Runs a simple 'Hello, world!' program"""
root = tk.Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
root.mainloop()
