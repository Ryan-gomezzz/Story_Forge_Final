"""
Enhanced story generator using Ollama for varied, high-quality stories.
"""
import json
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OllamaStoryGenerator:
    """Generate diverse stories using Ollama local AI."""
    
    def __init__(self, ai_settings: Dict[str, Any] = None):
        self.ai_settings = ai_settings or {}
        self.ollama_host = 'http://localhost:11434'
        self.story_model = 'llama3.1:8b'
        self.available = self._check_ollama_availability()
        
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                return any(self.story_model in name for name in model_names)
            return False
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def generate_story(self, user_prompt: str, length: str = 'medium') -> str:
        """Generate unique story using Ollama."""
        if not self.available:
            return self._generate_fallback_story(user_prompt)
        
        try:
            system_prompt = f"""You are a master storyteller. Create an original, engaging story that:
- Is completely unique and different from typical stories
- Has unexpected plot twists and creative elements
- Includes rich character development and dialogue
- Is approximately {self._get_word_target(length)} words
Be creative and avoid clichés."""

            full_prompt = f'Based on this idea: "{user_prompt}"\n\nCreate an original story that is memorable and distinctive.'

            story = self._call_ollama(system_prompt, full_prompt)
            
            if story and len(story.split()) > 100:
                return story
            else:
                return self._generate_fallback_story(user_prompt)
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return self._generate_fallback_story(user_prompt)
    
    def generate_character_description(self, story: str) -> str:
        """Generate character description for image generation."""
        if not self.available:
            return self._fallback_character_description(story)
        
        try:
            system_prompt = "Create a detailed visual description of the main character for AI image generation. Include physical appearance, clothing, and mood."
            user_prompt = f"Story: {story[:1000]}...\n\nDescribe the main character visually in under 100 words."
            
            description = self._call_ollama(system_prompt, user_prompt)
            return description if description else self._fallback_character_description(story)
            
        except Exception as e:
            return self._fallback_character_description(story)
    
    def generate_scene_description(self, story: str) -> str:
        """Generate scene description for image generation."""
        if not self.available:
            return self._fallback_scene_description(story)
        
        try:
            system_prompt = "Create a detailed scene description for AI image generation. Focus on environment, lighting, and atmosphere."
            user_prompt = f"Story: {story[:1000]}...\n\nDescribe the main setting visually in under 100 words."
            
            description = self._call_ollama(system_prompt, user_prompt)
            return description if description else self._fallback_scene_description(story)
            
        except Exception as e:
            return self._fallback_scene_description(story)
    
    def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """Make API call to Ollama."""
        try:
            payload = {
                "model": self.story_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {"temperature": 0.8}
            }
            
            response = requests.post(f"{self.ollama_host}/api/chat", json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('message', {}).get('content', '').strip()
            return ""
                
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            return ""
    
    def _get_word_target(self, length: str) -> str:
        """Get word count target."""
        targets = {'short': '300-500', 'medium': '500-1000', 'long': '1000-1500'}
        return targets.get(length, '500-1000')
    
    def _generate_fallback_story(self, prompt: str) -> str:
        """Enhanced fallback story."""
        return f"""In a world of endless possibilities, the adventure began with {prompt.lower()}. What started as an ordinary moment quickly transformed into something extraordinary that would change everything.

Our protagonist discovered that reality was far more complex and wonderful than they had ever imagined. Each step forward revealed new mysteries, each challenge overcome led to greater revelations, and each friend made along the way added depth to a journey of self-discovery.

The path was neither straight nor easy. Obstacles that seemed insurmountable became stepping stones to growth. Enemies revealed unexpected depths. Allies emerged from unlikely places, and wisdom came from sources both ancient and new.

As the journey progressed, our hero learned that true strength comes not from individual prowess, but from connections forged with others. The greatest magic was not in supernatural powers, but in the human ability to hope, persevere, and find light in darkness.

The resolution was both surprising and inevitable. What began with {prompt.lower()} became a transformation not just of circumstances, but of character. The adventure's end marked a beginning—the start of a life lived with purpose and courage.

And so our story concludes, but the ripples would continue to spread, inspiring others to find their own courage and embark on their own journeys of discovery."""
    
    def _fallback_character_description(self, story: str) -> str:
        """Fallback character description."""
        story_lower = story.lower()
        
        if 'knight' in story_lower or 'sword' in story_lower:
            return "A determined knight in polished steel armor with a noble bearing, strong jawline, and piercing blue eyes. Wears a deep red cloak and carries an ornate sword."
        elif 'wizard' in story_lower or 'magic' in story_lower:
            return "An ancient wizard with flowing silver robes, long white beard, deep violet eyes, and a tall staff crowned with a glowing crystal orb."
        elif 'space' in story_lower or 'star' in story_lower:
            return "A confident space explorer in a sleek uniform with integrated technology, sharp features, and advanced equipment."
        else:
            return "A brave adventurer with an athletic build, practical traveling clothes, and the confident bearing of someone ready for any challenge."
    
    def _fallback_scene_description(self, story: str) -> str:
        """Fallback scene description."""
        story_lower = story.lower()
        
        if 'forest' in story_lower or 'tree' in story_lower:
            return "An ancient enchanted forest with towering oak trees, golden sunlight streaming through emerald canopy, and crystal streams."
        elif 'castle' in story_lower or 'tower' in story_lower:
            return "A majestic medieval castle perched on a cliff, with grey stone towers, colorful banners, and warm light from arched windows."
        elif 'space' in story_lower or 'star' in story_lower:
            return "The infinite vastness of space with countless stars, spectacular nebulae in brilliant colors, and distant spiral galaxies."
        else:
            return "A breathtaking landscape under a dramatic sunset sky with rolling hills, ancient ruins, and a winding path toward adventure."

def check_and_suggest_ollama_setup():
    """Check Ollama setup."""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            return True, model_names
        return False, []
    except:
        return False, []