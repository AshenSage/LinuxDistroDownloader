#!/usr/bin/env python3
"""
Linux Distro Downloader - Launcher Script

This script provides an alternative entry point for the application
with additional error handling and dependency checking.
"""

import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        print("Please upgrade Python and try again.")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = {
        'customtkinter': 'customtkinter>=5.2.0',
        'requests': 'requests>=2.31.0',
        'packaging': 'packaging>=23.0'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        if importlib.util.find_spec(package) is None:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print("Error: Missing required dependencies:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nTo install dependencies, run:")
        print(f"  pip install {' '.join(missing_packages)}")
        print("\nOr install all at once:")
        print("  pip install -r requirements.txt")
        
        # Ask user if they want to install automatically
        try:
            response = input("\nWould you like to install dependencies automatically? (y/n): ")
            if response.lower() in ['y', 'yes']:
                print("Installing dependencies...")
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
                    print("Dependencies installed successfully!")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"Failed to install dependencies: {e}")
                    return False
            else:
                return False
        except KeyboardInterrupt:
            print("\nInstallation cancelled.")
            return False
    
    return True

def check_data_file():
    """Check if distribution data file exists"""
    data_file = Path('distro_data.json')
    if not data_file.exists():
        print("Error: Distribution data file 'distro_data.json' not found.")
        print("Make sure you're running the script from the correct directory.")
        return False
    return True

def main():
    """Main launcher function"""
    print("Linux Distro Downloader - Starting up...")
    print("=" * 50)
    
    # Check Python version
    print("Checking Python version...")
    check_python_version()
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        print("\nCannot start application without required dependencies.")
        sys.exit(1)
    print("✓ All dependencies available")
    
    # Check data file
    print("Checking data files...")
    if not check_data_file():
        sys.exit(1)
    print("✓ Distribution data file found")
    
    print("\nStarting application...")
    print("=" * 50)
    
    # Import and run the main application
    try:
        from main import main as app_main
        app_main()
    except ImportError as e:
        print(f"Error importing main application: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)