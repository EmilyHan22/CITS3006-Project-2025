# CITS3006-Project-2025
## Team 17:
- Emily Han (23925907)
- Aung Phone Hein (23738739)
- Jake Blackburne (23782618)
- Vincent Ta (23975858)

**Point of Contact:** Jake

### Reports
Reports for Tasks 1 and 2 in Google Docs.
Link: https://docs.google.com/document/d/16IExvQyQPki9rLnz035yEToeajHfd5sK6XYudVQQuAo/edit?usp=sharing

## Project Description
### Task 1:
Make a VirtualBox with 6 vulnerabilities. 

## Environment Setup Guide

### 1. Create a Virtual Environment

Creating a virtual environment ensures that project dependencies do not conflict with other Python projects on your system.

```bash
# Create a virtual environment named "venv"
python -m venv venv
```

Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

If the environment is active, your terminal prompt should show `(venv)`.

### 2. Install Dependencies

Install all required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Verify the Installation

Run the following command to confirm all dependencies are installed correctly:

```bash
python -m pip list
```

You should see the packages from `requirements.txt` listed.

### 4. Running the Application

To run the application:

```bash
python database.py
python app.py
```

### 5. Deactivating the Virtual Environment

When you are done working on the project, deactivate the virtual environment:

```bash
deactivate
```

### 6. Optional: Updating Dependencies

If new packages are installed, update `requirements.txt`:

```bash
pip freeze > requirements.txt
```

Commit the updated file so the team can stay in sync.

---




