# Quick Test Reference

## 🚀 Run All Tests (Quick)

```bash
# Test cProfile fix
python tests/test_cprofile_fix.py

# Test Jupyter integration  
python tests/test_jupyter_integration.py

# Test flamegraph functionality
python tests/test_flamegraph.py

# Run demos (generates HTML files)
python examples/jupyter_standalone_demo.py
python examples/flamegraph_example.py
```

## ✅ What to Verify

### cProfile Fix ✓
- [ ] CPU Profile shows **non-zero** execution time
- [ ] Function calls count is **> 0**
- [ ] Hot spots count is **> 0**
- [ ] Detailed profile data is visible
- [ ] Health indicators show correct colors

### Jupyter Integration ✓
- [ ] Test script passes all 7 tests
- [ ] Demo generates 5 HTML files
- [ ] HTML files open and render correctly
- [ ] Interactive controls work (layouts, filters)
- [ ] CPU profile section expands/collapses

### Flamegraph ✓
- [ ] Test script passes all 10 tests
- [ ] Demo generates 7 flamegraph HTML files
- [ ] Flamegraphs render with D3.js
- [ ] Interactive zoom and tooltips work
- [ ] Performance hotspots are visible (wider bars)

## 🎯 One-Line Tests

```bash
# Verify cProfile fix works
python -c "from callflow_tracer import profile_section; import time; exec('with profile_section(\"test\") as s: time.sleep(0.01)\nprint(\"CPU data:\", len(s._get_cpu_stats().get(\"profile_data\", \"\")))')"

# Verify Jupyter integration works
python -c "from callflow_tracer import trace_scope; exec('with trace_scope() as g: sum(range(100))\nprint(\"Nodes:\", len(g.nodes), \"Edges:\", len(g.edges))')"

# Verify flamegraph works
python -c "from callflow_tracer import trace_scope; from callflow_tracer.flamegraph import generate_flamegraph; exec('with trace_scope() as g: sum(range(100))\ngenerate_flamegraph(g, \"test_flame.html\")\nprint(\"Flamegraph generated\")')"
```

## 📊 Expected Results

### test_cprofile_fix.py
```
✓ Found function call summary: XXX function calls in X.XXX seconds
✓ CPU Profile section present
✓ ALL TESTS PASSED!
```

### test_jupyter_integration.py
```
RESULTS: 7 passed, 0 failed
✓ ALL TESTS PASSED!
```

### jupyter_standalone_demo.py
```
✓ All demos completed successfully!
Generated HTML files:
  1. demo1_basic_tracing.html
  2. demo2_recursive_functions.html
  3. demo4_combined_analysis.html
  4. demo5_ml_pipeline.html
  5. demo6_nested_calls.html
```

### test_flamegraph.py
```
RESULTS: 10 passed, 0 failed
✓ ALL TESTS PASSED!
Generated test files:
  - test_flamegraph_basic.html
  - test_flamegraph_recursive.html
  - test_flamegraph_complex.html
  - And more...
```

### flamegraph_example.py
```
ALL EXAMPLES COMPLETED!
Generated flamegraph files:
  1. flamegraph_1_simple.html
  2. flamegraph_2_recursive.html
  3. flamegraph_3_nested.html
  4. flamegraph_4_parallel.html
  5. flamegraph_5_hotspots.html
  6. flamegraph_6_pipeline.html
  7. flamegraph_7_algorithms.html
```

## 🐛 Quick Debug

If tests fail:

```python
# Check profiling works
from callflow_tracer import profile_section
with profile_section("debug") as s:
    sum(range(1000))
print("Has CPU stats:", s.cpu_profile_stats is not None)
print("CPU data length:", len(s._get_cpu_stats().get('profile_data', '')))

# Check tracing works
from callflow_tracer import trace_scope
with trace_scope() as g:
    sum(range(100))
print("Nodes:", len(g.nodes), "Edges:", len(g.edges))

# Check flamegraph works
from callflow_tracer.flamegraph import generate_flamegraph
with trace_scope() as g:
    sum(range(100))
generate_flamegraph(g, "debug_flame.html")
print("Flamegraph created")
```

## 📝 Files Created

After running tests, you should have:

```
tests/
  ├── test_cprofile_output.html           # From cProfile test
  ├── test_jupyter_export.html            # From Jupyter test
  ├── test_flamegraph_basic.html          # From flamegraph test
  ├── test_flamegraph_recursive.html
  ├── test_flamegraph_complex.html
  └── test_flamegraph_*.html              # More flamegraph tests

examples/
  ├── demo1_basic_tracing.html            # From Jupyter demo
  ├── demo2_recursive_functions.html
  ├── demo4_combined_analysis.html
  ├── demo5_ml_pipeline.html
  ├── demo6_nested_calls.html
  ├── flamegraph_1_simple.html            # From flamegraph demo
  ├── flamegraph_2_recursive.html
  ├── flamegraph_3_nested.html
  ├── flamegraph_4_parallel.html
  ├── flamegraph_5_hotspots.html
  ├── flamegraph_6_pipeline.html
  └── flamegraph_7_algorithms.html
```

Open any `.html` file in your browser to verify visualizations work!

**Flamegraph files**: Show stacked bar charts (width = time, height = depth)
**Call graph files**: Show network diagrams with interactive controls
