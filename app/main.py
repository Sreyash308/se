"""
Main FastAPI Application Entrypoint for PlantCare AI.
Provides API Gateway routing, CORS security middleware, OpenAPI schema,
and mounts the Web UI client dashboard.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os

from app.config import settings
from app.api.endpoints import router as api_router

app = FastAPI(
    title="PlantCare AI: Precision Disease Diagnosis & Hyperlocal Medicine Availability",
    description=(
        "Enterprise-grade agricultural intelligence and supply-chain routing platform. "
        "Bridges the last-mile disconnect by coupling edge computer vision pathology classification "
        "with regulatory-compliant (CIBRC) prescriptions and real-time hyperlocal agro-dealer inventory reservation."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# Cross-Origin Resource Sharing (CORS) Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Include API Routers
# ---------------------------------------------------------------------------
app.include_router(api_router)

# ---------------------------------------------------------------------------
# Static Files & Web Dashboard Mounting
# ---------------------------------------------------------------------------
static_path = settings.STATIC_DIR
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        """Serves the interactive web client portal."""
        index_file = static_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return JSONResponse({"message": "PlantCare AI API is running. Visit /docs for OpenAPI documentation."})


# ---------------------------------------------------------------------------
# Global Exception Sanitization
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Prevents unhandled 500 exceptions from leaking internal stack traces."""
    if settings.DEBUG:
        detail = str(exc)
    else:
        detail = "An internal processing error occurred. Please verify your request payload."
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "detail": detail},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
