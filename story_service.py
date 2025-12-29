"""
Story Generation Service - Uses Google Gemini for cultural storytelling
"""
import os
from typing import Optional

# Try new google-genai first, fall back to legacy
try:
    from google import genai
    USE_NEW_API = True
except ImportError:
    import google.generativeai as genai
    USE_NEW_API = False


# Cultural knowledge embedded in prompts
CULTURAL_CONTEXTS = {
    "indian": {
        "elements": "Include elements like dharma, karma, ancient wisdom, moral lessons, festivals, deities, or village life.",
        "style": "Use poetic language with metaphors from nature, rivers, and mountains.",
        "examples": "Panchatantra, Jataka Tales, Ramayana, Mahabharata stories"
    },
    "japanese": {
        "elements": "Include elements like honor, nature spirits (kami), seasonal beauty, zen philosophy, or yokai.",
        "style": "Use concise, contemplative language with references to cherry blossoms, moon, and mountains.",
        "examples": "Momotaro, Urashima Taro, Kaguya-hime, Tanuki tales"
    },
    "african": {
        "elements": "Include elements like community wisdom, animal tricksters (Anansi), ancestral spirits, and nature.",
        "style": "Use vibrant, rhythmic storytelling with proverbs and call-and-response patterns.",
        "examples": "Anansi stories, Why the Sun and Moon Live in the Sky, The Tortoise tales"
    },
    "celtic": {
        "elements": "Include elements like faeries, druids, ancient magic, heroic quests, and sacred groves.",
        "style": "Use mystical, lyrical language with references to mist, standing stones, and otherworldly realms.",
        "examples": "Cu Chulainn, The Morrigan, Selkie tales, Leprechaun legends"
    },
    "chinese": {
        "elements": "Include elements like dragons, filial piety, yin-yang balance, immortals, and the Jade Emperor.",
        "style": "Use elegant prose with references to mountains, rivers, and celestial beings.",
        "examples": "Journey to the West, White Snake, Monkey King, Moon Goddess"
    },
    "greek": {
        "elements": "Include elements like gods of Olympus, heroes, quests, hubris, and fate.",
        "style": "Use epic, dramatic language with references to mythology and ancient wisdom.",
        "examples": "Odyssey, Hercules' labors, Perseus, Theseus and the Minotaur"
    },
    "arabian": {
        "elements": "Include elements like djinn, magic lamps, desert wisdom, merchants, and caliphs.",
        "style": "Use rich, ornate language with references to stars, oases, and ancient cities.",
        "examples": "One Thousand and One Nights, Aladdin, Sinbad, Ali Baba"
    },
    "native_american": {
        "elements": "Include elements like animal spirits, creation stories, harmony with nature, and vision quests.",
        "style": "Use reverent language honoring earth, sky, and all living beings.",
        "examples": "Coyote tales, Raven stories, The Rainbow Crow, How the Earth Was Made"
    }
}


def get_cultural_context(culture: str) -> dict:
    """Get cultural context for storytelling."""
    culture_lower = culture.lower().replace(" ", "_")
    return CULTURAL_CONTEXTS.get(culture_lower, CULTURAL_CONTEXTS["indian"])


def initialize_gemini(api_key: Optional[str] = None):
    """Initialize the Gemini API."""
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in environment variables.")
    
    if USE_NEW_API:
        # New google-genai package
        client = genai.Client(api_key=key)
        return client
    else:
        # Legacy google-generativeai package
        genai.configure(api_key=key)
        return genai.GenerativeModel('gemini-1.5-flash')


def generate_story(prompt: str, culture: str = "indian", model=None) -> dict:
    """
    Generate a cultural story based on the prompt.
    
    Returns:
        dict with 'title', 'story', 'scenes' (for video generation)
    """
    if model is None:
        model = initialize_gemini()
    
    context = get_cultural_context(culture)
    
    system_prompt = f"""You are a master storyteller specializing in {culture} cultural tales.
    
Cultural Guidelines:
- {context['elements']}
- {context['style']}
- Draw inspiration from: {context['examples']}

Create an engaging, immersive story that:
1. Has a clear beginning, middle, and end
2. Includes vivid descriptions and cultural authenticity
3. Teaches a meaningful lesson or moral
4. Is suitable for all ages
5. Is approximately 300-500 words

Format your response EXACTLY as follows:
TITLE: [Story Title]

STORY:
[The complete story text]

SCENES:
1. [Brief description of scene 1 - for video visualization]
2. [Brief description of scene 2 - for video visualization]
3. [Brief description of scene 3 - for video visualization]
4. [Brief description of scene 4 - for video visualization]
5. [Brief description of scene 5 - for video visualization]

MORAL: [The lesson or moral of the story]
"""
    
    full_prompt = f"{system_prompt}\n\nUser's story idea: {prompt}"
    
    try:
        if USE_NEW_API:
            # New google-genai package - model is actually a Client
            response = model.models.generate_content(
                model='gemini-1.5-flash',
                contents=full_prompt
            )
            text = response.text
        else:
            # Legacy google-generativeai package
            response = model.generate_content(full_prompt)
            text = response.text
        
        # Parse the response
        result = parse_story_response(text)
        result['culture'] = culture
        return result
        
    except Exception as e:
        return {
            "title": "Story Generation Error",
            "story": f"Unable to generate story: {str(e)}",
            "scenes": [],
            "moral": "",
            "culture": culture,
            "error": True
        }


def parse_story_response(text: str) -> dict:
    """Parse the structured story response from Gemini."""
    result = {
        "title": "Untitled Story",
        "story": "",
        "scenes": [],
        "moral": ""
    }
    
    lines = text.strip().split('\n')
    current_section = None
    story_lines = []
    
    for line in lines:
        line_stripped = line.strip()
        
        if line_stripped.startswith("TITLE:"):
            result["title"] = line_stripped.replace("TITLE:", "").strip()
        elif line_stripped == "STORY:":
            current_section = "story"
        elif line_stripped == "SCENES:":
            current_section = "scenes"
        elif line_stripped.startswith("MORAL:"):
            result["moral"] = line_stripped.replace("MORAL:", "").strip()
            current_section = None
        elif current_section == "story" and line_stripped:
            story_lines.append(line)
        elif current_section == "scenes" and line_stripped:
            # Remove numbering like "1. ", "2. "
            scene = line_stripped
            if len(scene) > 2 and scene[0].isdigit() and scene[1] in '.)':
                scene = scene[2:].strip()
            elif len(scene) > 3 and scene[:2].isdigit() and scene[2] in '.)':
                scene = scene[3:].strip()
            if scene:
                result["scenes"].append(scene)
    
    result["story"] = '\n'.join(story_lines).strip()
    
    # Ensure we have at least some scenes
    if not result["scenes"] and result["story"]:
        # Auto-generate scene descriptions from story
        paragraphs = result["story"].split('\n\n')
        result["scenes"] = [p[:100] + "..." if len(p) > 100 else p for p in paragraphs[:5]]
    
    return result


def get_available_cultures() -> list:
    """Return list of available cultures."""
    return list(CULTURAL_CONTEXTS.keys())
