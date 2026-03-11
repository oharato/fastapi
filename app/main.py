from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from taskiq_fastapi import init
from app.broker import broker
from app.database import create_db_and_tables
from app.routers import todo, job, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="FastAPI App", version="0.1.0", lifespan=lifespan)

init(broker, app)

app.include_router(auth.router)
app.include_router(todo.router)
app.include_router(job.router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}
