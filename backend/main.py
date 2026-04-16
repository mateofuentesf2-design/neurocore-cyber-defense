from fastapi import FastAPI
from backend.routes import events
from backend.routes import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔥 CORS (OBLIGATORIO para frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(auth.router)