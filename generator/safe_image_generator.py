"""
Safe image generator that avoids AI model conflicts in Django templates.
"""
import os
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

class SafeImageGenerator:
    """Safe image generator that works without AI model conflicts."""

    def __init__(self):
        self.colors = [
            (135, 206, 235),  # Sky blue
            (60, 179, 113),   # Medium sea green
            (255, 165, 0),    # Orange
            (147, 112, 219),  # Medium purple
            (220, 20, 60),    # Crimson
            (255, 215, 0),    # Gold
            (46, 125, 50),    # Dark green
            (63, 81, 181),    # Indigo
        ]

    def generate_character_image(self, description):
        """Generate enhanced character image."""
        width, height = 512, 512

        # Choose colors based on character type
        if 'knight' in description.lower():
            colors = [(70, 70, 120), (120, 120, 180), (180, 180, 220)]
        elif 'wizard' in description.lower():
            colors = [(80, 40, 120), (140, 80, 180), (200, 160, 240)]
        elif 'space' in description.lower():
            colors = [(20, 20, 60), (60, 80, 140), (100, 140, 200)]
        else:
            colors = [(100, 120, 80), (140, 180, 120), (180, 220, 160)]

        # Create radial gradient background
        img = Image.new('RGB', (width, height), colors[0])
        draw = ImageDraw.Draw(img)

        # Create gradient effect
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

        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=95)
        return buffer.getvalue()

    def generate_background_image(self, description):
        """Generate enhanced background image."""
        width, height = 512, 512

        # Create landscape-style background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        # Choose background type based on description
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

        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG', quality=95)
        return buffer.getvalue()

    def compose_images(self, char_image_path, bg_image_path):
        """Compose character and background images."""
        try:
            # Load images
            char_img = Image.open(char_image_path).convert('RGBA')
            bg_img = Image.open(bg_image_path).convert('RGBA')

            # Resize for composition
            bg_width, bg_height = bg_img.size

            # Resize character to be proportional
            char_scale = 0.6
            char_height = int(bg_height * char_scale)
            char_width = int(char_img.size[0] * (char_height / char_img.size[1]))
            char_img = char_img.resize((char_width, char_height), Image.Resampling.LANCZOS)

            # Position character
            char_x = int(bg_width * 0.6) - char_width // 2
            char_y = bg_height - char_height

            # Create composition
            final_img = bg_img.copy()

            # Create soft edge mask
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
            return self._create_error_placeholder()

    def _draw_character_silhouette(self, draw, width, height, description):
        """Draw simple character silhouette."""
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

    def _draw_space_background(self, draw, width, height):
        """Draw space-themed background."""
        # Dark space background with gradient
        for y in range(height):
            color_intensity = int(20 + (y / height) * 40)
            draw.line([(0, y), (width, y)], fill=(color_intensity, color_intensity, color_intensity + 20))

        # Add stars
        for _ in range(50):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, brightness))

    def _draw_forest_background(self, draw, width, height):
        """Draw forest-themed background."""
        # Green gradient
        for y in range(height):
            green_intensity = int(80 + (y / height) * 100)
            draw.line([(0, y), (width, y)], fill=(40, green_intensity, 40))

        # Simple tree shapes
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

        # Simple castle
        castle_width = width // 3
        castle_height = height // 2
        castle_x = width // 2 - castle_width // 2
        castle_y = height // 2

        draw.rectangle([
            castle_x, castle_y,
            castle_x + castle_width, castle_y + castle_height
        ], fill=(100, 100, 100))

    def _draw_generic_landscape(self, draw, width, height):
        """Draw generic landscape."""
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

    def _apply_artistic_effects(self, img):
        """Apply artistic effects."""
        # Slight blur
        img = img.filter(ImageFilter.GaussianBlur(0.5))

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)

        return img

    def _add_atmospheric_effects(self, img, description):
        """Add atmospheric effects."""
        if 'mystical' in description.lower() or 'magic' in description.lower():
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.3)

        return img

    def _apply_composition_effects(self, img):
        """Apply composition effects."""
        # Simple vignette
        width, height = img.size
        vignette = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        vignette_draw = ImageDraw.Draw(vignette)

        center_x, center_y = width // 2, height // 2
        max_distance = min(width, height) // 2

        for radius in range(max_distance, 0, -5):
            alpha = int((radius / max_distance) * 30)
            vignette_draw.ellipse([
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius
            ], outline=(0, 0, 0, alpha))

        return Image.alpha_composite(img, vignette)

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
