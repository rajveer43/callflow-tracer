#!/usr/bin/env python3

import os
import sys
import time

# Add the parent directory to the path
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

print("Step 1: Starting simple debug")

# Test basic import
try:
    from callflow_tracer import trace, trace_scope, get_current_graph
    print("Step 2: Import successful")
except Exception as e:
    print(f"Step 2: Import failed: {e}")
    sys.exit(1)

# Test simple function without decorator first
def simple_func():
    print("Step 4: Inside simple_func")
    time.sleep(0.01)
    return "result"

print("Step 3: About to test trace_scope")

# Test trace_scope
try:
    with trace_scope() as graph:
        print("Step 5: Inside trace_scope")
        result = simple_func()
        print(f"Step 6: simple_func returned: {result}")
        
        # Check if graph has any data
        print(f"Step 7: Graph has {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        
    print("Step 8: Exited trace_scope successfully")
    
except Exception as e:
    print(f"ERROR in trace_scope: {e}")
    import traceback
    traceback.print_exc()

print("Step 9: Test completed")
