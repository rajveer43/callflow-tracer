"""
Complete test for node spacing and control fixes
"""

from callflow_tracer import trace, trace_scope
import time


@trace
def fast_function():
    """Fast function"""
    time.sleep(0.001)
    return "fast"


@trace
def medium_function():
    """Medium speed function"""
    time.sleep(0.01)
    fast_function()
    return "medium"


@trace
def slow_function():
    """Slow function"""
    time.sleep(0.05)
    medium_function()
    return "slow"


@trace
def process_data():
    """Process some data"""
    fast_function()
    medium_function()
    return "processed"


@trace
def main():
    """Main entry point"""
    slow_function()
    process_data()
    fast_function()


if __name__ == "__main__":
    print("=" * 70)
    print("COMPLETE NODE SPACING FIX TEST")
    print("=" * 70)
    print("\nGenerating test HTML with all fixes...")
    
    with trace_scope("test_spacing_complete_fix.html"):
        main()
    
    print("\n✅ HTML generated: test_spacing_complete_fix.html")
    print("\n" + "=" * 70)
    print("TESTING CHECKLIST")
    print("=" * 70)
    
    print("\n📋 Open the HTML file and verify:")
    print("\n1. SPACING CONTROL:")
    print("   ✓ Select 'Circular' layout")
    print("   ✓ Change spacing: Compact → Normal → Relaxed → Wide")
    print("   ✓ Circle should grow/shrink smoothly")
    print("   ✓ Try with 'Grid' layout - nodes should spread out")
    print("   ✓ Try with 'Radial Tree' - circles should expand")
    
    print("\n2. PHYSICS TOGGLE:")
    print("   ✓ Select 'Force-Directed' layout")
    print("   ✓ Toggle Physics: Enabled → Disabled → Enabled")
    print("   ✓ No console errors should appear")
    print("   ✓ Nodes should stop/start moving")
    
    print("\n3. LAYOUT SWITCHING:")
    print("   ✓ Try all 9 layouts in dropdown")
    print("   ✓ Each should render correctly")
    print("   ✓ No JavaScript errors in console")
    
    print("\n4. COMBINED TEST:")
    print("   ✓ Select 'Grid' layout with 'Compact' spacing")
    print("   ✓ Switch to 'Wide' spacing - grid should expand")
    print("   ✓ Switch to 'Circular' layout - should use Wide spacing")
    print("   ✓ Switch to 'Radial Tree' - should use Wide spacing")
    
    print("\n" + "=" * 70)
    print("FIXED ISSUES")
    print("=" * 70)
    print("✅ window.network now assigned AFTER network creation")
    print("✅ togglePhysics function uses window.network")
    print("✅ All event listeners use window.network")
    print("✅ Circular layout uses custom spacing (radius = spacing * 2)")
    print("✅ Timeline layout uses custom spacing")
    print("✅ All layouts respond to spacing changes")
    print("=" * 70)
    
    print("\n🚀 Ready to test! Open the HTML file in your browser.")
