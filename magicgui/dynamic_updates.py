"""
Dynamic Form Builder using Pydantic and MagicGUI:

This script is a proof-of-concept demonstrates how to dynamically generate a graphical form interface
from a Pydantic model using the MagicGUI library. It serves as an interactive tool
for collecting and validating structured metadata — for example, information related
to experimental uploads

Usage:
1. Install dependencies using `pip install -r magicgui/requirements.txt`
2. Run the script
3. Interact with the GUI:
   - Fill in all required fields
   - Click "Submit" to validate the input
   - Click "Simulate Model Update" to dynamically add a new field and rebuild the form
   - View results and validation messages in the output box

"""

from typing import Optional

from pydantic import BaseModel, Field, ValidationError
from pydantic.fields import PydanticUndefined

from magicgui import widgets


# -------------------------------
# Step 1: Define Pydantic model
# -------------------------------
class UploadMetadata(BaseModel):
    experiment_name: str = Field(..., title="Experiment Name")
    principal_investigator: str = Field(..., title="Principal Investigator")
    data_type: str = Field(..., title="Data Type (e.g., behavior, ecephys)")
    date_collected: str = Field(..., title="Date Collected (YYYY-MM-DD)")
    s3_bucket_target: Optional[str] = Field("aind-open-data", title="S3 Bucket Target")


CURRENT_MODEL = UploadMetadata


# -------------------------------
# Step 2: Build the form dynamically
# -------------------------------
def build_form(model_cls, parent_container=None):
    """Create a MagicGUI form dynamically from a Pydantic model."""

    fields = {}

    # Create widgets for each model field
    for name, field in model_cls.model_fields.items():
        title = field.title or name.replace("_", " ").title()
        if field.default is PydanticUndefined or field.default is None:
            default = ""
        else:
            default = str(field.default)
        fields[name] = widgets.LineEdit(value=default, label=title)

    # Buttons + output
    submit_btn = widgets.PushButton(label="Submit")
    update_btn = widgets.PushButton(label="Simulate Model Update")
    output_box = widgets.TextEdit(value="", enabled=False, label="Output")

    @submit_btn.changed.connect
    def on_submit(_):
        data = {name: w.value for name, w in fields.items()}
        try:
            validated = model_cls(**data)
            output_box.value = f"✅ Success!\n\n{validated.model_dump_json(indent=2)}"
        except ValidationError as e:
            output_box.value = f"❌ Validation error:\n{e.json(indent=2)}"

    @update_btn.changed.connect
    def on_update(_):
        global CURRENT_MODEL

        # Define a new model subclass
        class UpdatedModel(CURRENT_MODEL):
            new_dynamic_field: Optional[str] = Field(
                "huzzah!", title="✨ Our New Field!"
            )

        CURRENT_MODEL = UpdatedModel
        output_box.value = "🔄 Rebuilding form with new field..."

        # 🔁 Rebuild form in place
        if parent_container:
            new_form = build_form(CURRENT_MODEL, parent_container)
            parent_container.clear()
            parent_container.extend(new_form)

    # Put widgets together
    form = [
        *fields.values(),
        submit_btn,
        update_btn,
        output_box,
    ]

    return form


# -------------------------------
# Step 3: Launch GUI
# -------------------------------
def main():
    container = widgets.Container(layout="vertical")
    container.extend(build_form(CURRENT_MODEL, parent_container=container))
    container.native.setStyleSheet("QWidget { font-size: 16px; }")
    container.show(run=True)


if __name__ == "__main__":
    main()
