#!/usr/bin/env python3
"""
JARVIS Voice-Controlled Assistant Launcher
Simplified launcher that handles the integration between backend and frontend
"""

import sys
import os
import threading
import time
import subprocess
from pathlib import Path

# Windows console compatibility
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")  # Set UTF-8 encoding

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'PyQt5', 'groq', 'cohere', 'edge-tts', 'pygame', 
        'selenium', 'requests', 'pillow', 'beautifulsoup4',
        'pywhatkit', 'appopener', 'keyboard', 'mtranslate',
        'googlesearch-python', 'webdriver-manager', 'rich'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                import bs4
            elif package == 'googlesearch-python':
                import googlesearch
            elif package == 'webdriver-manager':
                import webdriver_manager
            elif package == 'pillow':
                import PIL
            elif package == 'appopener':
                import AppOpener
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("ERROR: Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists(".env"):
        print("ERROR: .env file not found!")
        print("Please create a .env file with your API keys.")
        print("   You can use env_template.txt as a reference.")
        return False
    
    # Check for required environment variables
    required_vars = ['GroqAPIKey', 'CohereAPIKey', 'Username', 'Assistantname', 'InputLanguage']
    missing_vars = []
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
    except ImportError:
        print("ERROR: python-dotenv not installed. Install with: pip install python-dotenv")
        return False
    
    if missing_vars:
        print("ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    return True

def setup_directories():
    """Create necessary directories and files"""
    directories = [
        "Data",
        "Frontend/Files",
        "Frontend/Graphics"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"OK: Created directory: {directory}")
    
    # Create necessary data files
    data_files = [
        ("Data/Chatlog.json", "[]"),
        ("Frontend/Files/Status.data", ""),
        ("Frontend/Files/Mic.data", "False"),
        ("Frontend/Files/Responses.data", ""),
        ("Frontend/Files/ImageGeneration.data", "False,False"),
        ("Frontend/Files/Database.data", "")
    ]
    
    for file_path, default_content in data_files:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(default_content)
            print(f"OK: Created file: {file_path}")

def run_backend_services():
    """Run backend services in separate processes"""
    backend_services = [
        "Backend/ImageGeneration.py",
        "Backend/RealtimeSearchEngine.py"
    ]
    
    processes = []
    
    for service in backend_services:
        if os.path.exists(service):
            try:
                process = subprocess.Popen([sys.executable, service], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
                processes.append(process)
                print(f"OK: Started backend service: {service}")
            except Exception as e:
                print(f"WARNING: Could not start {service}: {e}")
    
    return processes

def main():
    """Main launcher function"""
    print("=" * 60)
    print("JARVIS Voice-Controlled Assistant")
    print("=" * 60)
    
    # Check dependencies
    print("\nChecking dependencies...")
    if not check_dependencies():
        return
    
    # Check environment file
    print("\nChecking environment configuration...")
    if not check_env_file():
        return
    
    # Setup directories
    print("\nSetting up directories...")
    setup_directories()
    
    # Start backend services
    print("\nStarting backend services...")
    backend_processes = run_backend_services()
    
    try:
        # Start the main GUI
        print("\nStarting GUI...")
        print("Click the microphone button to start voice control!")
        print("You can also use the GUI to navigate between screens.")
        print("\n" + "=" * 60)
        
        # Import and run the main application
        from main import JarvisAssistant
        assistant = JarvisAssistant()
        assistant.start()
        
    except KeyboardInterrupt:
        print("\nShutting down JARVIS...")
    except Exception as e:
        print(f"\nERROR running JARVIS: {e}")
    finally:
        # Clean up backend processes
        print("\nCleaning up backend processes...")
        for process in backend_processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("Shutdown complete!")

if __name__ == "__main__":
    main()

