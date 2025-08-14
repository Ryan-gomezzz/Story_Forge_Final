"""
Enhanced story engine with template-based generation - no AI conflicts.
"""
import random

class EnhancedStoryEngine:
    """Enhanced story generator using advanced templates."""

    def __init__(self, ai_settings=None):
        # Don't initialize AI models to avoid template conflicts
        self.ai_settings = ai_settings or {}

    def generate_story(self, prompt):
        """Generate an enhanced story using templates."""
        # Determine story elements
        genre = self._detect_genre(prompt)
        setting = self._extract_setting(prompt)
        character = self._extract_character(prompt)

        # Get appropriate template
        template = self._get_story_template(genre)

        # Generate story elements
        conflict = self._generate_conflict(genre)
        resolution = self._generate_resolution(genre)

        # Fill template
        story = template.format(
            prompt=prompt,
            character=character,
            setting=setting,
            conflict=conflict,
            resolution=resolution
        )

        return story

    def _detect_genre(self, prompt):
        """Detect story genre from prompt."""
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ['wizard', 'magic', 'dragon', 'knight', 'fantasy']):
            return 'fantasy'
        elif any(word in prompt_lower for word in ['space', 'alien', 'robot', 'future', 'sci-fi']):
            return 'sci-fi'
        elif any(word in prompt_lower for word in ['mystery', 'detective', 'crime']):
            return 'mystery'
        elif any(word in prompt_lower for word in ['love', 'romance']):
            return 'romance'
        else:
            return 'adventure'

    def _extract_setting(self, prompt):
        """Extract setting from prompt."""
        prompt_lower = prompt.lower()

        if 'forest' in prompt_lower:
            return "an ancient, mystical forest where sunlight filters through emerald canopies"
        elif 'castle' in prompt_lower:
            return "a magnificent castle perched high on a cliff"
        elif 'space' in prompt_lower:
            return "the vast expanse of space with distant galaxies"
        elif 'city' in prompt_lower:
            return "a bustling metropolis with towering skyscrapers"
        else:
            return "a realm where adventure awaits at every turn"

    def _extract_character(self, prompt):
        """Extract character from prompt."""
        prompt_lower = prompt.lower()

        if 'knight' in prompt_lower:
            return "Sir Aldric, a noble knight whose courage was legendary"
        elif 'wizard' in prompt_lower:
            return "Eldara the Wise, an ancient wizard with mystical powers"
        elif 'explorer' in prompt_lower:
            return "Captain Nova, a fearless explorer"
        else:
            return "our brave protagonist"

    def _get_story_template(self, genre):
        """Get story template for genre."""
        templates = {
            'fantasy': """In {setting}, {character} discovered something extraordinary that would change their destiny forever. What began as {prompt} evolved into an epic quest that would test every fiber of their being.

The ancient prophecies spoke of a chosen one, but none had imagined it would be someone so unlikely yet so determined. As dawn broke over the mystical landscape, {character} felt the weight of destiny settling upon their shoulders.

The journey ahead would lead through enchanted forests where trees whispered ancient secrets, across treacherous mountain passes guarded by creatures of legend, and into the heart of challenges that would forge a true hero.

Along the way, they encountered wise companions who became lifelong allies, each bringing unique skills and perspectives to their growing fellowship. Together, they faced trials that tested not only their individual strengths but their ability to work as one united force.

When {conflict} reached its climax, {character} discovered that true magic came not from external sources, but from the courage, compassion, and determination that had been growing within them all along.

{resolution} And so, {character} returned home forever changed, carrying within them the knowledge that even the most ordinary person can achieve extraordinary things when they have the courage to take the first step into adventure.""",

            'sci-fi': """The year 2387 brought unprecedented changes to human civilization, and {character} found themselves at the center of discoveries that would reshape humanity's understanding of the universe. What started as {prompt} had evolved into first contact with implications beyond imagination.

{setting} had become the staging ground for humanity's greatest challenge and opportunity. The mysterious signals detected by deep space monitoring stations revealed patterns of intelligence that both thrilled and terrified the scientific community.

{character} assembled a diverse team of specialists, each bringing crucial expertise to their mission. Together, they ventured into regions of space where the laws of physics seemed to bend and reality itself became malleable.

The journey revealed wonders beyond description: wormholes that defied conventional understanding, planets with impossible geometries, and energy signatures that rewrote the textbooks of science. Each discovery challenged fundamental assumptions about the nature of existence.

When {conflict} reached its critical moment, {character} realized that success would require not just technological advancement, but a fundamental shift in how humanity understood its place in the cosmic community.

{resolution} The mission's outcome established humanity as part of a greater galactic civilization, opening doors to knowledge and experiences that would guide the species toward a future bright with possibility.""",

            'adventure': """The ancient map had been gathering dust for decades, but when {character} first examined it, they knew their life was about to change dramatically. What began as {prompt} quickly became the adventure of a lifetime in {setting}.

The quest would test every survival skill and challenge every assumption about what was possible. {character} assembled a team of experts, each bringing unique talents that would prove essential to their success.

Their journey took them through some of Earth's most challenging environments, from scorching deserts where mirages played tricks on the mind to frozen peaks where one wrong step meant certain death. Each location presented obstacles that required not just physical endurance, but creative problem-solving and unwavering teamwork.

They were not alone in their quest. {conflict} turned their expedition into a race against time and adversaries who would stop at nothing to claim the prize for themselves.

The discovery, when it finally came, exceeded all expectations. Hidden in places that defied explanation, they found treasures that would rewrite history and challenge everything scholars thought they knew about human civilization.

{resolution} As they emerged with proof of their incredible discovery, {character} realized that the real treasure had been the journey itself—the friendships forged, the limits overcome, and the knowledge that courage and determination can unlock the world's greatest mysteries."""
        }

        return templates.get(genre, templates['adventure'])

    def _generate_conflict(self, genre):
        """Generate conflict for genre."""
        conflicts = {
            'fantasy': "an ancient evil stirred from its slumber, threatening to plunge the world into eternal darkness",
            'sci-fi': "hostile alien forces that tested humanity's resolve and ingenuity",
            'adventure': "rival expeditions and natural disasters that threatened to end their quest",
            'mystery': "a web of deception that reached into the highest levels of power",
            'romance': "misunderstandings and obstacles that seemed impossible to overcome"
        }
        return conflicts.get(genre, conflicts['adventure'])

    def _generate_resolution(self, genre):
        """Generate resolution for genre."""
        resolutions = {
            'fantasy': "Through courage, wisdom, and friendship, balance was restored to the realm",
            'sci-fi': "Humanity earned its place among the stars through diplomacy and understanding",
            'adventure': "They proved that the greatest treasures are the bonds forged through shared challenges",
            'mystery': "Justice prevailed, revealing truths that changed everything",
            'romance': "Love conquered all obstacles, proving that true hearts always find a way"
        }
        return resolutions.get(genre, resolutions['adventure'])

    def extract_character_description(self, story):
        """Extract character description."""
        story_lower = story.lower()

        if 'knight' in story_lower:
            return "A noble knight in gleaming armor with determined blue eyes and a crimson cloak"
        elif 'wizard' in story_lower:
            return "An elderly wizard with silver robes, white beard, and a crystal-topped staff"
        elif 'space' in story_lower:
            return "A space explorer in advanced uniform with technological interfaces"
        else:
            return "A brave adventurer with practical gear and determined expression"

    def extract_background_description(self, story):
        """Extract background description."""
        story_lower = story.lower()

        if 'forest' in story_lower:
            return "An enchanted forest with towering trees and magical atmosphere"
        elif 'castle' in story_lower:
            return "A majestic castle on a cliff with dramatic sky"
        elif 'space' in story_lower:
            return "The vastness of space with stars and distant galaxies"
        else:
            return "A dramatic landscape perfect for adventure"
