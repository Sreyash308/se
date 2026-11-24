"""
Main FastAPI Application Entrypoint for PlantCare AI.
Provides API Gateway routing, CORS security middleware, OpenAPI schema,
and mounts the Web UI client dashboard.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
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
    docs_url=None,  # Custom styled Swagger UI mounted below
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# Custom Styled OpenAPI Swagger UI (Clean, Polished Dark Theme - No Flashing)
# ---------------------------------------------------------------------------
SWAGGER_DARK_CSS = """
body {
    background-color: #0b0f19 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}
.swagger-ui {
    color: #cbd5e1 !important;
}
/* Completely disable unwanted flashing focus/active outlines and borders */
.swagger-ui *:focus,
.swagger-ui *:active,
.swagger-ui button:focus,
.swagger-ui a:focus,
.swagger-ui div:focus,
.swagger-ui input:focus,
.swagger-ui .opblock:focus,
.swagger-ui .opblock:active,
.swagger-ui .opblock-summary:focus,
.swagger-ui .opblock-summary:active,
.swagger-ui .opblock-summary-control:focus,
.swagger-ui .opblock-summary-control:active {
    outline: none !important;
    box-shadow: none !important;
    -webkit-tap-highlight-color: transparent !important;
}
.swagger-ui .topbar {
    background-color: #030712 !important;
    border-bottom: 1px solid #1e293b !important;
}
.swagger-ui .topbar .download-url-wrapper .select-label select {
    border: 1px solid #334155 !important;
    background: #0f172a !important;
    color: #f1f5f9 !important;
}
.swagger-ui .info {
    margin: 30px 0 !important;
}
.swagger-ui .info .title {
    color: #10b981 !important;
    font-weight: 800 !important;
}
.swagger-ui .info p, .swagger-ui .info li, .swagger-ui .info table {
    color: #94a3b8 !important;
}
.swagger-ui a.nostyle {
    color: #f1f5f9 !important;
}
.swagger-ui .scheme-container {
    background-color: #0f172a !important;
    box-shadow: none !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
    padding: 15px 20px !important;
    margin-bottom: 20px !important;
}
.swagger-ui select {
    background: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}
.swagger-ui .opblock {
    border-radius: 10px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3) !important;
    border: 1px solid #1e293b !important;
    background: #0f172a !important;
    margin: 0 0 16px !important;
    transition: border-color 0.15s ease, background-color 0.15s ease;
}
.swagger-ui .opblock .opblock-summary {
    border-bottom: 1px solid transparent !important;
    padding: 10px 16px !important;
}
.swagger-ui .opblock.opblock-post {
    border-color: rgba(16, 185, 129, 0.35) !important;
    background: rgba(16, 185, 129, 0.05) !important;
}
.swagger-ui .opblock.opblock-post .opblock-summary-method {
    background: #10b981 !important;
    color: #022c22 !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
}
.swagger-ui .opblock.opblock-get {
    border-color: rgba(56, 189, 248, 0.35) !important;
    background: rgba(56, 189, 248, 0.05) !important;
}
.swagger-ui .opblock.opblock-get .opblock-summary-method {
    background: #0284c7 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
}
.swagger-ui .opblock .opblock-summary-path,
.swagger-ui .opblock .opblock-summary-operation-id,
.swagger-ui .opblock .opblock-summary-path__deprecated {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
}
.swagger-ui .opblock .opblock-summary-description {
    color: #94a3b8 !important;
}
.swagger-ui .opblock-body {
    background: #0b1120 !important;
    color: #e2e8f0 !important;
}
.swagger-ui .opblock-body pre {
    background: #030712 !important;
    color: #38bdf8 !important;
    border: 1px solid #1e293b !important;
    border-radius: 8px !important;
}
.swagger-ui table thead tr td, .swagger-ui table thead tr th {
    color: #94a3b8 !important;
    border-bottom: 1px solid #1e293b !important;
}
.swagger-ui .parameters-col_name {
    color: #f1f5f9 !important;
}
.swagger-ui .parameter__name {
    color: #38bdf8 !important;
    font-weight: 600 !important;
}
.swagger-ui .parameter__type {
    color: #94a3b8 !important;
}
.swagger-ui input[type=text], .swagger-ui textarea {
    background: #0f172a !important;
    color: #f1f5f9 !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}
.swagger-ui input[type=text]:focus, .swagger-ui textarea:focus {
    border-color: #10b981 !important;
}
.swagger-ui .btn {
    border-radius: 6px !important;
    font-weight: 600 !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
    background: #1e293b !important;
}
.swagger-ui .btn.execute {
    background-color: #10b981 !important;
    color: #064e3b !important;
    border-color: #10b981 !important;
}
.swagger-ui .btn.execute:hover {
    background-color: #059669 !important;
}
.swagger-ui .btn.cancel {
    background-color: #dc2626 !important;
    color: #fff !important;
    border-color: #dc2626 !important;
}
.swagger-ui .response-col_status {
    color: #10b981 !important;
}
.swagger-ui .response-col_links {
    color: #94a3b8 !important;
}
.swagger-ui section.models {
    border: 1px solid #1e293b !important;
    border-radius: 10px !important;
    background: #0f172a !important;
}
.swagger-ui section.models h4 {
    color: #cbd5e1 !important;
}
.swagger-ui .model-box {
    background: #0b1120 !important;
}
.swagger-ui .model {
    color: #cbd5e1 !important;
}
.swagger-ui .model-title {
    color: #10b981 !important;
}
.swagger-ui .prop-type {
    color: #38bdf8 !important;
}
"""

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Renders customized, modern dark-themed Swagger UI with clean focus styling."""
    swagger_html = get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="PlantCare AI - Interactive OpenAPI Docs",
        swagger_favicon_url="/static/favicon-32.png",
    )
    # Inject custom dark theme CSS and remove ugly focus outlines
    custom_content = swagger_html.body.decode("utf-8").replace(
        "</head>",
        f"<style>{SWAGGER_DARK_CSS}</style></head>"
    )
    return HTMLResponse(content=custom_content)

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
