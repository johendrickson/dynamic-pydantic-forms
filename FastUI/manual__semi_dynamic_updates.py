"""
This script demonstrates a "manual semi-dynamic" approach to generating and
validating HTML forms from a Pydantic model using FastAPI

Manual / Semi-Dynamic: The form fields are generated automatically from
the Pydantic model (`UploadMetadata`), but adding new fields still requires
updating the Python class. The dynamic part comes from the fact that you
can modify the model and reload the server to see changes reflected in the form

Usage:
1. Install dependencies using `pip install -r fastui/requirements.txt`
2. Run the server
3. Open browser at `http://127.0.0.1:8000` to use the form
4. To add new fields, modify `UploadMetadata` and reload the server
"""

from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
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
    # new_testing_field: str = Field("huzzah!", title="New Optional Field")


# Uncomment `new_testing_field` to simulate a new field added later.
# If you run:
#     python -m uvicorn FastUI.better_dynamic_updates:app --reload
# in the terminal, you don’t have to restart the program —
# only reload to see schema changes take effect.

# -------------------------------
# Step 2: FastAPI app
# -------------------------------
app = FastAPI(title="FastUI Dynamic PoC")


def render_form(model_cls):
    """Generate HTML form from Pydantic model."""
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
async def submit_form(request: Request):
    # Dynamically read all form fields
    form_data = await request.form()
    data = dict(form_data)

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
