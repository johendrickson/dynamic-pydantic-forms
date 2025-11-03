"""
This script demonstrates a more "manual" approach to generating and
validating HTML forms from a Pydantic model using FastAPI

The form fields are automatically rendered from the UploadMetadata
class via the render_form function, and submissions are validated
against the same model to ensure required fields and default values
are enforced. Adding new fields is manual: you must uncomment or
add the field in both UploadMetadata and the submit_form endpoint
to have it appear in the form and be processed

Usage:
1. Install dependencies using `pip install -r fastui/requirements.txt`
2. Run the server
3. Open a browser at http://127.0.0.1:8000 to view and submit the form
4. To add new fields, uncomment the relevant lines in `UploadMetadata` and
   in the `submit_form` endpoint, then reload the server
"""

from typing import Optional

import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from pydantic.fields import PydanticUndefined


# -------------------------------
# Step 1: Define Pydantic model
# -------------------------------
class UploadMetadata(BaseModel):
    experiment_name: str = Field(..., title="Experiment Name")
    principal_investigator: str = Field(..., title="Principal Investigator")
    data_type: str = Field(..., title="Data Type (e.g., behavior, ecephys)")
    date_collected: str = Field(..., title="Date Collected (YYYY-MM-DD)")
    s3_bucket_target: Optional[str] = Field("aind-open-data", title="S3 Bucket Target")
    # new_testing_field: str = Field("huzzah!", title="Our New Field!")


# Uncomment `new_testing_field` to simulate a new field added later.


# -------------------------------
# Step 2: FastAPI + simple form rendering
# -------------------------------
app = FastAPI(title="FastUI PoC - Dynamic Pydantic Form")


def render_form(model_cls):
    html = "<form method='post'>"
    for name, field in model_cls.model_fields.items():
        title = field.title or name.replace("_", " ").title()
        default_val = "" if field.default is PydanticUndefined else field.default
        html += f"<label>{title}:</label><br>"
        html += f"<input type='text' name='{name}' value='{default_val}'><br><br>"
    html += "<input type='submit' value='Submit'>"
    html += "</form>"
    return html


@app.get("/", response_class=HTMLResponse)
async def get_form():
    return render_form(UploadMetadata)


@app.post("/submit", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    experiment_name: str = Form(...),
    principal_investigator: str = Form(...),
    data_type: str = Form(...),
    date_collected: str = Form(...),
    s3_bucket_target: str = Form("aind-open-data"),
    # new_testing_field: str = Form("huzzah!")
):
    # Collect form data into Pydantic model
    data = {
        "experiment_name": experiment_name,
        "principal_investigator": principal_investigator,
        "data_type": data_type,
        "date_collected": date_collected,
        "s3_bucket_target": s3_bucket_target,
        # "new_testing_field": new_testing_field
        # Uncomment `new_testing_field` to simulate a new field added later.
    }
    try:
        validated = UploadMetadata(**data)
        return (
            f"<h3>Success! Validated Data:</h3>"
            f"<pre>{validated.model_dump_json(indent=2)}</pre>"
            f"<a href='/'>Back to form</a>"
        )
    except Exception as e:
        return f"<h3>Error:</h3><pre>{str(e)}</pre>"


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
