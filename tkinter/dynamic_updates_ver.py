"""
Tkinter + Pydantic Dynamic Form with Module Reload

This script demonstrates a semi-dynamic GUI form built with Tkinter, where
form fields are automatically generated from a Pydantic model defined in
`models.py` and validated upon submission

Manual / Dynamic Behavior:
- The form fields are generated automatically from the Pydantic model
  class passed to `PydanticForm`
- Submissions are validated using Pydantic; errors are shown in a messagebox.
- The model can be updated dynamically by reloading the `models` module
  (via the "Reload Model from models.py" button), which rebuilds the form
  with any new or changed fields
- Fully new fields require editing `models.py`, but they appear in the GUI
  without restarting the application after hitting "Reload Model"

Usage:
1. Install dependencies using `pip install -r tkinter/requirements.txt`
2. Place your Pydantic model(s) in `models.py`. The default model should be
   `UploadMetadata`
3. Run the script
4. Fill in the form and submit; validated JSON is displayed in a messagebox
5. To test dynamic updates, modify `models.py` (e.g., add a new field to
   `UploadMetadata`) and click "Reload Model from models.py" in the GUI
   to rebuild the form

"""

import importlib
import tkinter as tk
from tkinter import messagebox

import models
from pydantic import BaseModel, ValidationError
from pydantic.fields import PydanticUndefined

# update the model in models.py for a dynamic update


class PydanticForm(tk.Frame):
    def __init__(self, master, model_cls: type[BaseModel]):
        super().__init__(master)
        self.model_cls = model_cls
        self.entries = {}
        self.build_form()

    def build_form(self):
        for widget in self.winfo_children():
            widget.destroy()

        for idx, (name, field) in enumerate(self.model_cls.model_fields.items()):
            label_text = field.title or name.replace("_", " ").title()
            default_val = "" if field.default is PydanticUndefined else field.default

            tk.Label(self, text=label_text).grid(
                row=idx, column=0, sticky="w", padx=5, pady=3
            )
            entry = tk.Entry(self, width=40)
            entry.insert(0, str(default_val))
            entry.grid(row=idx, column=1, padx=5, pady=3)
            self.entries[name] = entry

        tk.Button(self, text="Submit", command=self.submit).grid(
            row=len(self.model_cls.model_fields), columnspan=2, pady=10
        )

    def submit(self):
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
        self.model_cls = new_model_cls
        self.build_form()


def main():
    root = tk.Tk()
    root.title("Tkinter + Pydantic Dynamic Form with Module Reload")

    # initial model
    form = PydanticForm(root, models.UploadMetadata)
    form.pack(padx=10, pady=10)

    # simulate dynamic module reload
    def reload_model():
        importlib.reload(models)  # reload the module
        UpdatedModel = models.UploadMetadata  # get the latest model
        form.update_model(UpdatedModel)
        messagebox.showinfo("Model Reloaded", "Form updated from reloaded module!")

    tk.Button(root, text="Reload Model from models.py", command=reload_model).pack(
        pady=5
    )

    root.mainloop()


if __name__ == "__main__":
    main()
