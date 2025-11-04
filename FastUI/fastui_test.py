"""Working FastUI Dynamic Pydantic Form PoC"""

from typing import Optional, List
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

from fastui import FastUI, components as c
from fastui.events import GoToEvent
from fastapi.responses import RedirectResponse

# -------------------------------
# Step 1: Define initial Pydantic model
# -------------------------------
class UploadMetadata(BaseModel):
    experiment_name: str = Field(..., title="Experiment Name")
    principal_investigator: str = Field(..., title="Principal Investigator")
    data_type: str = Field(..., title="Data Type")
    date_collected: str = Field(..., title="Date Collected (YYYY-MM-DD)")
    s3_bucket_target: Optional[str] = Field("aind-open-data", title="S3 Bucket Target")

CURRENT_MODEL = UploadMetadata

# -------------------------------
# Step 2: FastAPI + FastUI setup
# -------------------------------
app = FastAPI(title="FastUI Dynamic Pydantic Form PoC")
fastui_app = FastUI(root=c.Page(components=[]))
app.mount("/fastui", fastui_app)

# -------------------------------
# Step 3: Root redirect
# -------------------------------
@app.get("/")
def root():
    return RedirectResponse("/fastui")

# -------------------------------
# Step 4: Render form dynamically
# -------------------------------
@app.get("/fastui", response_model=c.Page)
@app.get("/fastui", response_model=c.Page)
def get_form():
    # Dynamically create form fields from CURRENT_MODEL
    form_fields = []

    for name, field in CURRENT_MODEL.model_fields.items():
        if name == "data_type":
            options = [
                {"label": "Behavior", "value": "behavior"},
                {"label": "Ecephys", "value": "ecephys"},
                {"label": "Brightfield", "value": "brightfield"},
            ]
            form_fields.append(
                c.FormFieldSelect(
                    name=name,
                    title=field.title or name,
                    options=options,
                    required=True,
                    placeholder="Select a data type"
                )
            )
        else:
            form_fields.append(
                c.FormFieldInput(
                    name=name,
                    title=field.title or name,
                    required=True
                )
            )

    return c.Page(
        components=[
            c.Form(
                form_fields=form_fields,
                submit_url="/submit"  # Form automatically uses POST here
            ),
            # Extra buttons go at the page level
            c.Button(
                text="Simulate Model Update",
                on_click=GoToEvent(url="/update_model")
            )
        ]
    )


# -------------------------------
# Step 5: Validate submission
# -------------------------------
@app.post("/submit", response_model=c.Page)
async def submit_form(data: dict):
    try:
        # Validate incoming data with the CURRENT_MODEL
        validated = CURRENT_MODEL(**data)

        # Return a FastUI page showing the validated data
        return c.Page(
            components=[
                c.Markdown(
                    text=f"✅ **Validated Data:**\n```json\n{validated.model_dump_json(indent=2)}\n```"
                ),
                c.Button(
                    text="Back to Form",
                    on_click=GoToEvent("/fastui")  # Go back to the form page
                ),
            ]
        )

    except Exception as e:
        # Return a page showing the error
        return c.Page(
            components=[
                c.Markdown(
                    text=f"❌ **Error:**\n```\n{str(e)}\n```"
                ),
                c.Button(
                    text="Back to Form",
                    on_click=GoToEvent("/fastui")
                ),
            ]
        )


# -------------------------------
# Step 6: Simulate dynamic model update
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
# Step 7: Run server
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
