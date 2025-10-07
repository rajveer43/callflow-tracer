"""
FastAPI integration example for callflow-tracer.

Run:
    uvicorn examples.fastapi_example:app --reload

Then open http://127.0.0.1:8000/ and http://127.0.0.1:8000/items/42
"""

from fastapi import FastAPI

from callflow_tracer import trace_scope
from callflow_tracer.integrations.fastapi_integration import setup_fastapi_tracing


app = FastAPI()


# Wrap the app startup under a trace_scope so requests are captured into a graph
@app.on_event("startup")
async def _startup_trace_scope():
    # Create a single global scope for the app lifetime; the HTML will be
    # written when the process exits. For demo purposes we start it at startup.
    # In production, you may want to manage scopes per-request or periodically.
    global _cft_scope
    _cft_scope = trace_scope("fastapi_trace.html")
    _cft_scope.__enter__()


@app.on_event("shutdown")
async def _shutdown_trace_scope():
    global _cft_scope
    try:
        _cft_scope.__exit__(None, None, None)
    except Exception:
        pass


# Install middleware to record request -> endpoint relationships
setup_fastapi_tracing(app)


@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI + callflow-tracer"}


@app.get("/items/{item_id:int}")
async def read_item(item_id: int):
    return {"item_id": item_id, "detail": "Item details"}


