"""
A fake/mock JobSettings model for testing the Tkinter PoC GUI.

This class emulates the real JobSettings from the AIND Data Transfer Lite
repository, validating metadata and modality directories and storing optional
parameters like dry run and S3 bucket. The `_modality_abbreviations` list
provides sample keys for mapping modalities.
"""

from typing import ClassVar, Dict, List

from pydantic import BaseModel, DirectoryPath


class JobSettings(BaseModel):
    metadata_directory: DirectoryPath
    modality_directories: Dict[str, DirectoryPath]
    dry_run: bool = True
    s3_bucket: str = "aind-open-data"

    _modality_abbreviations: ClassVar[List[str]] = [
        "behavior",
        "ecephys",
        "brightfield",
    ]
