"""
Pydantic model definitions for dynamic form PoCs

This file defines the `UploadMetadata` Pydantic model, which serves as the schema
for form input fields in various proof-of-concept (PoC) scripts. Each field has
a type, optional default value, and an optional title for display purposes

Connection to other scripts:
- The Tkinter PoC (`tkinter_dynamic_form.py` or similar) imports this model to
  dynamically generate input fields

Usage:
1. Import the model in your PoC script:
       from models import UploadMetadata
2. Use `UploadMetadata` for form generation and validation
3. Modify fields here to simulate dynamic schema updates for testing
"""

from typing import Optional

from pydantic import BaseModel, Field


class UploadMetadata(BaseModel):
    experiment_name: str = Field(..., title="Experiment Name")
    principal_investigator: str = Field(..., title="Principal Investigator")
    data_type: str = Field(..., title="Data Type (e.g. ecephys, behavior)")
    date_collected: str = Field(..., title="Date Collected (YYYY-MM-DD)")
    s3_bucket_target: Optional[str] = Field("aind-open-data", title="S3 Bucket Target")
    new_testing_field: str = Field("huzzah!", title="Our New Field!")
    dry_run: bool = Field(..., title="Boolean test")
