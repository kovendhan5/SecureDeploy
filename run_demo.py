#!/usr/bin/env python3
"""
Quick Demo Launcher for PipeGuard
Runs the enhanced demo with real-time updates
"""

import subprocess
import sys
import os
import webbrowser
import time

def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     ██████╗ ██╗██████╗ ███████╗ ██████╗ ██╗   ██╗ █████╗   ║
    ║     ██╔══██╗██║██╔══██╗██╔════╝██╔════╝ ██║   ██║██╔══██╗  ║
    ║     ██████╔╝██║██████╔╝█████╗  ██║  ███╗██║   ██║███████║  ║
    ║     ██╔═══╝ ██║██╔═══╝ ██╔══╝  ██║   ██║██║   ██║██╔══██║  ║
    ║     ██║     ██║██║     ███████╗╚██████╔╝╚██████╔╝██║  ██║  ║
    ║     ╚═╝     ╚═╝╚═╝     ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝  ║
    ║                                                              ║
    ║              🚀  LIVE DEMO - REAL-TIME MONITORING  🚀       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print("\033[96m" + banner + "\033[0m")

def check_demo_data_generator():
    """Check if demo_data_generator.py exists"""
    if not os.path.exists('demo_data_generator.py'):
        print("❌ Error: demo_data_generator.py not found!")
        print("Please make sure all demo files are in the current directory.")
        return False
    return True

def main():
    print_banner()
    
    print("\n✨ PipeGuard Pro - Interactive Demo")
    print("=" * 60)
    print("📊 This demo showcases:")
    print("  • Real-time pipeline monitoring with live data updates")
    print("  • Interactive anomaly detection")
    print("  • AI-powered insights and recommendations")
    print("  • Performance analytics with beautiful charts")
    print("  • Manual build triggers for testing")
    print("=" * 60)
    
    # Check if demo files exist
    if not check_demo_data_generator():
        return
    
    print("\n🔧 Starting demo server...")
    print("📡 Demo features:")
    print("  ✓ Auto-refresh every 10 seconds")
    print("  ✓ Live statistics updates")
    print("  ✓ Interactive build triggers")
    print("  ✓ Real-time anomaly detection")
    print("\n🌐 Opening browser at http://localhost:8080...")
    print("⏰ Please wait 3 seconds...")
    
    # Start the demo server
    try:
        # Wait a moment before opening browser
        time.sleep(1)
        
        # Open browser
        def open_browser():
            time.sleep(3)
            webbrowser.open('http://localhost:8080')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run the demo app
        print("\n" + "=" * 60)
        print("🎯 Demo Server Starting...")
        print("=" * 60 + "\n")
        
        subprocess.run([sys.executable, 'demo_app.py'])
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user")
        print("Thank you for trying PipeGuard Pro!")
    except Exception as e:
        print(f"\n❌ Error starting demo: {e}")
        print("\nTry running manually:")
        print("  python demo_app.py")

if __name__ == '__main__':
    main()
