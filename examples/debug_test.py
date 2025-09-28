"""
Simple debug test to isolate the flamegraph issue.
"""

import os
import sys

# Ensure local package is imported when running from the examples directory
CURRENT_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

print("Step 1: Starting debug test")
print("Step 2: About to import callflow_tracer")

try:
    from callflow_tracer import trace, trace_scope, get_current_graph
    print("Step 3: Successfully imported callflow_tracer")
except Exception as e:
    print(f"Step 3: ERROR importing callflow_tracer: {e}")
    sys.exit(1)

print("Step 4: About to define test function")

@trace
def simple_function():
    print("Inside simple_function")
    return "test result"

print("Step 5: Defined test function")
print("Step 6: About to start trace_scope")

try:
    with trace_scope("debug_test"):
        print("Step 7: Inside trace_scope")
        result = simple_function()
        print(f"Step 8: Function returned: {result}")
        
        graph = get_current_graph()
        print(f"Step 9: Got graph with {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        
    print("Step 10: Exited trace_scope successfully")
    
except Exception as e:
    print(f"ERROR in trace_scope: {e}")
    import traceback
    traceback.print_exc()

print("Step 11: Test completed")
