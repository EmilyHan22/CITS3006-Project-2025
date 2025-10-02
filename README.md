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

Run the following command to confirm all dependencies are installed correctly:

```bash
python -m pip list
```

You should see the packages from `requirements.txt` listed.

### 3. Set up

```bash
python database.py
python setup.py
```

### 4. Running the Application

To run the application:

```bash
python app.py
```

### 5. Deactivating the Virtual Environment

When you are done working on the project, deactivate the virtual environment:

```bash
deactivate
```

## To test Vulnerabilities:

### Web Vulnerability: Stored XSS in Announcements. 

1. Go to Announcement Page. 
2. Create an announcement with a script in the body of the announcement
```
<script>
if(!document.getElementById('xss-banner')){
  var b = document.createElement('div');
  b.id = 'xss-banner';
  b.style.cssText = 'position:fixed;left:0;right:0;top:0;padding:10px 12px;background:#e74c3c;color:#fff;font-weight:600;z-index:99999;text-align:center';
  b.innerHTML = 'XSS DEMO — This page has been XSSed! <button id="xss-close" style="margin-left:8px;padding:2px 8px;border:none;border-radius:4px;cursor:pointer">×</button>';
  document.documentElement.appendChild(b);
  document.getElementById('xss-close').onclick = function(){ b.remove(); };
  setTimeout(function(){ if(b.parentNode) b.remove(); }, 15000);
}
</script>
```
3. Post the announcement
4. See the change (a pop up banner message to show it worked)
5. Now, everytime the page is refreshed, click out and back into the page, the pop up will appear. 




