#!/usr/bin/env python3
"""
Installation script for callflow-tracer.
This script installs the package in development mode.
"""

import subprocess
import sys
import os

def install_package():
    """Install the callflow-tracer package in development mode."""
    print("🚀 Installing callflow-tracer...")
    
    try:
        # Install in development mode
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("✅ Installation completed successfully!")
        
        # Test the installation
        print("\n🧪 Testing installation...")
        import callflow_tracer
        print(f"✅ Package imported successfully! Version: {callflow_tracer.__version__}")
        
        print("\n🎉 callflow-tracer is ready to use!")
        print("\nQuick start:")
        print("  from callflow_tracer import trace, trace_scope")
        print("  ")
        print("  @trace")
        print("  def my_function():")
        print("      return 'Hello, World!'")
        print("  ")
        print("  with trace_scope('output.html'):")
        print("      my_function()")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = install_package()
    sys.exit(0 if success else 1)
