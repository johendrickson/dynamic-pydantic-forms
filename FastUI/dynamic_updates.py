"""
This script demonstrates a more "dynamic" approach to generating and
validating HTML forms from a Pydantic model using FastAPI. The form is
automatically generated from the `CURRENT_MODEL` class, and submissions
are validated against the same model

Manual / Dynamic Behavior:
- The form fields update automatically from the current Pydantic model
- New fields can be added dynamically using the `/update_model` endpoint,
  which creates a new model class inheriting from the current model
- After hitting "Simulate Model Update," the form will reflect new fields
  without manually modifying the HTML generation code
- Full dynamic behavior is limited: adding completely custom fields still
  requires modifying the model class in code if you want them persisted

Usage:
1. Install dependencies using `pip install -r fastui/requirements.txt`
2. Run the server
3. Open a browser at http://127.0.0.1:8000 to view and submit the form
4. Submit the form with initial fields to see validated JSON output.
5. Click "Simulate Model Update" to add a new field dynamically, then go
   back to the form to see it appear automatically
6. Submitting the updated form validates the new field along with the
   original fields
"""

from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from pydantic.fields import PydanticUndefined


# -------------------------------
# Step 1: Define initial Pydantic model
# -------------------------------
class UploadMetadata(BaseModel):
    experiment_name: str = Field(..., title="Experiment Name")
    principal_investigator: str = Field(..., title="Principal Investigator")
    data_type: str = Field(..., title="Data Type (e.g., behavior, ecephys)")
    date_collected: str = Field(..., title="Date Collected (YYYY-MM-DD)")
    s3_bucket_target: Optional[str] = Field("aind-open-data", title="S3 Bucket Target")


# -------------------------------
# Step 2: FastAPI app and model state
# -------------------------------
app = FastAPI(title="FastUI Dynamic Pydantic Form PoC")

# Store the current model as global state for dynamic updates
CURRENT_MODEL = UploadMetadata


def render_form():
    """Render HTML form based on CURRENT_MODEL"""
    model_cls = CURRENT_MODEL
    html = "<h2>Upload Metadata Form</h2>"
    html += "<form method='post' action='/submit'>"

    for name, field in model_cls.model_fields.items():
        title = field.title or name.replace("_", " ").title()
        # Use empty string if no default
        if field.default is PydanticUndefined:
            default_val = ""
        elif field.default is None:
            default_val = ""
        else:
            default_val = field.default
        html += f"<label>{title}:</label><br>"
        html += f"<input type='text' name='{name}' value='{default_val}'><br><br>"

    html += "<input type='submit' value='Submit'>"
    html += "</form>"

    html += "<form method='post' action='/update_model' style='margin-top:20px;'>"
    html += "<input type='submit' value='Simulate Model Update (add new field)'>"
    html += "</form>"

    return html


# -------------------------------
# Step 3: GET form
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def get_form():
    return render_form()


# -------------------------------
# Step 4: POST form submission
# -------------------------------
@app.post("/submit", response_class=HTMLResponse)
async def submit_form(request: Request):
    form_data = await request.form()
    data = dict(form_data)
    try:
        validated = CURRENT_MODEL(**data)
        return (
            f"<h3>Success! Validated Data:</h3>"
            f"<pre>{validated.model_dump_json(indent=2)}</pre>"
            f"<a href='/'>Back to form</a>"
        )
    except Exception as e:
        return f"<h3>Error:</h3><pre>{str(e)}</pre><a href='/'>Back to form</a>"


# -------------------------------
# Step 5: POST endpoint to simulate dynamic model update
# -------------------------------
@app.post("/update_model", response_class=HTMLResponse)
async def update_model():
    global CURRENT_MODEL

    # Create a new model class inheriting from CURRENT_MODEL with a new field
    class UpdatedMetadata(CURRENT_MODEL):
        new_testing_field: str = Field("huzzah!", title="Our New Field!")

    CURRENT_MODEL = UpdatedMetadata
    return "<h3>Model updated! New field added.</h3><a href='/'>Back to form</a>"


# -------------------------------
# Step 6: Run server
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)