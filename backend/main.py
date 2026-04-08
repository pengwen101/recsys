from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.app.routes import router
from fastapi.middleware.cors import CORSMiddleware
from backend.app import state

@asynccontextmanager
async def lifespan(app: FastAPI):
    state.load_state()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Must be explicit origins, no "*"
    allow_credentials=True,      # Required because Axios has withCredentials: true
    allow_methods=["*"],         # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],         # Allows all headers
)

app.include_router(router)