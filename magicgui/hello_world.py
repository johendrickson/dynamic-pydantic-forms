"""
MagicGUI Hello World Example

This script shows a very basic use of MagicGUI with Qt.
It creates a single widget displaying "Hello World" and starts
the Qt event loop to show it on screen

Purpose: Demonstrate the minimal setup for MagicGUI + Qt

Usage:
1. Install dependencies using `pip install -r magicgui/requirements.txt
2. Run the script
3. A small window will appear showing "Hello World". Close the window to exit
"""

import sys

from qtpy.QtWidgets import QApplication

from magicgui.widgets import create_widget

app = QApplication(sys.argv)  # create the Qt application
widget = create_widget(value="Hello World")
widget.show()
app.exec()  # start the event loop
