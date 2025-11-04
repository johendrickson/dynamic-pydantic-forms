# Interactive Form PoCs with Pydantic

This repository contains multiple proof-of-concept interactive forms using
 **Pydantic** for data validation, implemented in different UI frameworks:
 **Tkinter**, **MagicGui + Qt**, **FastUI**, and **Jupyter Notebook**

---
## Folder Overview

### 1. `tkinter/`
- **Purpose:** A desktop GUI version of the AIND Data Transfer Lite workflow using **Tkinter**
- **Features:**
  - Select a metadata directory
  - Select one or more modality directories (add more dynamically)
  - Optional settings: Dry Run and S3 Bucket
  - Validate inputs against a fake `JobSettings` Pydantic model
  - Output box displays validation results, and content can be copied to clipboard
---

### 2. `magicgui/`
- **Purpose:** A Qt-based interactive form PoC using **MagicGUI**
- **Features:**
  - Dynamically generate form from a Pydantic model
  - Add/delete multiple modality directories
  - Optional Dry Run and S3 Bucket fields
  - Validate and submit configuration
  - Output is read-only but selectable; can copy to clipboard
---

### 3. `fastui/`
- **Purpose:** A **FastAPI** + HTML version of a dynamic form
- **Features:**
  - Dynamically generates a form from a Pydantic model on a web page
  - POST form submission validates data and shows success or error messages
  - Simulate model updates by adding new fields dynamically
---

### 4. `jupyter_notebook/`
- **Purpose:** Interactive form inside a **Jupyter Notebook** using **ipywidgets**
- **Features:**
  - Dynamically generates fields from a Pydantic model
  - Submit button validates the inputs
  - Simulate model updates by adding new fields dynamically
  - Output is displayed below the form
---

## Requirements
Each subproject has its own `requirements.txt`. Make sure to install dependencies in a dedicated virtual environment for each if needed
