# Framework Integrations Guide

Complete documentation for framework integrations.

**Location**: `callflow_tracer/integrations/` (5 integration modules)

---

## Overview

The Integrations module provides automatic tracing and profiling for popular Python frameworks without modifying application code.

## Available Integrations

### 1. Flask Integration (`flask_integration.py`)

Automatic tracing for Flask web applications.

**Features**:
- Trace all request handlers
- Track request/response times
- Capture request context
- Automatic call graph generation
- Performance metrics per endpoint

**Setup**:
```python
from flask import Flask
from callflow_tracer.integrations.flask_integration import setup_flask_tracing

app = Flask(__name__)
setup_flask_tracing(app)

@app.route('/api/data')
def get_data():
    return {'data': 'value'}

if __name__ == '__main__':
    app.run()
```

**Output**:
- Traces saved to `traces/` directory
- One HTML file per request
- Automatic browser opening (optional)

**Configuration**:
```python
setup_flask_tracing(
    app,
    output_dir="traces",
    auto_open=True,
    include_args=False
)
```

### 2. FastAPI Integration (`fastapi_integration.py`)

Automatic tracing for FastAPI applications.

**Features**:
- Trace all endpoints
- Async/await support
- Request context tracking
- Performance monitoring
- Dependency injection tracing

**Setup**:
```python
from fastapi import FastAPI
from callflow_tracer.integrations.fastapi_integration import setup_fastapi_tracing

app = FastAPI()
setup_fastapi_tracing(app)

@app.get("/api/data")
async def get_data():
    return {"data": "value"}

# Run with: uvicorn app:app --reload
```

**Output**:
- Traces saved to `traces/` directory
- One HTML file per request
- Async call graph support

**Configuration**:
```python
setup_fastapi_tracing(
    app,
    output_dir="traces",
    auto_open=True,
    include_args=False
)
```

### 3. Django Integration (`django_integration.py`)

Automatic tracing for Django applications.

**Features**:
- Trace view functions
- Middleware integration
- Request/response tracking
- Database query monitoring
- Template rendering tracking

**Setup**:
```python
# In settings.py
MIDDLEWARE = [
    'callflow_tracer.integrations.django_integration.CallflowTracingMiddleware',
    # ... other middleware
]

CALLFLOW_TRACING = {
    'output_dir': 'traces',
    'auto_open': True,
    'include_args': False
}

# Views are automatically traced
def my_view(request):
    return HttpResponse("Hello")
```

**Output**:
- Traces saved to `traces/` directory
- One HTML file per request
- Database query tracking

**Configuration**:
```python
CALLFLOW_TRACING = {
    'output_dir': 'traces',
    'auto_open': True,
    'include_args': False,
    'trace_db': True,
    'trace_templates': True
}
```

### 4. SQLAlchemy Integration (`sqlalchemy_integration.py`)

Automatic tracing for SQLAlchemy ORM operations.

**Features**:
- Trace database queries
- Track query performance
- Monitor connection pooling
- Identify slow queries
- Query parameter logging

**Setup**:
```python
from sqlalchemy import create_engine
from callflow_tracer.integrations.sqlalchemy_integration import setup_sqlalchemy_tracing

engine = create_engine('postgresql://user:pass@localhost/db')
setup_sqlalchemy_tracing(engine)

# All queries are automatically traced
session = Session(engine)
users = session.query(User).all()
```

**Output**:
- Query execution times
- Query parameters
- Connection pool statistics
- Slow query identification

**Configuration**:
```python
setup_sqlalchemy_tracing(
    engine,
    log_queries=True,
    slow_query_threshold=1.0,  # seconds
    include_params=True
)
```

### 5. psycopg2 Integration (`psycopg2_integration.py`)

Automatic tracing for psycopg2 database operations.

**Features**:
- Trace SQL queries
- Track execution time
- Monitor connections
- Capture query parameters
- Connection pooling support

**Setup**:
```python
import psycopg2
from callflow_tracer.integrations.psycopg2_integration import setup_psycopg2_tracing

setup_psycopg2_tracing()

conn = psycopg2.connect("dbname=test user=postgres")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")  # Automatically traced
```

**Output**:
- Query execution times
- Query parameters
- Connection statistics
- Error tracking

**Configuration**:
```python
setup_psycopg2_tracing(
    log_queries=True,
    slow_query_threshold=1.0,  # seconds
    include_params=True
)
```

## Integration Architecture

Each integration follows this pattern:

1. **Setup Function**: Initialize tracing for the framework
2. **Decorator/Middleware**: Intercept framework calls
3. **Context Manager**: Manage trace scope
4. **Automatic Export**: Generate visualizations

## Usage Examples

### Example 1: Flask with Tracing
```python
from flask import Flask
from callflow_tracer.integrations.flask_integration import setup_flask_tracing

app = Flask(__name__)
setup_flask_tracing(app, output_dir="api_traces")

@app.route('/process')
def process():
    result = expensive_operation()
    return {'result': result}

@app.route('/data')
def get_data():
    data = fetch_from_db()
    return {'data': data}

if __name__ == '__main__':
    app.run(debug=True)
    # Traces saved to api_traces/ directory
```

### Example 2: FastAPI with Async
```python
from fastapi import FastAPI
from callflow_tracer.integrations.fastapi_integration import setup_fastapi_tracing

app = FastAPI()
setup_fastapi_tracing(app, output_dir="api_traces")

@app.get("/process")
async def process():
    result = await expensive_operation()
    return {'result': result}

@app.get("/data")
async def get_data():
    data = await fetch_from_db()
    return {'data': data}

# Run: uvicorn app:app --reload
# Traces saved to api_traces/ directory
```

### Example 3: Django with Middleware
```python
# settings.py
MIDDLEWARE = [
    'callflow_tracer.integrations.django_integration.CallflowTracingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # ... other middleware
]

CALLFLOW_TRACING = {
    'output_dir': 'traces',
    'auto_open': False,
    'trace_db': True
}

# views.py
from django.http import JsonResponse

def process_data(request):
    # Automatically traced
    result = expensive_operation()
    return JsonResponse({'result': result})

def get_data(request):
    # Automatically traced
    data = fetch_from_db()
    return JsonResponse({'data': data})
```

### Example 4: SQLAlchemy Integration
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import Session
from callflow_tracer.integrations.sqlalchemy_integration import setup_sqlalchemy_tracing

# Setup
engine = create_engine('postgresql://user:pass@localhost/db')
setup_sqlalchemy_tracing(engine, slow_query_threshold=0.5)

# Usage - all queries automatically traced
session = Session(engine)
users = session.query(User).filter(User.active == True).all()
session.close()
```

### Example 5: psycopg2 Integration
```python
import psycopg2
from callflow_tracer.integrations.psycopg2_integration import setup_psycopg2_tracing

# Setup
setup_psycopg2_tracing(log_queries=True, slow_query_threshold=1.0)

# Usage - all queries automatically traced
conn = psycopg2.connect("dbname=mydb user=postgres password=secret")
cursor = conn.cursor()

cursor.execute("SELECT * FROM users WHERE id = %s", (123,))
result = cursor.fetchall()

cursor.close()
conn.close()
```

## Best Practices

### 1. Development vs Production
```python
import os
from callflow_tracer.integrations.flask_integration import setup_flask_tracing

app = Flask(__name__)

if os.getenv('ENVIRONMENT') == 'development':
    setup_flask_tracing(app, auto_open=True)
else:
    setup_flask_tracing(app, auto_open=False)
```

### 2. Output Directory Management
```python
import os
from datetime import datetime

output_dir = f"traces/{datetime.now().strftime('%Y%m%d')}"
os.makedirs(output_dir, exist_ok=True)

setup_flask_tracing(app, output_dir=output_dir)
```

### 3. Selective Tracing
```python
# Trace only specific routes
@app.route('/expensive')
def expensive_operation():
    # This will be traced
    pass

@app.route('/simple')
def simple_operation():
    # This won't be traced (if configured)
    pass
```

### 4. Performance Monitoring
```python
# Combine with predictive analysis
from callflow_tracer.predictive_analysis import PerformancePredictor

setup_flask_tracing(app)
predictor = PerformancePredictor("trace_history.json")

# Periodically check predictions
predictions = predictor.predict_performance_issues(current_trace)
```

## Troubleshooting

### Traces Not Generated
- Check output directory exists and is writable
- Verify integration setup is called before routes
- Check for exceptions in application logs

### Performance Impact
- Use `auto_open=False` in production
- Consider sampling for high-traffic endpoints
- Monitor trace file sizes

### Database Query Issues
- Ensure database driver is installed
- Check database connection settings
- Verify query parameters are logged correctly

## Configuration Reference

### Common Options
- `output_dir` - Directory for trace files
- `auto_open` - Automatically open browser
- `include_args` - Include function arguments
- `log_queries` - Log database queries
- `slow_query_threshold` - Threshold for slow queries (seconds)

### Environment Variables
- `CALLFLOW_OUTPUT_DIR` - Override output directory
- `CALLFLOW_AUTO_OPEN` - Override auto-open setting
- `CALLFLOW_TRACE_DB` - Enable database tracing
