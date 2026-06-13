# WaterDIP

**WaterDIP** is a Production Decline and Water Breakthrough Decision Intelligence Platform.

An end-to-end ML Platform Assistant designed to support production analytics, decline curve analysis, water breakthrough monitoring, and intelligent decision-making workflows across energy operations.

---

## Local Development Test Run

### Prerequisites

* Windows environment
* Python installed and available on `PATH`

### Start the Application

- Navigate to the project root directory (WaterDIP), then change directory to the FAST-API backend directory.

```powershell
PS C:\Users\Harrison.Obidinnu\WaterDIP> cd genai-microservice
```

- Activate the backend directory and start-up a new FAST-API backend process:

```powershell
PS C:\Users\Harrison.Obidinnu\WaterDIP\genai-microservice> .venv\Scripts\activate
(.venv) PS C:\Users\Harrison.Obidinnu\WaterDIP\genai-microservice> uvicorn app.main:app --reload --host 127.0.0.1 --port 8080    
```


- While the backend process is active, spawn up a new shell process (which starts again at the project root) for the Flask Frontend.

- Confirm that .venv is deactivated (if shell is configured to activate at start-up by default)

```powershell
(.venv) PS C:\Users\Harrison.Obidinnu\WaterDIP> deactivate
```

- Start the flask application from the shell:

```powershell
PS C:\Users\Harrison.Obidinnu\WaterDIP> python llm.py
```

Expected startup output:

```text
instance path is ... C:\Users\Harrison.Obidinnu\WaterDIP\instance
Windows automatically sets python path.
finished setting project and python paths
/app/llm
platform name is ... CCLNG-14062129
ensured database tables exist in vLLM_App.db
has_user_table is ...True
has_note_table is ...True
 * Serving Flask app 'website'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Access the Application

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

### Verify LLM Demo Page

Navigate to:

```text
http://127.0.0.1:5000/app/llm
```

Expected log output:

```text
running LLM demo page
root path is ...C:\Users\Harrison.Obidinnu\WaterDIP\website
current working directory is C:\Users\Harrison.Obidinnu\WaterDIP
I'm in ready_for_upload
127.0.0.1 - - [timestamp] "GET /app/llm HTTP/1.1" 200 -
```

A successful `HTTP 200` response confirms that the local development environment is functioning correctly.

---

## Status

Initial repository bootstrap and local development validation.
