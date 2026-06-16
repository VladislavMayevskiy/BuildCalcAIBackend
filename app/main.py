from fastapi import FastAPI
from app.api.routes import (
    ai,
    auth,
    calculations,
    concrete,
    earthworks,
    estimates,
    facade,
    floors,
    foundation,
    mep,
    rebar,
    roofing,
    rooms,
    tiles,
    users,
    walls,
    work_catalog,
)
from app.api.routes.bars_calculation import index
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API is running"}


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculations.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(rooms.router)
app.include_router(ai.router)
app.include_router(foundation.router)
app.include_router(rebar.router)
app.include_router(earthworks.router)
app.include_router(concrete.router)
app.include_router(walls.router)
app.include_router(facade.router)
app.include_router(floors.router)
app.include_router(tiles.router)
app.include_router(roofing.router)
app.include_router(mep.router)
app.include_router(work_catalog.router)
app.include_router(estimates.router)
app.include_router(index.router)