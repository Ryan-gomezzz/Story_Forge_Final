"""
Enhanced image generator using Stable Diffusion and other AI models.
Supports multiple providers and generates realistic character and background images.
"""
import os
import logging
import requests
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import torch
from django.conf import settings

# Try to import AI image generation libraries
try:
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    from transformers import pipeline
    AI_IMAGE_AVAILABLE = True
except ImportError:
    AI_IMAGE_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedImageGenerator:
    """Enhanced image generator with multiple AI model support."""

    def __init__(self):
        self.ai_settings = getattr(settings, 'AI_MODELS', {})
        self.character_pipeline = None
        self.background_pipeline = None
        self._initialize_pipelines()

    def _initialize_pipelines(self):
        """Initialize Stable Diffusion pipelines."""
        if not AI_IMAGE_AVAILABLE:
            logger.warning("AI image libraries not available, using enhanced fallback")
            return

        try:
            # Initialize character generation pipeline
            character_model = self.ai_settings.get('CHARACTER_MODEL', 'runwayml/stable-diffusion-v1-5')

            if torch.cuda.is_available() and self.ai_settings.get('USE_GPU'):
                self.character_pipeline = StableDiffusionPipeline.from_pretrained(
                    character_model,
                    torch_dtype=torch.float16,
                    safety_checker=None,
                    requires_safety_checker=False
                ).to("cuda")

                # Use DPM solver for faster generation
                self.character_pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                    self.character_pipeline.scheduler.config
                )

                # Enable memory efficient attention
                self.character_pipeline.enable_attention_slicing()

            logger.info("Stable Diffusion pipeline initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Stable Diffusion: {e}")
            self.character_pipeline = None

    def generate_character_image(self, description: str) -> bytes:
        """Generate character image using Stable Diffusion or enhanced fallback."""
        try:
            if self.character_pipeline:
                return self._generate_with_stable_diffusion(description, "character")
            else:
                return self._generate_enhanced_fallback_character(description)

        except Exception as e:
            logger.error(f"Character image generation failed: {e}")
            return self._generate_enhanced_fallback_character(description)

    def generate_background_image(self, description: str) -> bytes:
        """Generate background image using Stable Diffusion or enhanced fallback."""
        try:
            if self.character_pipeline:  # Use same pipeline for backgrounds
                return self._generate_with_stable_diffusion(description, "background")
            else:
                return self._generate_enhanced_fallback_background(description)

        except Exception as e:
            logger.error(f"Background image generation failed: {e}")
            return self._generate_enhanced_fallback_background(description)

    def _generate_with_stable_diffusion(self, description: str, image_type: str) -> bytes:
        """Generate image using Stable Diffusion."""
        # Enhance prompt for better results
        if image_type == "character":
            enhanced_prompt = f"high quality portrait, detailed character, {description}, professional digital art, trending on artstation, 8k resolution, highly detailed"
            negative_prompt = "blurry, low quality, distorted, ugly, bad anatomy, extra limbs"
        else:
            enhanced_prompt = f"beautiful landscape, detailed environment, {description}, professional digital art, stunning scenery, high resolution, masterpiece"
            negative_prompt = "blurry, low quality, people, characters, text, watermark"

        # Generate image
        with torch.autocast("cuda"):
            result = self.character_pipeline(
                enhanced_prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=20,
                guidance_scale=7.5,
                width=self.ai_settings.get('IMAGE_WIDTH', 512),
                height=self.ai_settings.get('IMAGE_HEIGHT', 512),
            )

        # Convert to bytes
        image = result.images[0]
        buffer = BytesIO()
        image.save(buffer, format='PNG', quality=95)
        return buffer.getvalue()

    def _generate_enhanced_fallback_character(self, description: str) -> bytes:
        """Generate enhanced character placeholder."""
        width = self.ai_settings.get('IMAGE_WIDTH', 512)
        height = self.ai_settings.get('IMAGE_HEIGHT', 512)

        # Create gradient background based on character type
        if 'knight' in description.lower():
            colors = [(70, 70, 120), (120, 120, 180), (180, 180, 220)]
        elif 'wizard' in description.lower():
            colors = [(80, 40, 120), (140, 80, 180), (200, 160, 240)]
        elif 'space' in description.lower():
            colors = [(20, 20, 60), (60, 80, 140), (100, 140, 200)]
        else:
            colors = [(100, 120, 80), (140, 180, 120), (180, 220, 160)]

        # Create radial gradient
        img = Image.new('RGB', (width, height), colors[0])
        draw = ImageDraw.Draw(img)

        # Create multiple circles for gradient effect
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 2

        for i in range(max_radius, 0, -5):
            alpha = i / max_radius
            color_idx = int(alpha * (len(colors) - 1))
            color = colors[min(color_idx, len(colors) - 1)]

            draw.ellipse([
                center_x - i, center_y - i,
                center_x + i, center_y + i
            ], fill=color)

        # Add character silhouette
        self._draw_character_silhouette(draw, width, height, description)

        # Add text overlay
        self._add_text_overlay(draw, width, height, "CHARACTER", description)

        # Apply artistic effects
        img = self._apply_artistic_effects(img)

        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=95)
        return buffer.getvalue()

    def _generate_enhanced_fallback_background(self, description: str) -> bytes:
        """Generate enhanced background placeholder."""
        width = self.ai_settings.get('IMAGE_WIDTH', 512)
        height = self.ai_settings.get('IMAGE_HEIGHT', 512)

        # Create landscape-style background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        # Sky gradient
        if 'space' in description.lower():
            self._draw_space_background(draw, width, height)
        elif 'forest' in description.lower():
            self._draw_forest_background(draw, width, height)
        elif 'castle' in description.lower():
            self._draw_castle_background(draw, width, height)
        else:
            self._draw_generic_landscape(draw, width, height)

        # Add atmospheric effects
        img = self._add_atmospheric_effects(img, description)

        # Add text overlay
        self._add_text_overlay(draw, width, height, "BACKGROUND", description)

        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=95)
        return buffer.getvalue()

    def _draw_character_silhouette(self, draw, width, height, description):
        """Draw character silhouette based on description."""
        center_x, center_y = width // 2, height // 2

        # Simple human silhouette
        # Head
        draw.ellipse([
            center_x - 30, center_y - 60,
            center_x + 30, center_y - 0
        ], fill=(50, 50, 50, 128))

        # Body
        draw.rectangle([
            center_x - 25, center_y,
            center_x + 25, center_y + 80
        ], fill=(60, 60, 60, 128))

        # Arms
        draw.rectangle([
            center_x - 45, center_y + 10,
            center_x - 25, center_y + 60
        ], fill=(55, 55, 55, 128))

        draw.rectangle([
            center_x + 25, center_y + 10,
            center_x + 45, center_y + 60
        ], fill=(55, 55, 55, 128))

        # Legs
        draw.rectangle([
            center_x - 20, center_y + 80,
            center_x - 5, center_y + 140
        ], fill=(55, 55, 55, 128))

        draw.rectangle([
            center_x + 5, center_y + 80,
            center_x + 20, center_y + 140
        ], fill=(55, 55, 55, 128))

    def _draw_space_background(self, draw, width, height):
        """Draw space-themed background."""
        # Dark space background
        for y in range(height):
            color_intensity = int(20 + (y / height) * 40)
            draw.line([(0, y), (width, y)], fill=(color_intensity, color_intensity, color_intensity + 20))

        # Add stars
        import random
        for _ in range(50):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, brightness))

    def _draw_forest_background(self, draw, width, height):
        """Draw forest-themed background."""
        # Green gradient for trees
        for y in range(height):
            green_intensity = int(80 + (y / height) * 100)
            draw.line([(0, y), (width, y)], fill=(40, green_intensity, 40))

        # Simple tree shapes
        import random
        for _ in range(8):
            x = random.randint(0, width)
            tree_height = random.randint(height // 3, height)
            tree_width = random.randint(20, 40)
            draw.ellipse([
                x - tree_width // 2, height - tree_height,
                x + tree_width // 2, height
            ], fill=(30, 60, 30))

    def _draw_castle_background(self, draw, width, height):
        """Draw castle-themed background."""
        # Sky gradient
        for y in range(height // 2):
            blue_intensity = int(150 + (y / (height // 2)) * 100)
            draw.line([(0, y), (width, y)], fill=(blue_intensity, blue_intensity, 255))

        # Ground
        for y in range(height // 2, height):
            green_intensity = int(100 - ((y - height // 2) / (height // 2)) * 50)
            draw.line([(0, y), (width, y)], fill=(green_intensity, green_intensity + 20, green_intensity // 2))

        # Simple castle silhouette
        castle_width = width // 3
        castle_height = height // 2
        castle_x = width // 2 - castle_width // 2
        castle_y = height // 2

        draw.rectangle([
            castle_x, castle_y,
            castle_x + castle_width, castle_y + castle_height
        ], fill=(100, 100, 100))

        # Towers
        for i in range(3):
            tower_x = castle_x + i * castle_width // 3
            draw.rectangle([
                tower_x, castle_y - 20,
                tower_x + 30, castle_y + castle_height
            ], fill=(80, 80, 80))

    def _draw_generic_landscape(self, draw, width, height):
        """Draw generic landscape background."""
        # Sky gradient
        for y in range(height // 2):
            color_intensity = int(200 - (y / (height // 2)) * 100)
            draw.line([(0, y), (width, y)], fill=(color_intensity, color_intensity + 20, color_intensity + 40))

        # Ground
        for y in range(height // 2, height):
            green_intensity = int(120 + ((y - height // 2) / (height // 2)) * 60)
            draw.line([(0, y), (width, y)], fill=(green_intensity - 40, green_intensity, green_intensity - 60))

    def _add_text_overlay(self, draw, width, height, label, description):
        """Add text overlay to image."""
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()

        # Add label
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        text_y = 20

        # Text shadow
        draw.text((text_x + 2, text_y + 2), label, font=font, fill=(0, 0, 0, 180))
        draw.text((text_x, text_y), label, font=font, fill=(255, 255, 255))

        # Add description snippet
        desc_snippet = description[:50] + "..." if len(description) > 50 else description
        try:
            small_font = ImageFont.truetype("arial.ttf", 12)
        except:
            small_font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), desc_snippet, font=small_font)
        desc_width = bbox[2] - bbox[0]
        desc_x = (width - desc_width) // 2
        desc_y = height - 40

        draw.text((desc_x + 1, desc_y + 1), desc_snippet, font=small_font, fill=(0, 0, 0, 180))
        draw.text((desc_x, desc_y), desc_snippet, font=small_font, fill=(255, 255, 255))

    def _apply_artistic_effects(self, img):
        """Apply artistic effects to enhance the image."""
        # Slight blur for artistic effect
        img = img.filter(ImageFilter.GaussianBlur(0.5))

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)

        # Enhance color
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)

        return img

    def _add_atmospheric_effects(self, img, description):
        """Add atmospheric effects based on description."""
        if 'mystical' in description.lower() or 'magic' in description.lower():
            # Add purple tint
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.3)
        elif 'dramatic' in description.lower():
            # Increase contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.4)

        return img

class EnhancedImageComposer:
    """Enhanced image composer with better blending."""

    def __init__(self):
        self.ai_settings = getattr(settings, 'AI_MODELS', {})

    def compose_images(self, char_image_path: str, bg_image_path: str) -> bytes:
        """Compose character and background with advanced blending."""
        try:
            # Load images
            char_img = Image.open(char_image_path).convert('RGBA')
            bg_img = Image.open(bg_image_path).convert('RGBA')

            # Resize for composition
            bg_width, bg_height = bg_img.size

            # Resize character to be proportional
            char_scale = 0.6  # Character takes 60% of background height
            char_height = int(bg_height * char_scale)
            char_width = int(char_img.size[0] * (char_height / char_img.size[1]))
            char_img = char_img.resize((char_width, char_height), Image.Resampling.LANCZOS)

            # Position character (slightly right of center, bottom aligned)
            char_x = int(bg_width * 0.6) - char_width // 2
            char_y = bg_height - char_height

            # Create composition
            final_img = bg_img.copy()

            # Create soft edge mask for character
            char_mask = Image.new('L', char_img.size, 0)
            mask_draw = ImageDraw.Draw(char_mask)
            mask_draw.ellipse([0, 0, char_img.size[0], char_img.size[1]], fill=255)
            char_mask = char_mask.filter(ImageFilter.GaussianBlur(2))

            # Composite with mask
            final_img.paste(char_img, (char_x, char_y), char_mask)

            # Apply final effects
            final_img = self._apply_composition_effects(final_img)

            # Convert to bytes
            buffer = BytesIO()
            final_img.convert('RGB').save(buffer, format='PNG', quality=95)
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Image composition failed: {e}")
            return self._create_error_placeholder()

    def _apply_composition_effects(self, img):
        """Apply final composition effects."""
        # Slight vignette effect
        width, height = img.size
        vignette = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        vignette_draw = ImageDraw.Draw(vignette)

        # Create vignette gradient
        center_x, center_y = width // 2, height // 2
        max_distance = min(width, height) // 2

        for radius in range(max_distance, 0, -5):
            alpha = int((radius / max_distance) * 30)
            vignette_draw.ellipse([
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius
            ], outline=(0, 0, 0, alpha))

        # Apply vignette
        img = Image.alpha_composite(img, vignette)

        return img

    def _create_error_placeholder(self):
        """Create error placeholder."""
        img = Image.new('RGB', (512, 512), (100, 100, 100))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()

        text = "COMPOSED SCENE"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (512 - text_width) // 2
        y = (512 - text_height) // 2

        draw.text((x, y), text, font=font, fill=(255, 255, 255))

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
