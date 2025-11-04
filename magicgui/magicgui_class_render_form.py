"""
Example: MagicGUI class-based form for a simplified AIND Data Transfer workflow.
Demonstrates how to define a GUI as a class using @magicclass.

Features:
- Metadata directory picker
- One or more modality rows (dropdown + FileEdit)
- Add/Delete modality functionality (must keep at least one)
- Simple validation feedback box

Usage:
1. Install dependencies using `pip install -r magicgui/requirements.txt`
2. Run the script
"""

from magicclass import magicclass
from magicgui import widgets
from qtpy import QtCore, QtWidgets


@magicclass(layout="vertical", labels=False)
class DataTransferForm:
    def __init__(self):
        # Create metadata directory picker
        self.metadata = widgets.FileEdit(label="Metadata Directory", mode="d")

        # Container for modality rows
        self.modality_container = widgets.Container(layout="vertical")
        self.modality_container.append(self._make_modality_row())

        # Add button
        self.add_btn = widgets.PushButton(text="Add Modality")
        self.add_btn.changed.connect(self._add_modality)

        # Validate button + output area
        self.validate_btn = widgets.PushButton(text="Validate")
        self.validate_btn.changed.connect(self._validate_form)

        self.output_box = widgets.TextEdit(label="Output", value="")
        self.output_box.native.setReadOnly(True)
        self.output_box.native.setMinimumHeight(80)

        # Add widgets to layout
        self.append(self.metadata)
        self.append(self.modality_container)
        self.append(self.add_btn)
        self.append(self.validate_btn)
        self.append(self.output_box)

    # -------------------------------
    # Helper: Create one modality row
    # -------------------------------
    def _make_modality_row(self):
        dropdown = widgets.ComboBox(
            label="Type",
            choices=["behavior", "ecephys", "brightfield"],
            value="behavior",
        )
        picker = widgets.FileEdit(label="Directory", mode="d")
        delete_btn = widgets.PushButton(text="Delete")

        row = widgets.Container(widgets=[dropdown, picker, delete_btn], layout="horizontal")

        def delete_clicked():
            if len(self.modality_container) > 1:
                self.modality_container.remove(row)
            else:
                QtWidgets.QToolTip.showText(
                    delete_btn.native.mapToGlobal(QtCore.QPoint(0, 0)),
                    "At least one modality is required",
                )

        delete_btn.changed.connect(delete_clicked)
        return row

    # -------------------------------
    # Button handlers
    # -------------------------------
    def _add_modality(self):
        self.modality_container.append(self._make_modality_row())

    def _validate_form(self):
        metadata_path = self.metadata.value
        modalities = []
        for row in self.modality_container:
            mod_type = row[0].value
            mod_path = row[1].value
            if mod_path and str(mod_path) != ".":
                modalities.append((mod_type, mod_path))

        # Simple validation
        if not metadata_path or str(metadata_path) == ".":
            self.output_box.value = "Error: Metadata directory is required."
            return
        if not modalities:
            self.output_box.value = "Error: At least one modality directory is required."
            return

        # Success
        self.output_box.value = (
            "Validation successful!\n"
            f"Metadata: {metadata_path}\n"
            + "\n".join([f"{t}: {p}" for t, p in modalities])
        )


if __name__ == "__main__":
    gui = DataTransferForm()
    gui.show(run=True)
