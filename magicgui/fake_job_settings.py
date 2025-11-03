"""
Fake JobSettings model for testing

Mocks the real JobSettings from AIND Data Transfer Lite, validating
metadata and modality directories and storing optional settings
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
