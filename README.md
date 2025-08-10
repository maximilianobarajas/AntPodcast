# AntPodcaster

**Ant Podcaster** is a minimal, fast writing assistant that helps you outline on the left pane and compose on the right—then turns your draft into a short **podcast** via streamed TTS (no file writes, no dev-server reloads).  
Backend: **FastAPI** (OpenAI for text + speech). Frontend: **HTML/CSS/JS** (optional **p5.js** background). Default layout is a **50/50 resizable split** with careful sizing so content never overlaps.


## Table of contents
- [Project description](#project-description)
- [Repository structure](#repository-structure)
- [Setup instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Backend (FastAPI)](#backend-fastapi)
  - [Frontend (VS Code Live Server)](#frontend-vs-code-live-server)
  - [p5.js integration (optional)](#p5js-integration-optional)
- [Environment & dependencies](#environment--dependencies)
  - [Environment variables](#environment-variables)
  - [requirements.txt](#requirementstxt)
- [API quick reference](#api-quick-reference)
- [Troubleshooting](#troubleshooting)

---

## Project description

- **Backend (FastAPI)**
  - Endpoints:
    - `POST /generate_intro` — model-written introductions.
    - `POST /generate_subtopics?main_topic=&num_topics=` — structured subtopic suggestions.
    - `POST /generate_subtopic_paragraph` — per-subtopic expansions.
    - `POST /podcast/build-openai` — **streams** `audio/mpeg` (TTS) to the browser; frontend plays a **blob URL**.
  - OpenAI (Python SDK) for **text generation** and **text-to-speech**.
  - **CORS** configured for local dev to allow JSON POSTs from the frontend.

- **Frontend (Vanilla JS + optional p5.js)**
  - Left pane: subtopics (drag/drop, duplicate, per-subtopic AI paragraph).
  - Right pane: composer + toolbar + **audio player**.
  - **Stable audio swap**: `pause()` → `removeAttribute('src'); load()` → set `src = URL.createObjectURL(blob)` → wait `canplay` → `play()`.
  - Served via **VS Code → “Open with Live Server”** from `WEBSITE/WEBSITE/index.html`.

---

## Repository structure
```bash
.
├─ app/
│  ├─ routers/
│  │  ├─ generation.py
│  │  └─ podcast\_openai.py
│  └─ services/
│     ├─ text\_generation.py
│     ├─ audio\_openai.py
│     └─ ai\_client.py
├─ main.py
├─ requirements.txt
├─ .env.example
├─ WEBSITE/
│  └─ WEBSITE/
│     ├─ index.html
│     ├─ style.css
│     ├─ app.js
│     └─ sketch.js         # optional p5.js background
└─ README.md
````


---

## Setup instructions

### Prerequisites

- **Python 3.11+** — https://www.python.org/downloads/  
- **Visual Studio Code** — https://code.visualstudio.com/  
- **Live Server (VS Code extension)** — https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer  
- **p5.js** (optional) — Getting started: https://p5js.org/get-started/ • Learn: https://p5js.org/learn/  
- **OpenAI API key** — https://platform.openai.com/

---

### Backend (FastAPI)

1) **Clone & enter repo**
```bash
git clone <your-repo-url>
cd <your-repo>
````

2. **Create virtual environment & install deps**

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3. **Configure environment**

Copy example and fill in:

```bash
cp .env.example .env
```

Minimal `.env`:

```dotenv
OPENAI_API_KEY=sk-...
OPENAI_API_BASE=
OPENAI_MODEL=gpt-4o-mini
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE=onyx
ALLOWED_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```

4. **Run the API**

```bash
uvicorn app.main:app --reload
```

5. **CORS (main.py)** — ensure something like:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.generation import router as generation_router
from app.routers.podcast_openai import router as podcast_openai_router

app = FastAPI(title="Ant Podcaster API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500","http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, Ants!"}

app.include_router(generation_router)
app.include_router(podcast_openai_router)
```

---

### Frontend (VS Code Live Server)

1. Open **VS Code** at the repo root.
2. In the Explorer, open `WEBSITE/WEBSITE/index.html`.
3. **Right-click → “Open with Live Server”.**
4. The site opens at something like:
   `http://127.0.0.1:5500/WEBSITE/WEBSITE/`

> If your API is not `http://127.0.0.1:8000`, edit `API.BASE` at the top of `WEBSITE/WEBSITE/app.js`.

---

### p5.js integration (optional)

Add p5.js via CDN in `WEBSITE/WEBSITE/index.html` (before `sketch.js`):

```html
<script src="https://cdn.jsdelivr.net/npm/p5@1.9.0/lib/p5.min.js"></script>
<script src="./sketch.js"></script>
```

* p5 “Get Started”: [https://p5js.org/get-started/](https://p5js.org/get-started/)
* p5 “Learn”: [https://p5js.org/learn/](https://p5js.org/learn/)

---

## Environment & dependencies

### Environment variables

| Variable           | Required | Default                                       | Description                                        |
| ------------------ | -------- | --------------------------------------------- | -------------------------------------------------- |
| `OPENAI_API_KEY`   | ✅        | —                                             | OpenAI API key                                     |
| `OPENAI_API_BASE`  | ❌        | OpenAI default                                | Custom API base if using a proxy                   |
| `OPENAI_MODEL`     | ✅        | `gpt-4o-mini`                                 | Chat/completions model                             |
| `OPENAI_TTS_MODEL` | ✅        | `gpt-4o-mini-tts`                             | TTS model                                          |
| `OPENAI_TTS_VOICE` | ❌        | `onyx`                                        | TTS voice (e.g., `alloy`, `echo`, `fable`, `onyx`) |
| `ALLOWED_ORIGINS`  | ✅        | `http://127.0.0.1:5500,http://localhost:5500` | CORS origins for local dev                         |
| `PODCAST_OUT_DIR`  | ❌        | `media/podcasts`                              | Only used if you switch to file-based audio        |

### requirements.txt

```txt
fastapi>=0.115
uvicorn[standard]>=0.30
pydantic>=2.8
python-dotenv>=1.0
httpx>=0.27
openai>=1.40
```

---

## API quick reference

* **POST `/generate_intro`**
  **Body**

  ```json
  { "main_topic": "Your topic", "word_count": 120 }
  ```

  **Returns**

  ```json
  { "introduction": "..." }
  ```

* **POST** `/generate_subtopics?main_topic=Topic&num_topics=6`
  **Returns**

  ```json
  { "subtopics": ["…","…", "..."] }
  ```

* **POST `/generate_subtopic_paragraph`**
  **Body**

  ```json
  { "text": "optional context", "subtopic": "Title", "word_count": 180 }
  ```

  **Returns**

  ```json
  { "paragraph": "..." }
  ```

* **POST `/podcast/build-openai`** (TTS streamed as `audio/mpeg`)
  **Body**

  ```json
  {
    "source_text": "Full draft text",
    "title": "Episode title",
    "target_minutes": 8,
    "segments": 4,
    "tone": "friendly and informative",
    "voice": "onyx"
  }
  ```

  **Response**: raw `audio/mpeg` stream (frontend converts to a **blob URL** and plays).

---
