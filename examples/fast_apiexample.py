"""
FastAPI integration example for callflow-tracer.

Run:
    uvicorn examples.fastapi_example:app --reload

Then try:
    - http://127.0.0.1:8000/
    - http://127.0.0.1:8000/items/42
    - http://127.0.0.1:8000/items/42/price
    - http://127.0.0.1:8000/search?q=test
    - http://127.0.0.1:8000/calculate/10/plus/5
"""
import os
import sys
import logging
import random
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

# Ensure local package is imported when running from the examples directory
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from callflow_tracer import trace_scope
from callflow_tracer.integrations.fastapi_integration import setup_fastapi_tracing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example database (in-memory for demo)
fake_items_db: Dict[int, Dict] = {
    1: {"name": "Widget", "price": 9.99, "in_stock": True},
    2: {"name": "Gadget", "price": 19.99, "in_stock": True},
    3: {"name": "Doodad", "price": 4.99, "in_stock": False},
}

# Pydantic models
class Item(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., gt=0, description="Price must be greater than zero")
    in_stock: bool = True
    tags: List[str] = []
    image_url: Optional[HttpUrl] = None

class ItemResponse(Item):
    id: int
    created_at: datetime

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    global _cft_scope
    _cft_scope = trace_scope("fastapi_trace.html")
    _cft_scope.__enter__()
    
    # Add some sample data
    for item_id, item_data in fake_items_db.items():
        item_data["created_at"] = datetime.utcnow()
    
    yield  # This is where the application runs
    
    # Shutdown
    logger.info("Shutting down...")
    try:
        _cft_scope.__exit__(None, None, None)
    except Exception as e:
        logger.error(f"Error during trace scope cleanup: {e}")

app = FastAPI(
    title="Callflow-Tracer FastAPI Example",
    description="Enhanced FastAPI example with callflow-tracer integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup callflow-tracing
setup_fastapi_tracing(app)

# Middleware for request/response logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code} for {request.method} {request.url}")
        return response
    except Exception as e:
        logger.error(f"Error processing {request.url}: {str(e)}")
        raise

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "Welcome to the FastAPI + callflow-tracer example",
        "endpoints": [
            "/docs - API documentation",
            "/items - List all items",
            "/items/{id} - Get item by ID",
            "/search?q=term - Search items",
            "/calculate/{a}/{operation}/{b} - Simple calculator"
        ]
    }

# Get all items
@app.get("/items", response_model=Dict[int, ItemResponse])
async def list_items():
    return fake_items_db

# Get item by ID
@app.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    responses={
        404: {"description": "Item not found"},
        200: {"description": "Item found", "model": ItemResponse}
    }
)
async def get_item(item_id: int):
    if item_id not in fake_items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return {"id": item_id, **fake_items_db[item_id]}

# Search items
@app.get("/search")
async def search_items(q: str, limit: int = 10):
    results = [
        {"id": item_id, **item}
        for item_id, item in fake_items_db.items()
        if q.lower() in item["name"].lower()
    ][:limit]
    return {"query": q, "results": results}

# Simple calculator
@app.get("/calculate/{a:float}/{operation}/{b:float}")
async def calculate(a: float, operation: str, b: float):
    operations = {
        "plus": a + b,
        "minus": a - b,
        "times": a * b,
        "divided_by": a / b if b != 0 else None,
    }
    
    if operation not in operations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid operation. Use one of: {', '.join(operations.keys())}"
        )
    
    if operation == "divided_by" and b == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot divide by zero"
        )
    
    return {
        "a": a,
        "b": b,
        "operation": operation,
        "result": operations[operation]
    }

# Create new item
@app.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_item(item: Item):
    new_id = max(fake_items_db.keys(), default=0) + 1
    new_item = {
        **item.dict(),
        "id": new_id,
        "created_at": datetime.utcnow()
    }
    fake_items_db[new_id] = new_item
    return new_item
