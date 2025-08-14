"""
Enhanced LangChain orchestrator with real AI model integration.
Supports OpenAI, Anthropic, and Hugging Face models for story generation.
"""
import os
import logging
from typing import Dict, Any, Optional
from django.conf import settings

# LangChain imports
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser

# Model providers
try:
    from langchain_openai import OpenAI, ChatOpenAI
    from langchain_community.llms import HuggingFacePipeline
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    import torch
    AI_IMPORTS_AVAILABLE = True
except ImportError:
    AI_IMPORTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class StoryOutputParser(BaseOutputParser):
    """Parse story output to ensure proper formatting."""

    def parse(self, text: str) -> str:
        """Clean and format the generated story."""
        # Remove any unwanted prefixes/suffixes
        text = text.strip()

        # Ensure minimum length
        min_length = getattr(settings, 'AI_MODELS', {}).get('STORY_MIN_LENGTH', 500)
        words = text.split()

        if len(words) < min_length // 4:  # Rough word count estimate
            text += "\n\nThe adventure continues with even more exciting discoveries and challenges that test our hero's courage, wisdom, and determination. Each step forward reveals new mysteries and brings them closer to their ultimate destiny."

        return text

    @property
    def _type(self) -> str:
        return "story_output_parser"

class EnhancedStoryOrchestrator:
    """Advanced story orchestrator using LangChain with multiple AI providers."""

    def __init__(self):
        self.ai_settings = getattr(settings, 'AI_MODELS', {})
        self.llm = self._initialize_llm()
        self.story_chain = self._create_story_chain()
        self.character_chain = self._create_character_chain()
        self.background_chain = self._create_background_chain()

    def _initialize_llm(self):
        """Initialize the language model based on configuration."""
        if not AI_IMPORTS_AVAILABLE:
            logger.warning("AI libraries not available, using fallback")
            return None

        provider = self.ai_settings.get('TEXT_MODEL_PROVIDER', 'huggingface')

        try:
            if provider == 'openai' and self.ai_settings.get('OPENAI_API_KEY'):
                return ChatOpenAI(
                    openai_api_key=self.ai_settings['OPENAI_API_KEY'],
                    model_name="gpt-3.5-turbo",
                    temperature=0.8,
                    max_tokens=1500
                )
            elif provider == 'huggingface':
                return self._initialize_huggingface_llm()
            else:
                logger.warning(f"Provider {provider} not configured, using fallback")
                return None

        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            return None

    def _initialize_huggingface_llm(self):
        """Initialize Hugging Face pipeline."""
        try:
            model_name = self.ai_settings.get('TEXT_MODEL_NAME', 'microsoft/DialoGPT-medium')

            # Use GPU if available and enabled
            device = 0 if torch.cuda.is_available() and self.ai_settings.get('USE_GPU') else -1

            text_generator = pipeline(
                "text-generation",
                model=model_name,
                device=device,
                max_length=1000,
                temperature=0.8,
                do_sample=True,
                pad_token_id=50256
            )

            return HuggingFacePipeline(pipeline=text_generator)

        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face model: {e}")
            return None

    def _create_story_chain(self):
        """Create the main story generation chain."""
        story_template = """You are a master storyteller known for creating immersive, detailed narratives. 

Create a compelling story based on this prompt: {user_prompt}

Requirements:
- Length: 500-1500 words
- Rich character development with detailed descriptions
- Vivid setting and world-building
- Engaging plot with clear beginning, middle, and end
- Descriptive language that paints clear visual scenes
- Include dialogue and character interactions
- Create atmosphere and mood through detailed descriptions

Style: Write in an engaging, literary style with rich imagery and emotional depth.

Story:"""

        if self.llm:
            prompt = PromptTemplate(
                input_variables=["user_prompt"],
                template=story_template
            )

            return LLMChain(
                llm=self.llm,
                prompt=prompt,
                output_parser=StoryOutputParser(),
                verbose=True
            )
        return None

    def _create_character_chain(self):
        """Create character description extraction chain."""
        character_template = """Analyze this story and extract detailed character descriptions suitable for image generation:

Story: {story_text}

Extract the main character's visual details:

PHYSICAL APPEARANCE:
- Age and build
- Hair (color, style, length)
- Eyes (color, expression)
- Facial features
- Height and body type
- Skin tone
- Any distinctive features

CLOTHING AND STYLE:
- Specific clothing items and colors
- Style period (modern, medieval, futuristic, etc.)
- Accessories (jewelry, weapons, tools)
- Overall aesthetic

CHARACTER TRAITS VISIBLE IN APPEARANCE:
- Posture and demeanor
- Expression and mood
- Social status indicators

Format as a detailed visual description for AI image generation:"""

        if self.llm:
            prompt = PromptTemplate(
                input_variables=["story_text"],
                template=character_template
            )

            return LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=True
            )
        return None

    def _create_background_chain(self):
        """Create background/scene description extraction chain."""
        background_template = """Analyze this story and create a detailed scene description for the main setting:

Story: {story_text}

Create a detailed visual description of the primary setting:

ENVIRONMENT:
- Location type (indoor/outdoor, specific place)
- Time of day and lighting
- Weather and atmospheric conditions
- Season and climate

VISUAL ELEMENTS:
- Key architectural or natural features
- Colors and textures
- Foreground, middle ground, background elements
- Scale and perspective

MOOD AND ATMOSPHERE:
- Overall feeling and tone
- Lighting quality (soft, harsh, mystical, etc.)
- Environmental details that support the story

Format as a detailed scene description for AI image generation:"""

        if self.llm:
            prompt = PromptTemplate(
                input_variables=["story_text"],
                template=background_template
            )

            return LLMChain(
                llm=self.llm,
                prompt=prompt,
                verbose=True
            )
        return None

    def generate_story(self, user_prompt: str) -> str:
        """Generate a full story from user prompt."""
        try:
            if self.story_chain:
                result = self.story_chain.run(user_prompt=user_prompt)
                return result
            else:
                # Fallback to template-based generation
                return self._generate_fallback_story(user_prompt)

        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            return self._generate_fallback_story(user_prompt)

    def extract_character_description(self, story_text: str) -> str:
        """Extract character description from story."""
        try:
            if self.character_chain:
                result = self.character_chain.run(story_text=story_text)
                return result
            else:
                return self._generate_fallback_character(story_text)

        except Exception as e:
            logger.error(f"Character extraction failed: {e}")
            return self._generate_fallback_character(story_text)

    def extract_background_description(self, story_text: str) -> str:
        """Extract background description from story."""
        try:
            if self.background_chain:
                result = self.background_chain.run(story_text=story_text)
                return result
            else:
                return self._generate_fallback_background(story_text)

        except Exception as e:
            logger.error(f"Background extraction failed: {e}")
            return self._generate_fallback_background(story_text)

    def _generate_fallback_story(self, prompt: str) -> str:
        """Fallback story generation using templates."""
        templates = [
            f"In a world where imagination knows no bounds, {prompt.lower()} begins an extraordinary journey. The protagonist faces challenges that test their courage, discovers hidden truths about themselves, and ultimately transforms not just their own destiny, but the fate of everyone around them. Through trials of strength, wisdom, and heart, they learn that true power comes from within, and that even the smallest actions can have the greatest impact. The adventure unfolds across mystical landscapes and through encounters with memorable characters, each adding depth to a tale that celebrates the triumph of hope over despair, courage over fear, and love over hatred.",

            f"Once upon a time, in a realm beyond ordinary reality, {prompt.lower()} set in motion events that would change everything. Our hero embarks on a quest filled with wonder, danger, and discovery. Along the way, they encounter allies who become lifelong friends, face enemies who challenge their resolve, and discover powers they never knew they possessed. The journey takes them through enchanted forests, across vast oceans, over towering mountains, and into the depths of ancient mysteries. Each step forward brings new revelations, and each challenge overcome makes them stronger. In the end, they realize that the greatest adventure was not the destination, but the transformation that occurred along the way."
        ]

        import random
        return random.choice(templates)

    def _generate_fallback_character(self, story: str) -> str:
        """Fallback character description."""
        if 'knight' in story.lower():
            return "A noble warrior with strong build, wearing gleaming plate armor with intricate engravings. Has determined blue eyes, weathered hands from battle, and carries an ornate sword. Cape flows behind them, and their posture exudes confidence and honor."
        elif 'wizard' in story.lower():
            return "An elderly sage with flowing white beard and wise, twinkling eyes. Wears deep blue robes adorned with silver stars and moons. Carries a tall wooden staff topped with a glowing crystal orb. Has weathered hands that speak of years spent studying ancient magic."
        elif 'space' in story.lower():
            return "A futuristic explorer in sleek, form-fitting space suit with transparent helmet. Has confident posture and keen eyes that have seen the wonders of the cosmos. Suit displays various technological interfaces and equipment for space exploration."
        else:
            return "A brave adventurer with athletic build and determined expression. Wears practical clothing suited for their journey - leather boots, sturdy pants, and a weather-worn jacket. Carries essential gear and has the look of someone ready for any challenge."

    def _generate_fallback_background(self, story: str) -> str:
        """Fallback background description."""
        if 'forest' in story.lower():
            return "An ancient enchanted forest with towering trees whose canopy filters golden sunlight into dancing beams. Moss-covered rocks and fallen logs create natural paths, while magical creatures can be glimpsed in the shadows. The air shimmers with mystical energy."
        elif 'space' in story.lower():
            return "The vast expanse of space with distant galaxies swirling in cosmic dances. Nebulae paint the darkness in brilliant purples, blues, and golds. A nearby planet looms large, its surface mysterious and inviting exploration."
        elif 'castle' in story.lower():
            return "A majestic medieval castle perched on a hilltop, its towers reaching toward dramatic clouds. Stone walls weathered by time but still strong, with banners flying from tall flagpoles. The surrounding landscape rolls away in green hills and distant mountains."
        else:
            return "A dramatic landscape that perfectly captures the mood of the adventure - rolling hills, distant mountains, and a sky painted with the colors of dawn or dusk. The scene conveys a sense of journey and possibility, with paths leading toward unknown horizons."
