"""Currently unfinished and in a non-working state."""


from typing import Optional

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

from fastui import FastUI
from fastui import components as c
from fastui.events import GoToEvent

# -------------------------------
# Step 1: Define initial Pydantic model
# -------------------------------
class UploadMetadata(BaseModel):
    experiment_name: str = Field(..., title="Experiment Name")
    principal_investigator: str = Field(..., title="Principal Investigator")
    data_type: str = Field(..., title="Data Type (e.g., behavior, ecephys)")
    date_collected: str = Field(..., title="Date Collected (YYYY-MM-DD)")
    s3_bucket_target: Optional[str] = Field("aind-open-data", title="S3 Bucket Target")

CURRENT_MODEL = UploadMetadata

# -------------------------------
# Step 2: FastAPI + FastUI setup
# -------------------------------
app = FastAPI(title="FastUI Dynamic Pydantic Form PoC")
fastui_app = FastUI()
app.mount("/fastui", fastui_app)

# -------------------------------
# Step 3: Render form dynamically from CURRENT_MODEL
# -------------------------------
@app.get("/fastui", response_model=c.Page)
def get_form():
    fields = [c.Input(field=name) for name in CURRENT_MODEL.model_fields]
    return c.Page(
        components=[
            c.Form(
                fields=fields,
                submit_url="/submit",
                submit_button=c.Button(text="Submit"),
                extra_buttons=[
                    c.Button(text="Simulate Model Update", on_click=GoToEvent("/update_model"))
                ],
            )
        ]
    )

# -------------------------------
# Step 4: Validate submission
# -------------------------------
@app.post("/submit", response_model=c.Page)
async def submit_form(data: dict):
    try:
        validated = CURRENT_MODEL(**data)
        return c.Page(
            components=[
                c.Markdown(text=f"✅ **Validated Data:**\n```json\n{validated.model_dump_json(indent=2)}\n```"),
                c.Button(text="Back to Form", on_click=GoToEvent("/fastui")),
            ]
        )
    except Exception as e:
        return c.Page(
            components=[
                c.Markdown(text=f"❌ **Error:**\n```\n{str(e)}\n```"),
                c.Button(text="Back to Form", on_click=GoToEvent("/fastui")),
            ]
        )

# -------------------------------
# Step 5: Simulate dynamic model update
# -------------------------------
@app.get("/update_model", response_model=c.Page)
def update_model():
    global CURRENT_MODEL

    class UpdatedMetadata(CURRENT_MODEL):
        new_testing_field: str = Field("huzzah!", title="Our New Field!")

    CURRENT_MODEL = UpdatedMetadata
    return c.Page(
        components=[
            c.Markdown(text="✅ Added a new field: `new_testing_field`"),
            c.Button(text="Back to Form", on_click=GoToEvent("/fastui")),
        ]
    )

# -------------------------------
# Step 6: Run server
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
