from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.app.routes import router
from backend.app import state

@asynccontextmanager
async def lifespan(app: FastAPI):
    state.load_state()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)