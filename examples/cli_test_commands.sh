#!/bin/bash
# Test script for callflow-tracer CLI commands
# This script demonstrates all CLI features

echo "=== CallFlow Tracer CLI Test Suite ==="
echo ""

# Create output directory
mkdir -p cli_test_output

echo "1. Testing basic trace command..."
callflow-tracer trace cli_demo.py -o cli_test_output/basic_trace.html
echo "   ✓ Basic trace complete"
echo ""

echo "2. Testing trace with JSON output..."
callflow-tracer trace cli_demo.py --format json -o cli_test_output/trace.json
echo "   ✓ JSON trace complete"
echo ""

echo "3. Testing trace with both formats..."
callflow-tracer trace cli_demo.py --format both -o cli_test_output/both_trace
echo "   ✓ Both formats complete"
echo ""

echo "4. Testing 3D visualization..."
callflow-tracer trace cli_demo.py --3d -o cli_test_output/trace_3d.html --no-browser
echo "   ✓ 3D visualization complete"
echo ""

echo "5. Testing flamegraph generation..."
callflow-tracer flamegraph cli_demo.py -o cli_test_output/flamegraph.html --no-browser
echo "   ✓ Flamegraph complete"
echo ""

echo "6. Testing flamegraph with min-time filter..."
callflow-tracer flamegraph cli_demo.py --min-time 5.0 -o cli_test_output/flamegraph_filtered.html --no-browser
echo "   ✓ Filtered flamegraph complete"
echo ""

echo "7. Testing profile command..."
callflow-tracer profile cli_demo.py -o cli_test_output/profile.html --no-browser
echo "   ✓ Profile complete"
echo ""

echo "8. Testing profile with memory..."
callflow-tracer profile cli_demo.py --memory -o cli_test_output/profile_memory.html --no-browser
echo "   ✓ Memory profile complete"
echo ""

echo "9. Testing profile as JSON..."
callflow-tracer profile cli_demo.py --format json -o cli_test_output/profile.json
echo "   ✓ JSON profile complete"
echo ""

echo "10. Testing profile as text..."
callflow-tracer profile cli_demo.py --format text -o cli_test_output/profile.txt
echo "   ✓ Text profile complete"
echo ""

echo "11. Testing memory leak detection..."
callflow-tracer memory-leak cli_demo.py -o cli_test_output/memory_leak.html --threshold 5 --no-browser
echo "   ✓ Memory leak detection complete"
echo ""

echo "12. Testing info command..."
callflow-tracer info cli_test_output/trace.json
echo "   ✓ Info display complete"
echo ""

echo "13. Testing detailed info..."
callflow-tracer info cli_test_output/trace.json --detailed
echo "   ✓ Detailed info complete"
echo ""

echo "14. Testing export to HTML..."
callflow-tracer export cli_test_output/trace.json -o cli_test_output/exported.html --format html
echo "   ✓ Export to HTML complete"
echo ""

echo "15. Testing export to 3D..."
callflow-tracer export cli_test_output/trace.json -o cli_test_output/exported_3d.html --format 3d
echo "   ✓ Export to 3D complete"
echo ""

# Create a second trace for comparison
echo "16. Creating second trace for comparison..."
callflow-tracer trace cli_demo.py --format json -o cli_test_output/trace2.json
echo "   ✓ Second trace complete"
echo ""

echo "17. Testing compare command..."
callflow-tracer compare cli_test_output/trace.json cli_test_output/trace2.json \
  -o cli_test_output/comparison.html \
  --label1 "First Run" \
  --label2 "Second Run" \
  --no-browser
echo "   ✓ Comparison complete"
echo ""

echo "=== All CLI tests completed successfully! ==="
echo ""
echo "Output files are in: cli_test_output/"
echo ""
echo "Generated files:"
ls -lh cli_test_output/
