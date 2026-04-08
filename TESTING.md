# AIPlatformEnv — Testing Walkthrough

## Prerequisites

Make sure you are in the project directory:
```powershell
cd "C:\Users\hasto\OneDrive\Desktop\jasonhackathon"
```

---

## Step 1 — Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

Expected output: all packages installed with no errors.

---

## Step 2 — Run the Smoke Test (no server needed)

```powershell
python -c "
import sys; sys.path.insert(0, '.')
from env import AIPlatformEnv
from models import AIPlatformAction

for task in ['answer_selection', 'ranking_subtle', 'ambiguity_calibration']:
    e = AIPlatformEnv(task_name=task, seed=42)
    obs = e.reset()
    action = AIPlatformAction(selected_index=0, confidence=0.8)
    obs2, reward, done, info = e.step(action)
    print(f'{task}: reward={reward:.4f}, done={done}, correct_index={info[\"correct_index\"]}')
"
```

Expected output:
```
answer_selection: reward=0.0300, done=True, correct_index=2
ranking_subtle: reward=0.5000, done=True, correct_index=...
ambiguity_calibration: reward=0.2400, done=True, correct_index=2
```

---

## Step 3 — Start the Server

Open a terminal and run:
```powershell
python server/app.py
```

Leave this running. The server starts at `http://localhost:8000`.

---

## Step 4 — Test API Endpoints

Open a **second terminal** and run each command.

### Health check
```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
```
✅ Expected: `status: ok`

### List tasks
```powershell
Invoke-RestMethod -Uri http://localhost:8000/tasks
```
✅ Expected: 3 tasks (answer_selection, ranking_subtle, ambiguity_calibration)

### Interactive docs
Open in browser: http://localhost:8000/docs

---

## Step 5 — Run a Full Episode via API

### Reset (Easy task)
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/reset `
  -ContentType "application/json" `
  -Body '{"task_name": "answer_selection"}'
```
Note the `candidate_responses` array in the output.

### Step (pick index 0, confidence 0.9)
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/step `
  -ContentType "application/json" `
  -Body '{"selected_index": 0, "confidence": 0.9, "reasoning": "testing"}'
```
✅ Expected: `reward` between 0.0–1.0, `done: true`

### Check state
```powershell
Invoke-RestMethod -Uri http://localhost:8000/state
```
✅ Expected: `step_count: 1`, `done: true`

---

## Step 6 — Run OpenEnv Validate

```powershell
& "C:\Users\hasto\AppData\Local\Python\pythoncore-3.14-64\Scripts\openenv.exe" validate
```
✅ Expected: `[OK] jasonhackathon: Ready for multi-mode deployment`

---

## Step 7 — Run Inference Script (requires API key)

```powershell
$env:HF_TOKEN     = "hf_your_token_here"
$env:API_BASE_URL = "https://router.huggingface.co/v1"
$env:MODEL_NAME   = "Qwen/Qwen2.5-72B-Instruct"
$env:API_URL      = "http://localhost:8000"

python inference.py
```

✅ Expected stdout format:
```
[START] task=answer_selection env=aiplatformenv model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=select(2, conf=0.85) reward=0.97 done=true error=null
[END] success=true steps=1 score=0.97 rewards=0.97
...
FINAL RESULTS:
  answer_selection: 0.9700
  ranking_subtle:   0.7000
  ambiguity_calibration: 0.5000
  Average: 0.7233
```

---

## Step 8 — Build & Run with Docker

```powershell
docker build -t aiplatformenv .
docker run -p 8000:8000 aiplatformenv
```

Then re-run Steps 4–6 to confirm everything works inside the container.

✅ Expected: Same API responses as local server.

---

## Summary Checklist

| Test | Command | Expected Result |
|---|---|---|
| Smoke test | `python -c ...` | 3 rewards printed |
| Server starts | `python server/app.py` | Running on port 8000 |
| Health endpoint | `/health` | `status: ok` |
| Tasks endpoint | `/tasks` | 3 tasks listed |
| Full episode | `/reset` → `/step` | reward in [0, 1] |
| OpenEnv validate | `openenv validate` | `[OK]` |
| Inference script | `python inference.py` | `[START]/[STEP]/[END]` logs |
| Docker build | `docker build ...` | Build succeeds |
