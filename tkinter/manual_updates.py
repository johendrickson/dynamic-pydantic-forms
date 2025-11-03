"""
Tkinter + Pydantic Manual Dynamic Form (PoC)

This script demonstrates a "manual" approach to creating a GUI form with Tkinter
where input fields are generated from a Pydantic model. It validates user input
using Pydantic and shows results or errors via message boxes

Manual / Semi-Dynamic Behavior:
- The form fields are generated automatically from the Pydantic model (`UploadMetadata`)
- Submissions are validated using Pydantic; validation errors are displayed in
  a Tkinter messagebox
- Adding new fields requires modifying the Pydantic model or defining a subclass
  (as done in the `simulate_model_update` function). The form is rebuilt dynamically
  using the `update_model` method without restarting the GUI
- This version is more "manual" because adding new fields is done in-code
  rather than by editing an external module and reloading

Usage:
1. Install dependencies using `pip install -r tkinter/requirements.txt`
2. Run the script
3. Fill in the form and submit; validated JSON is displayed in a messagebox
4. Click "Simulate Model Update" to add a new optional field and rebuild the form
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional

from pydantic import BaseModel, Field, ValidationError


# -------------------------------
# Step 1: Define a sample Pydantic model
# -------------------------------
class UploadMetadata(BaseModel):
    experiment_name: str = Field(..., title="Experiment Name")
    principal_investigator: str = Field(..., title="Principal Investigator")
    data_type: str = Field(..., title="Data Type (e.g. ecephys, behavior)")
    date_collected: str = Field(..., title="Date Collected (YYYY-MM-DD)")
    s3_bucket_target: Optional[str] = Field("aind-open-data", title="S3 Bucket Target")


# -------------------------------
# Step 2: Dynamic Tkinter form
# -------------------------------
class PydanticForm(tk.Frame):
    def __init__(self, master, model_cls: type[BaseModel]):
        super().__init__(master)
        self.model_cls = model_cls
        self.entries = {}
        self.build_form()

    def build_form(self):
        """Dynamically create labels and entries for each Pydantic field"""
        for widget in self.winfo_children():
            widget.destroy()

        for idx, (name, field) in enumerate(self.model_cls.model_fields.items()):
            label_text = field.title or name.replace("_", " ").title()
            tk.Label(self, text=label_text).grid(
                row=idx, column=0, sticky="w", padx=5, pady=3
            )

            entry = tk.Entry(self, width=40)
            entry.insert(0, str(field.default) if field.default is not None else "")
            entry.grid(row=idx, column=1, padx=5, pady=3)
            self.entries[name] = entry

        # Submit button
        tk.Button(self, text="Submit", command=self.submit).grid(
            row=len(self.model_cls.model_fields), columnspan=2, pady=10
        )

    def submit(self):
        """Validate and show results"""
        data = {name: entry.get() for name, entry in self.entries.items()}
        try:
            validated = self.model_cls(**data)
            messagebox.showinfo(
                "Success",
                f"Validated Data:\n{validated.model_dump_json(indent=2)}",
            )
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))

    def update_model(self, new_model_cls: type[BaseModel]):
        """Rebuild form for updated model"""
        self.model_cls = new_model_cls
        self.build_form()


# -------------------------------
# Step 3: Main application
# -------------------------------
def main():
    root = tk.Tk()
    root.title("Tkinter + Pydantic Dynamic Form (PoC)")

    form = PydanticForm(root, UploadMetadata)
    form.pack(padx=10, pady=10)

    # Simulate a model update (e.g., new field added later)
    def simulate_model_update():
        class UpdatedMetadata(UploadMetadata):
            new_testing_field: Optional[str] = Field(None, title="New Optional Field")

        form.update_model(UpdatedMetadata)
        messagebox.showinfo("Model Update", "Form updated with new Pydantic field!")

    tk.Button(root, text="Simulate Model Update", command=simulate_model_update).pack(
        pady=5
    )

    root.mainloop()


if __name__ == "__main__":
    main()
