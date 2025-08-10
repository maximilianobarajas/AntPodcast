from fastapi import FastAPI
from app.routers.generation import router as generation_router
from app.routers.podcast_openai import router as podcast_openai_router
from fastapi.middleware.cors import CORSMiddleware
from app.routers.generation_ai_extras import router as ai_extras_router

app = FastAPI(title="Writing Assistant API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",   # VS Code Live Server
        "http://localhost:5500",
        "http://localhost:5173",   # Vite
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # "*" is okay for quick local dev if you don't use cookies:
        # "*",
    ],
    allow_credentials=False,       # set True only if you send cookies/auth
    allow_methods=["GET","POST","OPTIONS"],  # or ["*"]
    allow_headers=["*"],           # allow Content-Type, Authorization, etc.
)
app.include_router(ai_extras_router)
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

app.include_router(generation_router)
app.include_router(podcast_openai_router)
