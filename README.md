StoryForge AI - Enhanced AI Story Generator
Overview
StoryForge AI is a powerful Django web application that generates unique AI-written stories along with high-quality images. It leverages local GPU acceleration and Ollama AI for story creation, alongside Stable Diffusion for generating vivid character and background images.

This project also supports audio input for story prompts, providing an all-around creative storytelling experience.

Setup Instructions
1. Prerequisites
A computer with an NVIDIA CUDA-compatible GPU (8GB VRAM or more recommended)

Python 3.10 or later installed

NVIDIA drivers installed with CUDA 11.8 or 12.1+ support

Ollama AI installed and running locally for story generation

2. Get the Project
Download or clone the project zip, and extract it to your working folder.

3. Setup Python Environment (Recommended)
bash
python -m venv gpu_env
# Windows
gpu_env\Scripts\activate
# Linux/macOS
source gpu_env/bin/activate
4. Install Dependencies
bash
pip install --upgrade pip

pip install torch==2.1.0+cu121 torchvision==0.16.0+cu121 torchaudio==2.1.0+cu121 --index-url https://download.pytorch.org/whl/cu121

pip install diffusers==0.24.0 transformers==4.36.2 accelerate==0.25.0 xformers==0.0.23 requests

pip install django==4.2.0 python-dotenv pillow requests
If you want audio input support:

bash
pip install openai-whisper SpeechRecognition pydub
5. Install and Start Ollama
Windows: Install using winget install Ollama.Ollama

Other: Download from https://ollama.ai/download

Then start Ollama and pull the model:

bash
ollama serve
ollama pull llama3.1:8b
Keep Ollama running while using the app.

6. Setup Environment Variables
Create a .env file in the project root with content like:

text
USE_GPU=True
OLLAMA_HOST=http://localhost:11434
DEBUG=True
IMAGE_WIDTH=512
IMAGE_HEIGHT=512
7. Database Setup
Run migrations:

bash
python manage.py makemigrations
python manage.py migrate
(Optional) Create an admin user:

bash
python manage.py createsuperuser
8. Run the Server
bash
python manage.py runserver
Open your browser at http://localhost:8000 to start using StoryForge AI.

Architecture Overview
Core Components
Django Web Framework
Hosts the web app, routes requests, serves the interface, and manages the database.

Ollama Story Generator (generator/ollama_story_generator.py)
Interfaces with the Ollama API running locally to generate diverse, coherent, and immersive stories in natural language.

GPU Image Generator (generator/gpu_image_generator.py)
Uses Stable Diffusion model via Hugging Face’s Diffusers with PyTorch to generate high-quality images of characters and backgrounds using your GPU.

Views (generator/views.py)
Coordinates user inputs, calls AI services (story and image generation), and returns rendered responses to the frontend.

Audio Input Support
Optional Whisper AI-powered module for transcribing voice prompts into text for story generation.

Interaction Flow
User enters a story prompt via text or audio.

The prompt is sent to Ollama running locally to produce a detailed story.

The story is analyzed to extract character and scene details.

Extracted details feed into the GPU image generator.

Stable Diffusion creates realistic character portraits and background environments.

Generated story and images are displayed in a modern, responsive web UI.

Prompt Engineering Documentation
How the Story Prompt Works
The user inputs a simple text prompt (e.g., "A brave knight discovers a magic sword").

This prompt is sent to the Ollama model running locally. Ollama uses a powerful LLM (language model) to expand this into a rich, 500-1500 word story.

Ollama’s prompt includes instructions to generate immersive narratives with vibrant details, emotional arcs, and creative dialogue.

The model output is a coherent story, unique every time due to the stochastic nature of the LLM.

How Character and Background Prompts Are Constructed
Character Prompts:
The story text is parsed to identify characters and their defining traits (e.g., clothing, appearance, attitude).
Example prompt to the image model:
"A medieval knight in detailed armor, stern expression, heroic pose, cinematic lighting, fantasy art style, 8k detailed portrait"

Background Prompts:
Key scenes from the story are extracted providing context for the environment.
Example prompt:
"A dense enchanted forest with glowing mushrooms, mist swirling around ancient trees, fantasy landscape, digital art, 8k"

These prompts are carefully engineered to guide the Stable Diffusion model to generate images matching the narrative while maintaining high artistic quality and realism.

Example Outputs and Iterations
Example Prompt:
User Input:
"A young wizard in a magical forest discovers a powerful artifact"

Story Output (excerpt):
"Elyan, the young wizard cloaked in deep blue robes, stepped cautiously into the heart of the enchanted forest. Sunlight filtered through ancient, towering trees as he sensed the hum of magic in the air. In a moss-covered clearing, a radiant artifact pulsed softly, calling to his destiny..."

Character Image Prompt:
"A young wizard with flowing blue robes, holding a glowing staff, mystical aura, fantasy portrait, cinematic lighting, 8k resolution"

Background Image Prompt:
"An enchanted forest with sunlight beams, moss-covered trees, magical glow, fantasy digital art, 8k"

Iterations:
Initial story might be shorter or less detailed; the prompt to Ollama can be modified to increase length and detail.

Similarly, image prompts can be tuned by adding or changing descriptors like art style, lighting, resolution, or specific attributes.

Advanced users can customize prompt templates in code to change tone (dark fantasy, whimsical, sci-fi) or visual style (oil painting, photorealistic, comic).
