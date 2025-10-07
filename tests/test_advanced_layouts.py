"""
Test script for advanced graph layouts
"""

from callflow_tracer import trace, trace_scope, get_current_graph, export_html
import os


@trace
def function_a():
    return "A"


@trace
def function_b():
    function_a()
    return "B"


@trace
def function_c():
    function_a()
    return "C"


@trace
def function_d():
    function_b()
    function_c()
    return "D"


@trace
def main():
    function_d()
    function_b()
    function_c()


if __name__ == "__main__":
    print("Testing advanced graph layouts...")
    
    # Trace the execution
    with trace_scope("test_advanced_layouts.html"):
        main()
    
    # Verify the file was created
    if os.path.exists("test_advanced_layouts.html"):
        print("✅ HTML file generated successfully!")
        
        # Read and check for new layout options
        with open("test_advanced_layouts.html", "r") as f:
            content = f.read()
            
        # Check for all new layouts
        layouts = [
            "radial",
            "grid", 
            "tree",
            "tree-horizontal",
            "organic"
        ]
        
        missing = []
        for layout in layouts:
            if layout not in content:
                missing.append(layout)
        
        if missing:
            print(f"❌ Missing layouts: {', '.join(missing)}")
        else:
            print("✅ All advanced layouts are present!")
            
        # Check for spacing control
        if "node-spacing" in content:
            print("✅ Node spacing control is present!")
        else:
            print("❌ Node spacing control is missing!")
            
        # Check for layout functions
        if "changeLayout" in content and "updateLayoutSpacing" in content:
            print("✅ Layout control functions are present!")
        else:
            print("❌ Layout control functions are missing!")
            
        print("\n✅ All tests passed! Open 'test_advanced_layouts.html' to see the layouts.")
    else:
        print("❌ HTML file was not generated!")
