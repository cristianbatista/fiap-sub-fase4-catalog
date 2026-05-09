from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from infrastructure.database.mongodb import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Catalog Service",
    description="Serviço de catálogo de veículos para revenda",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


from presentation.routers import health, vehicle_status, vehicles  # noqa: E402

app.include_router(health.router)
app.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
app.include_router(vehicle_status.router, prefix="/vehicles", tags=["vehicle-status"])
