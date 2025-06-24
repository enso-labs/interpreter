<h1 align="center">
  🤖 Prompt Engineers AI - Secure Code Interpreter (Sandboxed) 
</h1>

<p align="center">
  <a href="https://promptengineers-ai.gitbook.io/documentation/open-source"><img src="https://img.shields.io/badge/View%20Documentation-Docs-yellow"></a>
  <a href="https://join.slack.com/t/promptengineersai/shared_invite/zt-21upjsftv-gX~gNjTCU~2HfbeM_ZwTEQ"><img src="https://img.shields.io/badge/Join%20our%20community-Slack-blue"></a>
</p>

Unlock the potential of executing Python code safely and efficiently with the Prompt Engineers AI - Secure Code Interpreter. This API provides a robust sandboxed environment where users can execute Python scripts, upload files, install packages, and manage sessions with complete isolation from your main application code. Each session is meticulously separated, ensuring that the code, files, and packages for one session do not interfere with others, thereby enhancing security and preventing potential conflicts.

Our sandbox is designed with security as a top priority. By isolating execution environments, we mitigate risks associated with running untrusted code. This makes it an ideal solution for developers and organizations who need a safe and controlled way to execute scripts, test code snippets, or provide coding functionalities within their applications.

Key Features:
- 🛡️ **Secure Execution:** Run Python code in a sandboxed environment to ensure the applications remains secure and unaffected.
- 📁 **File Management:** Upload and manage files within isolated sessions to maintain data integrity and security.
- 📦 **Package Installation:** Install required Python packages per session without affecting the global environment.
- 🕹️ **Session Management:** Efficiently create, manage, and terminate sessions to maintain clean and organized execution spaces.

### Start Interpreter
```bash
docker-compose up --build
```

### Test the Langchain Toolkit
```bash
## Change Directory
cd toolkit

## Create Virtual Env
python3 -m venv .venv
source .venv/bin/activate

## Install Dependencies
pip install -r requirements.txt

## Run Script to view & test tool
python interpreter.py
```

### Example Requests

Simple Example

```bash
curl -X POST http://localhost:8001/execute -H "Content-Type: application/json" -d '{
  "session_id": "your_session_id",
  "code": "print(\"Hello from Interpreter!\")"
}'

## Result
# {"status":"success","output":"Hello from Interpreter!\n","errors":""}
```

Example curl Request (Verify will error when numpy is not installed):

```bash
curl -X POST http://localhost:8001/execute -H "Content-Type: application/json" -d '{
  "session_id": "your_session_id",
  "code": "import os\nimport numpy as np\na = int(os.getenv(\"VAR_A\"))\nb = int(os.getenv(\"VAR_B\"))\nc = int(os.getenv(\"VAR_C\"))\narray = np.array([a, b, c])\nresult = np.sum(array)\nprint(f\"Result of summing [{a}, {b}, {c}] is: {result}\")",
  "env": {
    "VAR_A": "10",
    "VAR_B": "20",
    "VAR_C": "30"
  }
}'

## Result
# {"status":"success","output":"","errors":"Traceback (most recent call last):\n  File \"/tmp/your_session_id/temp_code.py\", line 2, in <module>\n    import numpy as np\nModuleNotFoundError: No module named 'numpy'\n"}
```

Example curl Request (Install numpy and execute the code):

```bash
curl -X POST http://localhost:8001/install -H "Content-Type: application/json" -d '{
  "session_id": "your_session_id",
  "packages": ["numpy"]
}'

## Result
# {"status":"success","installed_packages":["numpy"]}
```

Execute numpy with Env vars

```bash
curl -X POST http://localhost:8001/execute -H "Content-Type: application/json" -d '{
  "session_id": "your_session_id",
  "code": "import os\nimport numpy as np\na = int(os.getenv(\"VAR_A\"))\nb = int(os.getenv(\"VAR_B\"))\nc = int(os.getenv(\"VAR_C\"))\narray = np.array([a, b, c])\nresult = np.sum(array)\nprint(f\"Result of summing [{a}, {b}, {c}] is: {result}\")",
  "env": {
    "VAR_A": "10",
    "VAR_B": "20",
    "VAR_C": "30"
  }
}'

## Result
# {"status":"success","output":"Result of summing [10, 20, 30] is: 60\n","errors":""}
```

Example curl Request (Verify numpy has been uninstalled):

```bash
curl -X POST http://localhost:8001/terminate -H "Content-Type: application/json" -d '{
  "session_id": "your_session_id"
}'

## Result
# {"status":"success","message":"Session your_session_id terminated successfully."}

curl -X POST http://localhost:8001/execute -H "Content-Type: application/json" -d '{
  "session_id": "your_session_id",
  "code": "import os\nimport numpy as np\na = int(os.getenv(\"VAR_A\"))\nb = int(os.getenv(\"VAR_B\"))\nc = int(os.getenv(\"VAR_C\"))\narray = np.array([a, b, c])\nresult = np.sum(array)\nprint(f\"Result of summing [{a}, {b}, {c}] is: {result}\")",
  "env": {
    "VAR_A": "10",
    "VAR_B": "20",
    "VAR_C": "30"
  }
}'

## Result
# {"status":"success","output":"","errors":"Traceback (most recent call last):\n  File \"/tmp/your_session_id/temp_code.py\", line 2, in <module>\n    import numpy as np\nModuleNotFoundError: No module named 'numpy'\n"}
```

### Execute against files

Upload a file for a specific session.

```bash
curl -X POST "http://localhost:8001/upload" \
  -H "accept: application/json" \
  -F "session_id=your_session_id" \
  -F "file=@data/AAPL.csv"

## Result
# {"filename":"AAPL.csv","location":"/tmp/your_session_id/AAPL.csv"}
```

Install pandas pacakage for created session to interact with csv.

```bash
curl -X POST http://localhost:8001/install -H "Content-Type: application/json" -d '{
  "session_id": "your_session_id",
  "packages": ["pandas"]
}'

## Result
# {"status":"success","installed_packages":["pandas"]}
```

Execute to interact with csv

```bash
curl -X POST http://localhost:8001/execute -H "Content-Type: application/json" -d '{
  "session_id": "your_session_id",
  "code": "import pandas as pd\nfile_path = \"/tmp/your_session_id/AAPL.csv\"\ndf = pd.read_csv(file_path)\nfirst_row = df.iloc[0]\nprint(first_row.to_json())"
}'

## Result
# {"status":"success","output":"{\"Date\":\"2022-03-16\",\"Open\":157.050003,\"High\":160.0,\"Low\":154.460007,\"Close\":159.589996,\"Adj Close\":158.629059,\"Volume\":102300200}\n","errors":""}
```

Download file from session

```bash
curl -X GET "http://localhost:8001/download?session_id=your_session_id&filename=AAPL.csv" -o AAPL_downloaded.csv

## Result
# File downloaded to workspace
```

Terminate session to uninstall pacakges and remove files.

```bash
curl -X POST http://localhost:8001/terminate -H "Content-Type: application/json" -d '{
  "session_id": "your_session_id"
}'

## Result
# {"status":"success","message":"Session your_session_id terminated successfully."}
```


```bash
docker run -d \
  --name jupyter \
  --restart always \
  --env-file .env.jupyter \
  -p 8888:8888 \
  -v "$PWD/notebooks:/home/jovyan/work" \
  -v jupyter_data:/home/jovyan/.jupyter \
  jupyter/base-notebook:latest
```