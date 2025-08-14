import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os

logger = logging.getLogger(__name__)

# Try to import GPU libraries
try:
    import torch
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    GPU_AVAILABLE = torch.cuda.is_available()
except ImportError:
    GPU_AVAILABLE = False

class GPUImageGenerator:
    """Generate high-quality images with much better prompts."""
    
    def __init__(self, ai_settings=None):
        self.ai_settings = ai_settings or {}
        self.device = "cuda" if GPU_AVAILABLE else "cpu"
        self.pipeline = None
        self.available = GPU_AVAILABLE
        
        if self.available:
            logger.info(f"GPU Image Generator - Device: {self.device}")
        else:
            logger.warning("GPU not available, using enhanced fallbacks")
    
    def _load_pipeline(self, style='realistic'):
        """Load Stable Diffusion pipeline with optimizations."""
        if not self.available:
            return False
            
        try:
            if self.pipeline is None:
                logger.info("Loading Stable Diffusion model...")
                
                # Use a better model
                model_id = "stabilityai/stable-diffusion-2-1"
                
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    safety_checker=None,
                    requires_safety_checker=False,
                    use_safetensors=False
                ).to(self.device)
                
                # Better scheduler
                self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                    self.pipeline.scheduler.config
                )
                
                if self.device == "cuda":
                    self.pipeline.enable_attention_slicing()
                    try:
                        self.pipeline.enable_xformers_memory_efficient_attention()
                    except:
                        pass
                
                logger.info("✅ Stable Diffusion model loaded successfully!")
                    
            return True
        except Exception as e:
            logger.error(f"Failed to load pipeline: {e}")
            return False
    
    def generate_character_image(self, description: str, style: str = 'realistic') -> bytes:
        """Generate character image with much better prompts."""
        if self.available and self._load_pipeline(style):
            try:
                # MUCH BETTER PROMPTS
                enhanced_prompt = self._create_enhanced_character_prompt(description, style)
                negative_prompt = self._get_detailed_negative_prompt('character')
                
                logger.info(f"Generating character with prompt: {enhanced_prompt[:100]}...")
                
                with torch.autocast(self.device):
                    result = self.pipeline(
                        enhanced_prompt,
                        negative_prompt=negative_prompt,
                        num_inference_steps=25,  # More steps = better quality
                        guidance_scale=8.5,      # Higher guidance = better adherence to prompt
                        width=512,
                        height=512,
                        generator=torch.Generator(device=self.device).manual_seed(42)
                    )
                
                # Post-process for better quality
                image = self._enhance_image(result.images[0])
                
                buffer = BytesIO()
                image.save(buffer, format='PNG', quality=95)
                logger.info("✅ Character image generated successfully!")
                return buffer.getvalue()
                
            except Exception as e:
                logger.error(f"GPU character generation failed: {e}")
        
        # Better fallback
        return self._create_artistic_character_placeholder(description)
    
    def generate_background_image(self, description: str, style: str = 'realistic') -> bytes:
        """Generate background with much better prompts."""
        if self.available and self._load_pipeline(style):
            try:
                enhanced_prompt = self._create_enhanced_background_prompt(description, style)
                negative_prompt = self._get_detailed_negative_prompt('background')
                
                logger.info(f"Generating background with prompt: {enhanced_prompt[:100]}...")
                
                with torch.autocast(self.device):
                    result = self.pipeline(
                        enhanced_prompt,
                        negative_prompt=negative_prompt,
                        num_inference_steps=25,
                        guidance_scale=8.0,
                        width=768,
                        height=512,
                        generator=torch.Generator(device=self.device).manual_seed(123)
                    )
                
                image = self._enhance_image(result.images[0])
                
                buffer = BytesIO()
                image.save(buffer, format='PNG', quality=95)
                logger.info("✅ Background image generated successfully!")
                return buffer.getvalue()
                
            except Exception as e:
                logger.error(f"GPU background generation failed: {e}")
        
        return self._create_artistic_background_placeholder(description)
    
    def _create_enhanced_character_prompt(self, description: str, style: str) -> str:
        """Create much better character prompts."""
        # Extract key elements from description
        character_type = self._identify_character_type(description)
        
        base_prompts = {
            'knight': "medieval knight in detailed armor, heroic pose, cinematic lighting, fantasy art, highly detailed, 8k resolution, masterpiece",
            'wizard': "powerful wizard with magical robes, mystical staff, arcane symbols, fantasy art, dramatic lighting, highly detailed, 8k",
            'space': "futuristic space explorer, sci-fi uniform, advanced technology, cyberpunk style, detailed, high quality, 8k resolution",
            'detective': "noir detective, 1940s style, dramatic shadows, film noir lighting, highly detailed portrait, cinematic quality",
            'adventurer': "rugged adventurer, practical gear, outdoor setting, action pose, realistic style, highly detailed, 8k resolution"
        }
        
        base_prompt = base_prompts.get(character_type, base_prompts['adventurer'])
        
        style_modifiers = {
            'realistic': "photorealistic, professional photography, studio lighting, sharp focus, detailed textures",
            'artistic': "digital art, concept art, trending on artstation, painted style, artistic lighting",
            'fantasy': "fantasy art, magical atmosphere, ethereal lighting, mystical style, enchanted"
        }
        
        style_mod = style_modifiers.get(style, style_modifiers['realistic'])
        
        return f"{base_prompt}, {description}, {style_mod}"
    
    def _create_enhanced_background_prompt(self, description: str, style: str) -> str:
        """Create much better background prompts."""
        setting_type = self._identify_setting_type(description)
        
        base_prompts = {
            'forest': "ancient mystical forest, towering trees, dappled sunlight, moss-covered ground, magical atmosphere, highly detailed landscape, 8k",
            'castle': "majestic medieval castle, stone towers, dramatic sky, epic landscape, fortress on hill, cinematic composition, 8k resolution",
            'space': "cosmic space scene, nebula, stars, galaxies, deep space, astronomical photography, highly detailed, 8k resolution",
            'city': "futuristic cityscape, skyscrapers, neon lights, cyberpunk atmosphere, urban landscape, detailed architecture, 8k",
            'mountain': "epic mountain landscape, dramatic peaks, golden hour lighting, majestic scenery, nature photography, 8k resolution"
        }
        
        base_prompt = base_prompts.get(setting_type, base_prompts['mountain'])
        
        style_modifiers = {
            'realistic': "landscape photography, natural lighting, photorealistic, high detail, sharp focus",
            'artistic': "digital matte painting, concept art, artistic interpretation, painted style",
            'fantasy': "fantasy landscape, magical lighting, ethereal atmosphere, mystical environment"
        }
        
        style_mod = style_modifiers.get(style, style_modifiers['realistic'])
        
        return f"{base_prompt}, {description}, {style_mod}"
    
    def _get_detailed_negative_prompt(self, image_type: str) -> str:
        """Detailed negative prompts to avoid common issues."""
        base_negative = "blurry, low quality, pixelated, distorted, ugly, deformed, bad anatomy, extra limbs, missing limbs, bad proportions, watermark, signature, text, username, logo, copyright, low resolution, jpeg artifacts, noise, grain"
        
        if image_type == 'character':
            return f"{base_negative}, multiple people, crowd, background objects, vehicles, buildings, landscape"
        else:  # background
            return f"{base_negative}, people, person, human, character, face, portrait, animals"
    
    def _identify_character_type(self, description: str) -> str:
        """Identify character type from description."""
        desc_lower = description.lower()
        if any(word in desc_lower for word in ['knight', 'armor', 'sword', 'medieval']):
            return 'knight'
        elif any(word in desc_lower for word in ['wizard', 'mage', 'magic', 'staff', 'robes']):
            return 'wizard'
        elif any(word in desc_lower for word in ['space', 'sci-fi', 'futuristic', 'cyberpunk']):
            return 'space'
        elif any(word in desc_lower for word in ['detective', 'noir', 'investigator']):
            return 'detective'
        else:
            return 'adventurer'
    
    def _identify_setting_type(self, description: str) -> str:
        """Identify setting type from description."""
        desc_lower = description.lower()
        if any(word in desc_lower for word in ['forest', 'tree', 'woods', 'jungle']):
            return 'forest'
        elif any(word in desc_lower for word in ['castle', 'fortress', 'tower', 'medieval']):
            return 'castle'
        elif any(word in desc_lower for word in ['space', 'cosmic', 'galaxy', 'nebula']):
            return 'space'
        elif any(word in desc_lower for word in ['city', 'urban', 'building', 'street']):
            return 'city'
        else:
            return 'mountain'
    
    def _enhance_image(self, image: Image.Image) -> Image.Image:
        """Post-process image for better quality."""
        try:
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            # Enhance color
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.05)
            
            return image
        except Exception as e:
            logger.warning(f"Image enhancement failed: {e}")
            return image
    
    def compose_images(self, char_path: str, bg_path: str) -> bytes:
        """Better image composition."""
        try:
            char_img = Image.open(char_path).convert('RGBA')
            bg_img = Image.open(bg_path).convert('RGBA')
            
            # Better scaling and positioning
            bg_width, bg_height = bg_img.size
            char_scale = 0.8
            char_height = int(bg_height * char_scale)
            char_width = int(char_img.size[0] * (char_height / char_img.size[1]))
            char_img = char_img.resize((char_width, char_height), Image.Resampling.LANCZOS)
            
            # Better positioning
            char_x = int(bg_width * 0.25)
            char_y = bg_height - char_height
            
            # Create composition
            final_img = bg_img.copy()
            final_img.paste(char_img, (char_x, char_y), char_img)
            
            buffer = BytesIO()
            final_img.convert('RGB').save(buffer, format='PNG', quality=95)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Composition failed: {e}")
            return self._create_placeholder("COMPOSED SCENE", 768, 512)
    
    def _create_artistic_character_placeholder(self, description: str) -> bytes:
        """Much better character placeholder."""
        img = Image.new('RGB', (512, 512))
        draw = ImageDraw.Draw(img)
        
        # Beautiful gradient background
        for y in range(512):
            r = int(70 + (y / 512) * 100)
            g = int(90 + (y / 512) * 120)  
            b = int(140 + (y / 512) * 100)
            draw.line([(0, y), (512, y)], fill=(r, g, b))
        
        # Better character silhouette
        center_x, center_y = 256, 300
        
        # Head
        draw.ellipse([center_x-50, center_y-100, center_x+50, center_y-10], fill=(40, 40, 50))
        # Body
        draw.rectangle([center_x-40, center_y-10, center_x+40, center_y+120], fill=(50, 50, 60))
        # Arms
        draw.rectangle([center_x-70, center_y+20, center_x-40, center_y+100], fill=(45, 45, 55))
        draw.rectangle([center_x+40, center_y+20, center_x+70, center_y+100], fill=(45, 45, 55))
        
        # Better text
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()
        
        draw.text((100, 450), "AI CHARACTER", font=font, fill=(255, 255, 255))
        draw.text((150, 480), "(Loading...)", font=font, fill=(200, 200, 200))
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _create_artistic_background_placeholder(self, description: str) -> bytes:
        """Much better background placeholder."""
        img = Image.new('RGB', (768, 512))
        draw = ImageDraw.Draw(img)
        
        # Beautiful sky gradient
        for y in range(256):
            r = int(135 + (y / 256) * 100)
            g = int(206 + (y / 256) * 40)
            b = int(235 - (y / 256) * 100)
            draw.line([(0, y), (768, y)], fill=(r, g, b))
        
        # Ground gradient
        for y in range(256, 512):
            progress = (y - 256) / 256
            r = int(60 + progress * 80)
            g = int(120 + progress * 60)
            b = int(40 + progress * 20)
            draw.line([(0, y), (768, y)], fill=(r, g, b))
        
        # Add some simple landscape elements
        # Mountains
        points = [(0, 200), (150, 120), (300, 180), (450, 100), (600, 160), (768, 140), (768, 256), (0, 256)]
        draw.polygon(points, fill=(80, 80, 120))
        
        # Better text
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        draw.text((250, 200), "AI BACKGROUND", font=font, fill=(255, 255, 255))
        draw.text((300, 250), "(Loading...)", font=font, fill=(220, 220, 220))
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def _create_placeholder(self, text: str, width: int, height: int) -> bytes:
        """Basic placeholder."""
        img = Image.new('RGB', (width, height), (120, 120, 120))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), text, font=font, fill=(255, 255, 255))
        except:
            pass
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def get_available_styles(self):
        """Get available styles."""
        return ['realistic', 'artistic', 'fantasy']
    
    def cleanup(self):
        """Cleanup GPU memory."""
        if self.available and hasattr(torch.cuda, 'empty_cache'):
            torch.cuda.empty_cache()

def check_gpu_requirements():
    """Check GPU status."""
    return {
        'cuda_available': GPU_AVAILABLE,
        'gpu_count': torch.cuda.device_count() if GPU_AVAILABLE else 0,
        'diffusers_available': 'diffusers' in globals(),
        'gpu_name': torch.cuda.get_device_name(0) if GPU_AVAILABLE else "None",
        'memory_gb': torch.cuda.get_device_properties(0).total_memory / (1024**3) if GPU_AVAILABLE else 0
    }