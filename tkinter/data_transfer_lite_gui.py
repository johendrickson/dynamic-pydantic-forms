"""
A proof-of-concept GUI for the AIND Data Transfer Lite workflow using Tkinter.

The GUI is a Tkinter adaptation of a previously implemented MagicGUI + Qt PoC,
using a simplified `JobSettings` class to emulate validation logic without
requiring the full AIND Data Transfer Lite repository.

Usage:
1. Install dependencies using `pip install -r tkinter/requirements.txt`
2. Run the script
3. Interact with the GUI:
   - Browse to select metadata and modality directories
   - Optionally toggle "Dry Run" or edit the S3 bucket
   - Click "Validate" to check inputs
   - Click "Submit" to simulate job submission if validation passes
   - Use "Copy Output" to copy validation/submission results to the clipboard
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from fake_job_settings import JobSettings

validation_passed = False


class ADTLPoC(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AIND Data Transfer Lite PoC")
        self.geometry("700x600")
        self.metadata_path = tk.StringVar()
        self.modality_paths = []
        self.dry_run = tk.BooleanVar(value=True)
        self.s3_bucket = tk.StringVar(value="aind-open-data")
        self.create_widgets()

    def create_widgets(self):
        # Metadata directory
        tk.Label(self, text="Metadata Directory:").pack(anchor="w", padx=10, pady=2)
        meta_frame = tk.Frame(self)
        meta_frame.pack(fill="x", padx=10)
        tk.Entry(meta_frame, textvariable=self.metadata_path, width=50).pack(
            side="left"
        )
        tk.Button(meta_frame, text="Browse", command=self.browse_metadata).pack(
            side="left", padx=5
        )

        # Modality directories
        self.modality_frame = tk.Frame(self)
        self.modality_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(self.modality_frame, text="Modality Directories:").pack(anchor="w")
        self.add_modality_field()
        tk.Button(
            self, text="Add another modality directory", command=self.add_modality_field
        ).pack(padx=10, pady=2)

        # Optional fields
        tk.Checkbutton(self, text="Dry Run (Optional)", variable=self.dry_run).pack(
            anchor="w", padx=10, pady=2
        )
        tk.Label(self, text="S3 Bucket (Optional):").pack(anchor="w", padx=10)
        tk.Entry(self, textvariable=self.s3_bucket, width=50).pack(padx=10, pady=2)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_frame, text="Validate", command=self.validate).pack(
            side="left", padx=5
        )
        tk.Button(btn_frame, text="Submit", command=self.submit).pack(
            side="left", padx=5
        )
        tk.Button(btn_frame, text="Copy Output", command=self.copy_output).pack(
            side="left", padx=5
        )

        # Output
        tk.Label(self, text="Output:").pack(anchor="w", padx=10)
        self.output_box = tk.Text(self, height=15, wrap="word")
        self.output_box.pack(fill="both", padx=10, pady=2, expand=True)
        self.output_box.config(state="disabled")

    def browse_metadata(self):
        path = filedialog.askdirectory()
        if path:
            self.metadata_path.set(path)

    def add_modality_field(self):
        path_var = tk.StringVar()
        self.modality_paths.append(path_var)
        frame = tk.Frame(self.modality_frame)
        frame.pack(fill="x", pady=2)
        tk.Entry(frame, textvariable=path_var, width=50).pack(side="left")
        tk.Button(
            frame, text="Browse", command=lambda v=path_var: self.browse_modality(v)
        ).pack(side="left", padx=5)

    def browse_modality(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    def write_output(self, text):
        self.output_box.config(state="normal")
        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, text)
        self.output_box.config(state="disabled")

    def validate(self):
        global validation_passed
        metadata = self.metadata_path.get()
        modalities = [v.get() for v in self.modality_paths if v.get()]
        dry = self.dry_run.get()
        s3 = self.s3_bucket.get()

        errors = []
        if not metadata:
            errors.append("Metadata directory is required")
        if not modalities:
            errors.append("At least one modality directory is required")

        if errors:
            errors = [errors[0]] + [e[0].lower() + e[1:] for e in errors[1:]]
            self.write_output("Error: " + " and ".join(errors) + ".")
            validation_passed = False
            return

        try:
            keys = JobSettings._modality_abbreviations[: len(modalities)]
            mod_dict = dict(zip(keys, modalities))
            job = JobSettings(
                metadata_directory=metadata,
                modality_directories=mod_dict,
                dry_run=dry,
                s3_bucket=s3,
            )
            self.write_output(
                "Validation successful!\n" + job.model_dump_json(indent=2)
            )
            validation_passed = True
        except Exception as e:
            self.write_output(f"Error. Validation failed:\n{e}")
            validation_passed = False

    def submit(self):
        if not validation_passed:
            self.write_output(
                "Cannot submit. Job type invalid. See validation details."
            )
            return
        modalities = [v.get() for v in self.modality_paths if v.get()]
        self.write_output(
            f"Submitting Job with:\nMetadata: {self.metadata_path.get()}\n"
            f"Modalities: {modalities}\nDry Run: {self.dry_run.get()}\n"
            f"S3 Bucket: {self.s3_bucket.get()}"
        )

    def copy_output(self):
        self.clipboard_clear()
        self.clipboard_append(self.output_box.get("1.0", tk.END))
        self.update()
        messagebox.showinfo("Copied", "Output copied to clipboard")


if __name__ == "__main__":
    app = ADTLPoC()
    app.mainloop()
