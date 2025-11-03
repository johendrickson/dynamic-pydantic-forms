"""
A proof-of-concept GUI for the AIND Data Transfer Lite workflow. This script uses
MagicGUI and Qt to build an interactive form that lets users select metadata and
modality directories, set optional parameters, and validate configuration inputs
against a mock `JobSettings` model (from `fake_job_settings.py`) that emulates the
real implementation in the AIND Data Transfer Lite repository

Usage:
1. Install dependencies using `pip install -r magicgui/requirements.txt`
2. Run the script
3. The GUI window will appear:
   - Pick a metadata directory
   - Pick one or more modality directories (add more if needed)
   - Optionally adjust "Dry Run" and "S3 Bucket"
   - Click "Validate" to check the configuration
   - Click "Submit" to simulate job submission if validation passes
4. The output box will display validation success or errors, and copying to clipboard is available
"""

from fake_job_settings import JobSettings
from qtpy import QtCore, QtGui, QtWidgets

from magicgui import widgets

validation_passed = False
# -------------------------------
# Metadata directory (single picker)
# -------------------------------
metadata_picker = widgets.FileEdit(label="Metadata Directory", mode="d")

# -------------------------------
# Container for modality directories (dynamic)
# -------------------------------
modality_container = widgets.Container(widgets=[], layout="vertical")
first_modality_picker = widgets.FileEdit(label="Modality Directory", mode="d")
modality_container.append(first_modality_picker)


def add_modality_clicked():
    new_picker = widgets.FileEdit(label="Modality Directory")
    modality_container.append(new_picker)


add_modality_btn = widgets.PushButton(text="Add another modality directory")
add_modality_btn.changed.connect(add_modality_clicked)

# -------------------------------
# Optional fields
# -------------------------------
dry_run_widget = widgets.CheckBox(label="Dry Run (Optional)", value=True)
s3_bucket_widget = widgets.LineEdit(
    label="S3 Bucket (Optional)", value="aind-open-data"
)

# -------------------------------
# Output box (read-only + selectable)
# -------------------------------
output_box = widgets.TextEdit(label="Output")
output_box.native.setReadOnly(True)
output_box.native.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)


def get_form_values():
    """Return current values from the form."""
    metadata_path = metadata_picker.value
    modality_paths = [w.value for w in modality_container if w.value]
    dry_run_val = dry_run_widget.value
    s3_val = s3_bucket_widget.value
    return metadata_path, modality_paths, dry_run_val, s3_val


# Copy button
def copy_to_clipboard():
    QtGui.QGuiApplication.clipboard().setText(output_box.value)
    QtWidgets.QToolTip.showText(
        copy_btn.native.mapToGlobal(QtCore.QPoint(0, 0)), "Copied to clipboard"
    )


copy_btn = widgets.PushButton(text="Copy Output")
copy_btn.changed.connect(copy_to_clipboard)

# Group output box + copy button
output_section = widgets.Container(widgets=[output_box, copy_btn], layout="vertical")


def validate_clicked():
    global validation_passed
    metadata_path, modality_paths, dry_run_val, s3_val = get_form_values()

    errors = []
    if not metadata_path or str(metadata_path) == ".":
        errors.append("Metadata directory is required")
    if not modality_paths or all(str(p) == "." for p in modality_paths):
        errors.append("At least one modality directory is required")

    if errors:
        errors = [errors[0]] + [e[0].lower() + e[1:] for e in errors[1:]]
        output_box.value = "Error: " + " and ".join(errors) + "."
        validation_passed = False
        return

    try:
        modality_keys = JobSettings._modality_abbreviations[: len(modality_paths)]
        modality_dict = dict(zip(modality_keys, modality_paths))

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


def submit_clicked():
    if not validation_passed:
        output_box.value = "Cannot submit. Job type invalid. See validation details."
        return

    metadata_path, modality_paths, dry_run_val, s3_val = get_form_values()

    output_box.value = (
        f"Submitting Job with:\n"
        f"Metadata: {metadata_path}\n"
        f"Modalities: {modality_paths}\n"
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
