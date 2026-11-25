# TruthLens

TruthLens is an evidence-oriented statement and conversation analysis workspace. It helps users examine claims, compare accounts, reconstruct timelines, and organize submitted evidence. It does not claim to detect lies, infer intent from nervousness, or produce a probability that somebody is deceptive.

## What is implemented

- FastAPI backend with SQLite by default and SQLAlchemy persistence.
- Registration, login, PBKDF2 password hashing, signed JWT access tokens, and ownership checks.
- Private history listing, detail retrieval, and deletion.
- Statement analysis with claim extraction, language observations, semantic qualifiers, explicit-reference comparison, alternative explanations, and neutral questions.
- Conversation parsing with speaker and optional timestamp preservation.
- Story comparison across multiple versions.
- Timeline event extraction with temporal references.
- Evidence upload validation for TXT, PDF, PNG, and JPEG. TXT extraction is implemented; PDF and image uploads are retained as metadata-only in this build.
- Audio/video upload inspection with an explicit metadata-only response. No facial, vocal, pause, or behavioural inference is fabricated.
- Configurable AI provider seam. Without credentials the API reports deterministic demo mode.
- React + Vite responsive workspace with auth, analysis mode navigation, results, timeline rendering, upload flow, and history deletion.
- Docker and Render backend configuration plus Vercel SPA rewrite configuration.

## Architecture

```text
frontend/src/main.jsx       React workspace and API client
frontend/src/styles.css     Responsive dark SaaS interface
backend/app/main.py        API routes and ownership boundaries
backend/app/security.py     Password hashing and JWT signing
backend/app/models.py       User and analysis persistence
backend/app/analyzer/       Independent analysis modules
backend/app/ai_service.py   Provider status and integration seam
```

## Run locally on Windows PowerShell

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\backend\requirements.txt
Copy-Item .env.example .env
$env:PYTHONPATH = "backend"
uvicorn app.main:app --app-dir backend --reload --port 8000
```

In a second PowerShell window:

```powershell
cd frontend
npm install
$env:VITE_API_URL = "http://127.0.0.1:8000"
npm run dev
```

Open `http://localhost:5173`. API documentation is available at `http://127.0.0.1:8000/docs`.

## Tests and build

```powershell
$env:PYTHONPATH = "backend"
.\.venv\Scripts\python.exe -m pytest backend\tests
cd frontend
npm run build
```

## Environment

Copy [.env.example](./.env.example) to `.env`. Set a long random `JWT_SECRET` before deployment. `AI_PROVIDER=none` is safe demo mode. A provider adapter can be added behind `backend/app/ai_service.py`; keys must remain backend-only.

For production, use PostgreSQL by setting `DATABASE_URL`, restrict `FRONTEND_URL` to the deployed frontend origin, put the API behind HTTPS, and use object storage with retention controls for uploaded documents.

## Deployment

1. Create a Git repository and commit the source after checking `.env` is ignored.
2. Deploy `frontend/` to Vercel with `VITE_API_URL` pointing to the backend URL.
3. Deploy the `backend/` service to Render using [render.yaml](./render.yaml), or build [backend/Dockerfile](./backend/Dockerfile) on another container host.
4. Configure `JWT_SECRET`, `DATABASE_URL`, and `FRONTEND_URL` in the backend host.
5. Run the test suite and frontend build before publishing.

## Limitations and responsible use

Current analysis is deterministic and intentionally conservative. Provider-backed semantic models, OCR, PDF parsing, transcription, vector retrieval, and reviewed computer-vision/audio research can be added, but their outputs must remain labelled as observations or interpretations. Uploaded documents are not automatically authentic, and changes in a story may reflect memory, clarification, or different event scope rather than deception.
