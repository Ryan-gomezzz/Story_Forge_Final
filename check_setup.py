import requests
import sys

print("🔍 STORYFORGE AI - SYSTEM CHECK")
print("=" * 50)

# Check Ollama
print("\n🤖 CHECKING OLLAMA:")
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print("✅ Ollama is running!")
        print(f"📋 Available models: {[m['name'] for m in models]}")
        
        # Check if llama3.1:8b is available
        model_names = [model['name'] for model in models]
        if any('llama3.1:8b' in name for name in model_names):
            print("✅ llama3.1:8b model found!")
        else:
            print("❌ llama3.1:8b model NOT found!")
            print("🔧 Fix: Run 'ollama pull llama3.1:8b'")
    else:
        print(f"❌ Ollama responded with status: {response.status_code}")
except Exception as e:
    print(f"❌ Ollama not responding: {e}")
    print("🔧 Fix: Run 'ollama serve' in a terminal")

# Check GPU
print("\n🖥️ CHECKING GPU:")
try:
    import torch
    print(f"✅ PyTorch installed: {torch.__version__}")
    print(f"🔍 CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"🎮 GPU name: {torch.cuda.get_device_name(0)}")
        print(f"💾 GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        print("❌ CUDA not available")
        print("🔧 Fix: Install CUDA or use CPU fallback")
        
except ImportError:
    print("❌ PyTorch not installed")
    print("🔧 Fix: pip install torch==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118")

# Check Diffusers
print("\n🎨 CHECKING DIFFUSERS:")
try:
    from diffusers import StableDiffusionPipeline
    print("✅ Diffusers library available")
except ImportError:
    print("❌ Diffusers not installed")
    print("🔧 Fix: pip install diffusers==0.24.0 transformers==4.36.2")

# Test Ollama generation
print("\n🧪 TESTING OLLAMA GENERATION:")
try:
    payload = {
        "model": "llama3.1:8b",
        "messages": [{"role": "user", "content": "Write a 50 word story about a robot."}],
        "stream": False
    }
    
    response = requests.post('http://localhost:11434/api/chat', json=payload, timeout=30)
    if response.status_code == 200:
        result = response.json()
        story = result.get('message', {}).get('content', '')
        print("✅ Ollama test successful!")
        print(f"📝 Sample story: {story[:100]}...")
    else:
        print(f"❌ Ollama test failed: {response.status_code}")
except Exception as e:
    print(f"❌ Ollama test error: {e}")

print("\n" + "=" * 50)
print("🎯 NEXT STEPS:")
print("1. Fix any ❌ issues shown above")
print("2. Make sure Ollama is running: ollama serve")
print("3. Ensure model is downloaded: ollama pull llama3.1:8b")  
print("4. Install GPU packages if missing")
print("5. Restart your Django server")