"""
Main FastAPI application with Supabase authentication integration.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.auth import init_auth_service
from app.config import get_settings
from app.dependency import Templates
from app.routers import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Initializes services on startup and cleans up on shutdown.
    """
    # Startup: Initialize auth service
    settings = get_settings()
    init_auth_service(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_anon_key
    )
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Educational Platform API",
    description="API with passwordless authentication via Supabase",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router)

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static"
)


# Home route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, templates: Templates):
    """Home page with links to demos"""
    return templates.TemplateResponse(
        "home.html",
        {"request": request}
    )


# Test route
@app.get("/test/viz", response_class=HTMLResponse)
async def test_viz(request: Request, templates: Templates):
    """Simple test page for visualization"""
    return templates.TemplateResponse(
        "test_viz.html",
        {"request": request}
    )


# Demo routes
@app.get("/demo/kadane", response_class=HTMLResponse)
async def demo_kadane(request: Request, templates: Templates):
    """Demo content viewer with Kadane's algorithm - FULLY RESPONSIVE"""
    content_data = {
        "title": "Kadane's Algorithm",
        "description": "Maximum subarray sum in linear time"
    }
    return templates.TemplateResponse(
        "content_viewer_responsive.html",
        {"request": request, "content": content_data}
    )


@app.get("/demo/mlp", response_class=HTMLResponse)
async def demo_mlp(request: Request, templates: Templates):
    """Deep Learning Viewer - MLP Forward Propagation with PDF + Interactive Visualization"""
    content_data = {
        "title": "Multi-Layer Perceptron: Forward Propagation",
        "description": "Understand how neural networks process information through layers",
        "learning_objectives": [
            "Understand the structure of a Multi-Layer Perceptron",
            "See how data flows through neural network layers",
            "Learn how activation functions transform neuron outputs",
            "Visualize the forward propagation algorithm step-by-step"
        ]
    }

    # Configuration for visualizations
    visualizations = {
        "mlp_forward": {
            "type": "mlp_forward",
            "config": {
                "layers": [3, 4, 2],
                "activation": "relu",
                "inputData": [0.5, 0.8, 0.3],
                "speed": 1000
            }
        }
    }

    # Map PDF pages to visualizations
    page_mappings = {
        "1": "mlp_forward",
        "2": "mlp_forward",
        "3": "mlp_forward"
    }

    # For MVP, we'll use a placeholder PDF or sample
    # You can replace this with your actual PDF URL
    pdf_url = "https://arxiv.org/pdf/1603.04467.pdf"  # Sample ML paper as placeholder

    return templates.TemplateResponse(
        "deep_learning_viewer.html",
        {
            "request": request,
            "content": content_data,
            "visualizations": visualizations,
            "page_mappings": page_mappings,
            "pdf_url": pdf_url
        }
    )
