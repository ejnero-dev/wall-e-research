#!/usr/bin/env python3
"""
Ollama Setup Script for Wall-E AI Engine
Downloads and configures Ollama with the recommended model
"""

import os
import sys
import subprocess
import requests
import time
import json

def run_command(command, shell=True, check=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_ollama_installed():
    """Check if Ollama is already installed"""
    success, stdout, stderr = run_command("which ollama", check=False)
    return success

def install_ollama():
    """Install Ollama"""
    print("📦 Installing Ollama...")
    
    # Download and install Ollama
    install_script = """
    curl -fsSL https://ollama.ai/install.sh | sh
    """
    
    print("⬇️ Downloading Ollama installation script...")
    success, stdout, stderr = run_command(install_script, check=False)
    
    if not success:
        print(f"❌ Installation failed: {stderr}")
        return False
    
    print("✅ Ollama installed successfully")
    return True

def start_ollama_service():
    """Start Ollama service"""
    print("🚀 Starting Ollama service...")
    
    # Try to start as service
    success, stdout, stderr = run_command("ollama serve &", check=False)
    
    if not success:
        print("⚠️ Failed to start as service, trying direct start...")
        # Try direct start in background
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✅ Ollama service started in background")
        except Exception as e:
            print(f"❌ Failed to start Ollama: {e}")
            return False
    
    # Wait for service to be ready
    print("⏳ Waiting for Ollama service to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print("✅ Ollama service is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    
    print("❌ Ollama service did not start within 30 seconds")
    return False

def pull_model(model_name="llama3.2:11b-vision-instruct-q4_0"):
    """Pull the required model"""
    print(f"📥 Pulling model: {model_name}")
    print("⚠️ This may take 15-30 minutes depending on your internet connection...")
    
    # Start the pull
    process = subprocess.Popen(
        ["ollama", "pull", model_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Monitor progress
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(f"📥 {output.strip()}")
    
    return_code = process.poll()
    if return_code == 0:
        print(f"✅ Model {model_name} pulled successfully")
        return True
    else:
        error = process.stderr.read()
        print(f"❌ Failed to pull model: {error}")
        return False

def verify_installation():
    """Verify that everything is working"""
    print("🔍 Verifying installation...")
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama service not responding")
            return False
        
        models = response.json()
        if not models.get('models'):
            print("❌ No models found")
            return False
        
        print(f"✅ Found {len(models['models'])} model(s):")
        for model in models['models']:
            print(f"  - {model['name']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_model_inference(model_name="llama3.2:11b-vision-instruct-q4_0"):
    """Test model inference"""
    print("🧪 Testing model inference...")
    
    test_prompt = "Responde solo 'OK' en español"
    
    success, stdout, stderr = run_command(
        f'ollama run {model_name} "{test_prompt}"',
        check=False
    )
    
    if success and "ok" in stdout.lower():
        print("✅ Model inference test passed")
        print(f"Response: {stdout.strip()}")
        return True
    else:
        print(f"❌ Model inference test failed: {stderr}")
        return False

def main():
    """Main setup process"""
    print("🤖 Wall-E Ollama Setup Script")
    print("="*50)
    
    # Check system requirements
    print("🔍 Checking system requirements...")
    
    # Check if running on supported system
    if os.name != 'posix':
        print("❌ This script only supports Linux/Unix systems")
        return False
    
    # Check available memory
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemTotal:' in line:
                    mem_kb = int(line.split()[1])
                    mem_gb = mem_kb / 1024 / 1024
                    print(f"💾 Available RAM: {mem_gb:.1f}GB")
                    
                    if mem_gb < 12:
                        print("⚠️ Warning: Less than 12GB RAM detected. Consider using a smaller model.")
                        model_name = "phi3.5:3.8b-mini-instruct-q4_0"
                        print(f"🔄 Switching to lighter model: {model_name}")
                    else:
                        model_name = "llama3.2:11b-vision-instruct-q4_0"
                        print(f"✅ Using recommended model: {model_name}")
                    break
    except Exception as e:
        print(f"⚠️ Could not detect RAM: {e}")
        model_name = "llama3.2:11b-vision-instruct-q4_0"
    
    # Step 1: Install Ollama if not present
    if check_ollama_installed():
        print("✅ Ollama is already installed")
    else:
        if not install_ollama():
            print("❌ Failed to install Ollama")
            return False
    
    # Step 2: Start Ollama service
    if not start_ollama_service():
        print("❌ Failed to start Ollama service")
        print("💡 Try running manually: ollama serve")
        return False
    
    # Step 3: Pull model
    if not pull_model(model_name):
        print("❌ Failed to pull model")
        return False
    
    # Step 4: Verify installation
    if not verify_installation():
        print("❌ Installation verification failed")
        return False
    
    # Step 5: Test inference
    if not test_model_inference(model_name):
        print("❌ Model inference test failed")
        return False
    
    print("\n" + "="*50)
    print("🎉 Ollama setup completed successfully!")
    print(f"📝 Model installed: {model_name}")
    print("🚀 AI Engine is now ready for full operation")
    print("\n💡 Next steps:")
    print("1. Run: python scripts/test_ai_engine_basic.py")
    print("2. Test full AI Engine: python scripts/test_ai_engine_full.py")
    print("3. Integrate with Wall-E bot")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)