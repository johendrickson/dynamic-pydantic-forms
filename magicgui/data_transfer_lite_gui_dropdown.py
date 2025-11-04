"""
A proof-of-concept GUI for the AIND Data Transfer Lite workflow. This script uses
MagicGUI and Qt to build an interactive form that lets users select metadata and
modality directories, set optional parameters, and validate configuration inputs
against a mock `JobSettings` model (from `fake_job_settings.py`) that emulates the
real implementation in the AIND Data Transfer Lite repository

Adds:
- Dropdown for selecting modality type (e.g., behavior, ecephys, brightfield)
- Delete buttons for removing modality rows (keeps at least one)
"""

from fake_job_settings import JobSettings
from qtpy import QtCore, QtGui, QtWidgets
from magicgui import widgets

validation_passed = False

# -------------------------------
# Metadata directory picker
# -------------------------------
metadata_picker = widgets.FileEdit(label="Metadata Directory", mode="d")

# -------------------------------
# Modality container + logic
# -------------------------------
modality_container = widgets.Container(widgets=[], layout="vertical")


def make_modality_row():
    """Create a row containing a dropdown, a directory picker, and a delete button."""
    modality_select = widgets.ComboBox(
        label="Modality Type",
        choices=JobSettings._modality_abbreviations,
        value=JobSettings._modality_abbreviations[0],
    )
    modality_picker = widgets.FileEdit(label="Directory", mode="d")
    delete_btn = widgets.PushButton(text="Delete")

    row = widgets.Container(
        widgets=[modality_select, modality_picker, delete_btn],
        layout="horizontal",
    )

    def delete_clicked():
        if len(modality_container) > 1:
            modality_container.remove(row)
        else:
            QtWidgets.QToolTip.showText(
                delete_btn.native.mapToGlobal(QtCore.QPoint(0, 0)),
                "At least one modality is required",
            )

    delete_btn.changed.connect(delete_clicked)
    return row


# Add first modality by default
modality_container.append(make_modality_row())


def add_modality_clicked():
    modality_container.append(make_modality_row())


add_modality_btn = widgets.PushButton(text="Add another modality directory")
add_modality_btn.changed.connect(add_modality_clicked)

# -------------------------------
# Optional fields
# -------------------------------
dry_run_widget = widgets.CheckBox(label="Dry Run (Optional)", value=True)
s3_bucket_widget = widgets.LineEdit(label="S3 Bucket (Optional)", value="aind-open-data")

# -------------------------------
# Output box + copy button
# -------------------------------
output_box = widgets.TextEdit(label="Output")
output_box.native.setReadOnly(True)
output_box.native.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)


def copy_to_clipboard():
    QtGui.QGuiApplication.clipboard().setText(output_box.value)
    QtWidgets.QToolTip.showText(
        copy_btn.native.mapToGlobal(QtCore.QPoint(0, 0)), "Copied to clipboard"
    )


copy_btn = widgets.PushButton(text="Copy Output")
copy_btn.changed.connect(copy_to_clipboard)

output_section = widgets.Container(widgets=[output_box, copy_btn], layout="vertical")

# -------------------------------
# Validate button
# -------------------------------
def validate_clicked():
    global validation_passed
    metadata_path = metadata_picker.value
    modality_rows = [
        w for w in modality_container if isinstance(w, widgets.Container)
    ]

    modality_dict = {}
    for row in modality_rows:
        modality_type = row[0].value
        modality_dir = row[1].value
        if modality_dir and str(modality_dir) != ".":
            modality_dict[modality_type] = modality_dir

    dry_run_val = dry_run_widget.value
    s3_val = s3_bucket_widget.value

    errors = []

    if not metadata_path or str(metadata_path) == ".":
        errors.append("Metadata directory is required")
    if not modality_dict:
        errors.append("At least one modality directory is required")

    if errors:
        errors = [errors[0]] + [e[0].lower() + e[1:] for e in errors[1:]]
        output_box.value = "Error: " + " and ".join(errors) + "."
        validation_passed = False
        return

    try:
        job_settings = JobSettings(
            metadata_directory=metadata_path,
            modality_directories=modality_dict,
            dry_run=dry_run_val,
            s3_bucket=s3_val,
        )
        output_box.value = "Validation successful!\n" + job_settings.model_dump_json(
            indent=2
        )
        validation_passed = True
    except Exception as e:
        output_box.value = f"Error. Validation failed:\n{e}"
        validation_passed = False


validate_btn = widgets.PushButton(text="Validate")
validate_btn.changed.connect(validate_clicked)

# -------------------------------
# Submit button
# -------------------------------
def submit_clicked():
    if not validation_passed:
        output_box.value = "Cannot submit. Job type invalid. See validation details."
        return

    metadata_path = metadata_picker.value
    modality_rows = [w for w in modality_container if isinstance(w, widgets.Container)]
    modality_dict = {
        row[0].value: row[1].value
        for row in modality_rows
        if row[1].value and str(row[1].value) != "."
    }

    dry_run_val = dry_run_widget.value
    s3_val = s3_bucket_widget.value

    output_box.value = (
        f"Submitting Job with:\n"
        f"Metadata: {metadata_path}\n"
        f"Modalities: {modality_dict}\n"
        f"Dry Run: {dry_run_val}\n"
        f"S3 Bucket: {s3_val}"
    )


submit_btn = widgets.PushButton(text="Submit")
submit_btn.changed.connect(submit_clicked)

# -------------------------------
# Main container
# -------------------------------
main_container = widgets.Container(
    widgets=[
        metadata_picker,
        modality_container,
        add_modality_btn,
        dry_run_widget,
        s3_bucket_widget,
        validate_btn,
        submit_btn,
        output_section,
    ],
    layout="vertical",
)

main_container.native.setWindowTitle("AIND Data Transfer Lite PoC")

main_container.show(run=True)
