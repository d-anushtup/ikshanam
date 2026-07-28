import streamlit as st
import os
from gtts import gTTS
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import random
import requests
from io import BytesIO
import urllib.parse

# Google Translate
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

# Edge TTS for natural-sounding neural voices (Microsoft)
try:
    import edge_tts
    import asyncio
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Sentiment Analysis for emotional audio control
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Try to import Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# Try to import MoviePy
try:
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

# Movis for advanced animations and compositions
try:
    import movis as mv
    MOVIS_AVAILABLE = True
except ImportError:
    MOVIS_AVAILABLE = False

# FFmpeg for high-quality video processing
try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False

# Imageio for frame-based video
try:
    import imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="Ikshanam - A Smart Cultural Storyteller", 
    page_icon="Ikshanam.png",
    layout="centered"
)

# Inject JavaScript to Force Scroll-to-Top
import streamlit.components.v1 as components

components.html(
    """
    <script>
        window.scrollTo(0, 0);
    </script>
    """,
    height=0,
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Hide deploy button and main menu, but keep sidebar toggle visible */
    #MainMenu {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    /* Hide the deploy button only - be specific to not hide sidebar toggle */
    .stDeployButton {
        display: none !important;
    }
    .stActionButton {
        display: none !important;
    }
    button[title="View app in fullscreen"] {
        display: none !important;
    }
    /* Hide only the right side of toolbar (deploy button area) */
    [data-testid="stToolbarActions"] {
        display: none !important;
    }
    
    /* Ensure sidebar toggle remains visible */
    button[data-testid="baseButton-headerNoPadding"] {
        display: block !important;
    }
    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Sidebar - Light background with proper input styling */
    section[data-testid="stSidebar"] {
        background: #f8f9fa !important;
    }
    section[data-testid="stSidebar"] * {
        color: #1a1a1a !important;
    }
    /* Ensure sidebar labels are black */
    section[data-testid="stSidebar"] label {
        color: #000000 !important;
    }
    section[data-testid="stSidebar"] label p {
        color: #000000 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextArea label,
    section[data-testid="stSidebar"] .stTextInput label {
        color: #000000 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stTextArea > div > div > textarea {
        background-color: #FFFFFF !important;
        color: #1a1a1a !important;
        border: 1px solid #ddd !important;
    }
    /* Selectbox (dropdown) - NO cursor, not editable, selection only */
    section[data-testid="stSidebar"] .stSelectbox input {
        caret-color: transparent !important;
        cursor: pointer !important;
        pointer-events: none !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        cursor: pointer !important;
    }
    /* Text inputs (Enter culture, Enter language, etc.) - white bg, black text, blinking cursor */
    section[data-testid="stSidebar"] .stTextInput input {
        background-color: #FFFFFF !important;
        color: #1a1a1a !important;
        caret-color: #1a1a1a !important;
        cursor: text !important;
        border: 1px solid #ddd !important;
    }
    section[data-testid="stSidebar"] .stTextInput input::placeholder {
        color: #888 !important;
    }
    section[data-testid="stSidebar"] .stTextInput input:focus {
        caret-color: #D4AF37 !important;
        animation: blink-caret 1s step-end infinite;
        border-color: #D4AF37 !important;
    }
    /* Only textarea (Custom Prompt) should have editable text */
    section[data-testid="stSidebar"] textarea {
        background-color: #FFFFFF !important;
        color: #1a1a1a !important;
        caret-color: #1a1a1a !important;
        cursor: text !important;
    }
    section[data-testid="stSidebar"] .stTextArea textarea::placeholder {
        color: #888 !important;
    }
    /* Blinking cursor animation ONLY for textarea (Custom Prompt) */
    section[data-testid="stSidebar"] .stTextArea textarea:focus {
        caret-color: #D4AF37 !important;
        animation: blink-caret 1s step-end infinite;
    }
    @keyframes blink-caret {
        from, to { caret-color: #D4AF37; }
        50% { caret-color: transparent; }
    }
    
    /* Main content - White text on dark background */
    .main .block-container h1,
    .main .block-container h2,
    .main .block-container h3,
    .main .block-container h4 {
        color: #FFFFFF !important;
    }
    .main .block-container p,
    .main .block-container span,
    .main .block-container label,
    .main .block-container .stMarkdown {
        color: #FFFFFF !important;
    }
    
    /* Story title styling */
    .story-title {
        color: #FFD700 !important;
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    .story-meta {
        color: #FFFFFF !important;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Header */
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .main-header h1 {
        color: #D4AF37 !important;
        font-size: 2.5rem;
    }
    .main-header p {
        color: #90EE90 !important;
        font-style: italic;
    }
    
    /* Story box */
    .story-box {
        background: rgba(255,255,255,0.08);
        border-radius: 15px;
        padding: 2rem;
        border-left: 4px solid #D4AF37;
        margin: 1rem 0;
        color: #FFFFFF !important;
        line-height: 1.6;
        font-family: "Times New Roman", Times, serif;
        font-size: 20px;
    }
    .story-box p {
        margin-bottom: 0.8rem;
    }
    
    /* Moral box */
    .moral-box {
        background: rgba(212, 175, 55, 0.15);
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #D4AF37;
        margin-top: 1rem;
        font-style: italic;
        font-size: 1.125rem;
        color: #FFD700 !important;
    }
    
    /* Media section header */
    .media-header {
        color: #FFFFFF !important;
        font-size: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Video/Audio headers */
    .section-header {
        color: #FFFFFF !important;
        font-size: 1.3rem;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Lime green color for processing spinners and status messages */
    .stSpinner > div > div {
        color: #90EE90 !important;
    }
    .stSpinner > div {
        color: #90EE90 !important;
    }
    /* Spinner text */
    .stSpinner p, .stSpinner span {
        color: #90EE90 !important;
    }
    
    /* Lime green toggle label */
    .stToggle label p, .stToggle label span {
        color: #90EE90 !important;
    }
    div[data-testid="stToggle"] label {
        color: #90EE90 !important;
    }
    div[data-testid="stToggle"] label p {
        color: #90EE90 !important;
    }
    div[data-testid="stToggle"] p {
        color: #90EE90 !important;
    }
    /* Force all toggle text to lime green */
    [data-testid="stToggle"] * {
        color: #90EE90 !important;
    }
    
    /* Lime green for voice selection label */
    .main .block-container label[data-testid="stWidgetLabel"] p:has-text("Narrator Voice"),
    .main .block-container .stSelectbox label p {
        color: #90EE90 !important;
    }
    /* Target selectbox with voice in label */
    .stSelectbox[data-testid="stSelectbox"] label {
        color: #90EE90 !important;
    }
    .stSelectbox label p {
        color: #90EE90 !important;
    }
    
    /* Main content selectbox (narrator voice) - NO cursor, not editable */
    .main .block-container .stSelectbox input {
        caret-color: transparent !important;
        cursor: pointer !important;
        pointer-events: none !important;
        user-select: none !important;
        -webkit-user-select: none !important;
    }
    .main .block-container .stSelectbox > div > div {
        cursor: pointer !important;
    }
    .main .block-container .stSelectbox input[type="text"] {
        caret-color: transparent !important;
        pointer-events: none !important;
    }
    /* Hide text cursor in all selectboxes in main content */
    .main .stSelectbox div[data-baseweb="select"] input {
        caret-color: transparent !important;
        cursor: pointer !important;
        pointer-events: none !important;
    }
    .main .stSelectbox div[data-baseweb="input"] input {
        caret-color: transparent !important;
        cursor: pointer !important;
    }
</style>
<script>
    // Disable keyboard input on selectboxes in main content
    const disableSelectboxInput = () => {
        const inputs = document.querySelectorAll('.main .stSelectbox input');
        inputs.forEach(input => {
            input.setAttribute('readonly', 'readonly');
            input.style.caretColor = 'transparent';
            input.style.cursor = 'pointer';
            input.addEventListener('keydown', (e) => {
                if (e.key !== 'Tab' && e.key !== 'Escape' && e.key !== 'Enter') {
                    e.preventDefault();
                }
            });
        });
    };
    // Run on load and observe for dynamic changes
    disableSelectboxInput();
    const observer = new MutationObserver(disableSelectboxInput);
    observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

# Google Fonts link (needed for header styling)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Permanent+Marker&family=UnifrakturMaguntia&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Cultural knowledge for prompts
CULTURES = {
    "Indian": "Indian culture with elements of dharma, karma, wisdom, festivals, and village life. Style: poetic with nature metaphors.",
    "Japanese": "Japanese culture with honor, nature spirits (kami), zen philosophy, cherry blossoms. Style: contemplative and elegant.",
    "African": "African culture with community wisdom, animal tricksters like Anansi, ancestral spirits. Style: vibrant with proverbs.",
    "Celtic": "Celtic culture with faeries, druids, ancient magic, sacred groves. Style: mystical and lyrical.",
    "Chinese": "Chinese culture with dragons, filial piety, immortals, Jade Emperor. Style: elegant and wise.",
    "Greek": "Greek culture with gods of Olympus, heroes, quests, fate. Style: epic and dramatic.",
    "Arabian": "Arabian culture with djinn, magic lamps, desert wisdom, merchants. Style: rich and ornate.",
    "Native American": "Native American culture with animal spirits, creation stories, harmony with nature. Style: reverent and earthy."
}


STORY_TYPES = ["Folk Tale", "Mythology", "Historical Story", "Moral Story", "Legend", "Other (type below)"]
TONES = ["Simple & Easy", "Dramatic & Epic", "Child-friendly", "Mysterious", "Humorous", "Other (type below)"]
LANGUAGES = ["English", "Bengali", "Marathi", "Odia", "Assamese", "Maithili", "Malayalam", "Tamil", "Gujarati", "Punjabi", "Italian", "Spanish", "French", "German", "Japanese", "Chinese", "Arabic", "Other (type below)"]

# Available narration voices (Edge TTS Neural Voices - free and high quality)
NARRATION_VOICES = {
    "Jenny (US, Clear)": "en-US-JennyNeural",
    "Aria (US, Warm)": "en-US-AriaNeural",
    "Guy (US, Male)": "en-US-GuyNeural",
    "Davis (US, Male Deep)": "en-US-DavisNeural",
    "Sonia (UK, Expressive)": "en-GB-SoniaNeural",
    "Ryan (UK, Male)": "en-GB-RyanNeural",
    "Natasha (AU, Female)": "en-AU-NatashaNeural",
    "William (AU, Male)": "en-AU-WilliamNeural",
    "Libby (UK, Warm)": "en-GB-LibbyNeural",
    "Maisie (UK, Young)": "en-GB-MaisieNeural",
    "Ana (US, Child)": "en-US-AnaNeural",
    "Christopher (US, News)": "en-US-ChristopherNeural",
}

# Language-specific voices for Edge TTS (used when story is in non-English language)
LANGUAGE_VOICES = {
    "bengali": ("bn-IN-TanishaaNeural", "bn"),
    "hindi": ("hi-IN-SwaraNeural", "hi"),
    "tamil": ("ta-IN-PallaviNeural", "ta"),
    "telugu": ("te-IN-ShrutiNeural", "te"),
    "marathi": ("mr-IN-AarohiNeural", "mr"),
    "gujarati": ("gu-IN-DhwaniNeural", "gu"),
    "kannada": ("kn-IN-SapnaNeural", "kn"),
    "malayalam": ("ml-IN-SobhanaNeural", "ml"),
    "punjabi": ("pa-IN-VaaniNeural", "pa"),
    "odia": ("or-IN-SubhasiniNeural", "or"),  
    "assamese": ("as-IN-YashicaNeural", "as"),
    "spanish": ("es-ES-ElviraNeural", "es"),
    "french": ("fr-FR-DeniseNeural", "fr"),
    "german": ("de-DE-KatjaNeural", "de"),
    "italian": ("it-IT-ElsaNeural", "it"),
    "japanese": ("ja-JP-NanamiNeural", "ja"),
    "chinese": ("zh-CN-XiaoxiaoNeural", "zh-CN"),
    "arabic": ("ar-SA-ZariyahNeural", "ar"),
    "korean": ("ko-KR-SunHiNeural", "ko"),
    "portuguese": ("pt-BR-FranciscaNeural", "pt"),
    "russian": ("ru-RU-SvetlanaNeural", "ru"),
    "turkish": ("tr-TR-EmelNeural", "tr"),
    "dutch": ("nl-NL-ColetteNeural", "nl"),
    "polish": ("pl-PL-AgnieszkaNeural", "pl"),
    "swedish": ("sv-SE-SofieNeural", "sv"),
    "greek": ("el-GR-AthinaNeural", "el"),
    "english": ("en-US-JennyNeural", "en"),
}

# --- Artistic Background Generator (Pillow fallback) ---
def generate_cultural_background(culture_name, width=800, height=400, title=""):
    """Generate a beautiful artistic background image for a given culture using Pillow.
    
    Creates gradient backgrounds with radial glow, decorative borders,
    subtle noise texture, and culture-specific color palettes.
    """
    from PIL import ImageDraw, ImageFilter, ImageFont
    import math
    
    # Rich culture-specific color palettes: (top-left, top-right, bottom-left, bottom-right, accent)
    CULTURE_PALETTES = {
        'Indian':          ((255, 153, 51),  (220, 80, 20),   (128, 0, 128),   (80, 0, 100),    (255, 215, 0)),
        'Japanese':        ((255, 183, 197), (200, 130, 170), (60, 80, 140),   (30, 40, 100),   (255, 255, 255)),
        'African':         ((255, 160, 0),   (200, 100, 0),   (120, 50, 10),   (60, 25, 5),     (255, 220, 100)),
        'Celtic':          ((30, 120, 50),   (20, 80, 40),    (60, 20, 100),   (30, 10, 70),    (180, 255, 180)),
        'Chinese':         ((200, 20, 20),   (150, 10, 10),   (180, 150, 0),   (120, 100, 0),   (255, 215, 0)),
        'Greek':           ((20, 100, 200),  (10, 60, 150),   (240, 240, 255), (180, 180, 220), (255, 255, 255)),
        'Arabian':         ((80, 40, 120),   (50, 20, 80),    (200, 160, 50),  (150, 120, 30),  (255, 215, 0)),
        'Native American': ((180, 80, 20),   (120, 50, 10),   (20, 100, 50),   (10, 60, 30),    (255, 200, 100)),
        'Egyptian':        ((200, 170, 50),  (160, 130, 30),  (100, 50, 10),   (60, 30, 5),     (255, 215, 0)),
    }
    
    palette = CULTURE_PALETTES.get(culture_name, ((40, 40, 80), (30, 30, 60), (80, 40, 60), (50, 20, 40), (200, 200, 255)))
    tl, tr, bl, br, accent = palette
    
    # Create base image with 4-corner gradient
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    for y in range(height):
        ry = y / max(height - 1, 1)
        for x in range(width):
            rx = x / max(width - 1, 1)
            # Bilinear interpolation of 4 corners
            top = tuple(int(tl[c] * (1 - rx) + tr[c] * rx) for c in range(3))
            bot = tuple(int(bl[c] * (1 - rx) + br[c] * rx) for c in range(3))
            color = tuple(int(top[c] * (1 - ry) + bot[c] * ry) for c in range(3))
            pixels[x, y] = color
    
    # Add radial glow in center
    glow = Image.new('RGB', (width, height), (0, 0, 0))
    glow_pixels = glow.load()
    cx, cy = width // 2, height // 2
    max_dist = math.sqrt(cx ** 2 + cy ** 2)
    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            intensity = max(0, 1 - (dist / max_dist)) ** 2
            glow_pixels[x, y] = (
                int(accent[0] * intensity * 0.3),
                int(accent[1] * intensity * 0.3),
                int(accent[2] * intensity * 0.3),
            )
    
    # Blend glow onto base
    from PIL import ImageChops
    img = ImageChops.add(img, glow)
    
    # Add subtle noise texture
    import random as _rnd
    noise_img = Image.new('RGB', (width, height))
    noise_pixels = noise_img.load()
    for y in range(height):
        for x in range(width):
            n = _rnd.randint(-15, 15)
            noise_pixels[x, y] = (n, n, n)
    img = ImageChops.add(img, noise_img)
    
    # Add decorative border frame
    draw = ImageDraw.Draw(img)
    border_color = tuple(min(255, c + 60) for c in accent)
    # Outer border
    draw.rectangle([8, 8, width - 9, height - 9], outline=(*border_color, 100), width=2)
    # Inner border with slight offset
    inner_color = tuple(min(255, c + 30) for c in accent)
    draw.rectangle([16, 16, width - 17, height - 17], outline=(*inner_color, 60), width=1)
    
    # Add corner ornaments (small diamond shapes)
    ornament_size = 6
    corners = [(20, 20), (width - 20, 20), (20, height - 20), (width - 20, height - 20)]
    for cx_o, cy_o in corners:
        draw.polygon([
            (cx_o, cy_o - ornament_size),
            (cx_o + ornament_size, cy_o),
            (cx_o, cy_o + ornament_size),
            (cx_o - ornament_size, cy_o),
        ], fill=border_color)
    
    # Add soft vignette (darken edges)
    vignette = Image.new('L', (width, height), 255)
    vig_draw = ImageDraw.Draw(vignette)
    for i in range(40):
        opacity = int(255 * (1 - i / 40) * 0.4)
        vig_draw.rectangle([i, i, width - i - 1, height - i - 1], outline=opacity)
    img = Image.composite(img, Image.new('RGB', (width, height), (0, 0, 0)), vignette)
    
    # Apply slight blur for a painterly feel
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    return img


# --- AI Image Generator via HF Router (Together / FLUX.1-schnell) ---
def generate_ai_image(prompt, hf_token, width=800, height=400, fallback_culture="", fallback_title=""):
    """Generate an image using FLUX.1-schnell via the HF Router (Together provider).
    
    Returns a data-URL string ready for use in an <img src="...">.
    Falls back to the Pillow gradient generator if HF is unavailable.
    Returns (data_url: str, error: str|None).
    """
    import base64

    if hf_token:
        try:
            hf_url = "https://router.huggingface.co/together/v1/images/generations"
            hf_headers = {
                "Authorization": f"Bearer {hf_token}",
                "Content-Type": "application/json",
            }
            hf_payload = {
                "model": "black-forest-labs/FLUX.1-schnell",
                "prompt": prompt,
                "n": 1,
                "width": width,
                "height": height,
                "steps": 4,
                "response_format": "b64_json",
            }
            resp = requests.post(hf_url, headers=hf_headers, json=hf_payload, timeout=60)
            if resp.status_code == 200:
                b64 = resp.json()["data"][0].get("b64_json", "")
                if b64:
                    return f"data:image/jpeg;base64,{b64}", None
                else:
                    err = "HF returned 200 but no b64_json field."
            else:
                err = f"HF API error {resp.status_code}: {resp.text[:200]}"
        except requests.exceptions.Timeout:
            err = "Request timed out — try again shortly."
        except Exception as e:
            err = f"Unexpected error: {e}"
    else:
        err = "HF_TOKEN not set in .env or Streamlit secrets."

    # Fallback: Pillow gradient
    culture_name = fallback_culture
    pil_img = generate_cultural_background(culture_name, width=width, height=height, title=fallback_title)
    buf = BytesIO()
    pil_img.save(buf, format="PNG")
    fb_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{fb_b64}", err

# Sidebar for inputs
st.sidebar.header("Create Your Story")

# Custom prompt
custom_prompt = st.sidebar.text_area(
    "Custom Prompt", 
    placeholder="Enter your thoughts..."
)

# Culture selection with custom option
culture_options = list(CULTURES.keys()) + ["Other (type below)"]
culture_choice = st.sidebar.selectbox("Choose Culture", culture_options)
if culture_choice == "Other (type below)":
    culture = st.sidebar.text_input("Enter culture:", placeholder="e.g., Korean, Persian, Slavic...")
else:
    culture = culture_choice

# Story Type selection with custom option
story_type_choice = st.sidebar.selectbox("Choose Story Type", STORY_TYPES)
if story_type_choice == "Other (type below)":
    story_type = st.sidebar.text_input("Enter story type:", placeholder="e.g., Fable, Parable, Epic...")
else:
    story_type = story_type_choice

# Tone selection with custom option
tone_choice = st.sidebar.selectbox("Choose Tone", TONES)
if tone_choice == "Other (type below)":
    tone = st.sidebar.text_input("Enter tone:", placeholder="e.g., Romantic, Philosophical, Adventurous...")
else:
    tone = tone_choice

# Language selection
language_choice = st.sidebar.selectbox("Choose Story Language", LANGUAGES, index=0)
if language_choice == "Other (type below)":
    story_language = st.sidebar.text_input("Enter language:", placeholder="e.g., Odia, Nepali, Portuguese...")
else:
    story_language = language_choice


# Check API key - supports both Streamlit Cloud (st.secrets) and local (.env)
api_key = None
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.warning("Please set GROQ_API_KEY to generate stories.")
    st.info("**Local:** Add `GROQ_API_KEY=your-key` to your `.env` file")
    st.info("**Streamlit Cloud:** Go to App Settings → Secrets and add:\n```\nGROQ_API_KEY = \"your-key-here\"\n```")
    st.info("Get your free API key at: https://console.groq.com/keys")
    st.stop()

# Load Hugging Face token for AI image generation (optional — falls back to Pillow gradient)
hf_token = None
try:
    hf_token = st.secrets["HF_TOKEN"]
except Exception:
    hf_token = os.getenv("HF_TOKEN")

if not GROQ_AVAILABLE:
    st.error("Groq package not installed. Run: pip install groq")
    st.stop()

# --- Prompt Relevance Guardrail ---
# Off-topic keywords/phrases that are clearly unrelated to cultural storytelling
_OFF_TOPIC_KEYWORDS = [
    # Sports
    "football score", "cricket score", "basketball score", "baseball score",
    "soccer score", "match result", "who won the match", "ipl score",
    "world cup score", "premier league", "nba score", "nfl score",
    "yesterday's game", "today's game", "live score",
    # Finance / Stocks
    "stock price", "share price", "market cap", "bitcoin price",
    "crypto price", "nifty", "sensex", "nasdaq", "dow jones",
    # Weather
    "weather today", "weather forecast", "temperature today",
    "will it rain", "weather in",
    # News / Current events
    "latest news", "breaking news", "headlines today",
    "election result", "who is the president", "who is the prime minister",
    # Tech support / Code
    "write code", "write a program", "fix my code", "debug this",
    "python code", "javascript code", "html code", "sql query",
    "how to install", "stack overflow",
    # Math / Homework
    "solve this equation", "calculate", "what is the formula",
    "math problem", "integral of", "derivative of",
    # Personal assistant
    "set an alarm", "remind me", "send an email", "call ",
    "book a flight", "order food", "pizza near me",
    "directions to", "navigate to", "open google",
    # Recipes (non-cultural)
    "recipe for", "how to cook", "calories in",
    # Generic chatbot
    "who are you", "what can you do", "are you alive",
    "tell me a joke", "sing a song",
]

def is_prompt_on_topic(prompt_text):
    """Check whether the custom prompt is relevant to cultural storytelling.
    
    Returns:
        (bool, str): (is_on_topic, reason_if_off_topic)
    """
    if not prompt_text or not prompt_text.strip():
        return True, ""  # Empty prompt is fine — the app uses default story settings
    
    prompt_lower = prompt_text.lower().strip()
    
    # --- Fast path: keyword-based check ---
    for keyword in _OFF_TOPIC_KEYWORDS:
        if keyword in prompt_lower:
            return False, (
                f"Your prompt appears to be about **\"{keyword}\"**, which is outside "
                "Ikshanam's scope. This app is a **cultural storytelling** platform — "
                "try prompts related to myths, legends, folk tales, cultural traditions, "
                "or historical stories instead!"
            )
    
    # --- Slow path: LLM-based relevance classifier ---
    try:
        client = Groq(api_key=api_key)
        classification = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a content-relevance classifier for a CULTURAL STORYTELLING app called Ikshanam. "
                        "The app generates folk tales, myths, legends, moral stories, and historical narratives "
                        "rooted in world cultures.\n\n"
                        "CRITICAL RULE: If the user is asking for a STORY, TALE, or NARRATIVE about ANY topic "
                        "(even modern ones like football, cricket, technology, etc.), that is ON_TOPIC. "
                        "The app can weave cultural stories around any subject.\n"
                        "Only reject prompts that are purely INFORMATIONAL QUERIES seeking facts, data, scores, "
                        "code, calculations, or real-time information — NOT storytelling.\n\n"
                        "ON_TOPIC examples (story/narrative requests):\n"
                        "- 'Tell me about a brave warrior princess' → ON_TOPIC\n"
                        "- 'A story involving dragons and wisdom' → ON_TOPIC\n"
                        "- 'Cultural story about football' → ON_TOPIC (wants a story themed around football)\n"
                        "- 'A tale about a cricket match' → ON_TOPIC (narrative request)\n"
                        "- 'Story about a village and technology' → ON_TOPIC\n"
                        "- 'Something about harvest festivals' → ON_TOPIC\n"
                        "- 'A warrior who learned humility' → ON_TOPIC\n\n"
                        "OFF_TOPIC examples (factual/informational queries, NOT story requests):\n"
                        "- 'What is the weather today?' → OFF_TOPIC (asking for real-time data)\n"
                        "- 'Tell me yesterday's football score' → OFF_TOPIC (asking for a factual score)\n"
                        "- 'Who won IPL 2024?' → OFF_TOPIC (asking for a result)\n"
                        "- 'Write Python code for sorting' → OFF_TOPIC (code request)\n"
                        "- 'What is 2+2?' → OFF_TOPIC (calculation)\n"
                        "- 'Who won the election?' → OFF_TOPIC (factual query)\n"
                        "- 'Explain quantum physics' → OFF_TOPIC (educational explanation)\n\n"
                        "When in doubt, lean ON_TOPIC — the app can create stories around almost anything.\n"
                        "Respond with EXACTLY one word: ON_TOPIC or OFF_TOPIC. Nothing else."
                    )
                },
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.0,
            max_tokens=10,
        )
        verdict = classification.choices[0].message.content.strip().upper()
        if "OFF_TOPIC" in verdict:
            return False, (
                "Your prompt doesn't seem related to **cultural storytelling**. "
                "Ikshanam is designed to craft folk tales, myths, legends, and cultural narratives. "
                "Try something like *\"A story about a clever fox in an ancient forest\"* or "
                "*\"Tell me a legend about a sacred river\"*!"
            )
    except Exception:
        pass  # If the classifier fails, allow the prompt through gracefully
    
    return True, ""

# Generate story function using GROQ
def generate_story(culture_name, story_type, tone, language="English", custom_prompt=""):
    """Generate a cultural story using GROQ API with rich emotional depth."""
    
    culture_context = CULTURES.get(culture_name, f"A rich cultural tradition with unique stories, values, and wisdom from {culture_name} culture.")
    culture_short = culture_name.split(' ', 1)[1] if ' ' in culture_name else culture_name
    
    # Random elements to ensure variety
    import random
    import time
    random.seed(int(time.time() * 1000) % 1000000)
    
    # Varied story elements for uniqueness
    story_seeds = [
        "a fateful encounter", "an ancient mystery", "a forbidden journey",
        "a sacred promise", "a forgotten prophecy", "an unexpected friendship",
        "a test of courage", "a moment of transformation", "a clash of worlds",
        "a redemption arc", "a sacrifice for love", "a discovery of truth"
    ]
    
    emotions = [
        "longing and hope", "fear transforming into courage", "grief becoming wisdom",
        "love conquering doubt", "pride humbled by compassion", "joy found in sorrow",
        "anger tempered by understanding", "despair reborn as faith"
    ]
    
    sensory_focus = random.choice([
        "the sounds of nature - rustling leaves, flowing water, distant thunder",
        "the textures and temperatures - cool morning mist, warm embrace, rough earth",
        "the colors and light - golden sunsets, silver moonlight, vibrant festivals",
        "the aromas and tastes - fragrant flowers, sacred incense, traditional foods"
    ])
    
    chosen_seed = random.choice(story_seeds)
    chosen_emotion = random.choice(emotions)
    
    # Tone-specific writing instructions
    tone_instructions = {
        "Simple & Easy": "Use clear, flowing language that a child could understand, but with hidden depth. Short sentences that paint vivid pictures.",
        "Dramatic & Epic": "Use powerful, sweeping prose with intense imagery. Build tension with long, flowing sentences that crescendo at key moments. Use metaphors of storms, fire, and destiny.",
        "Child-friendly": "Use warm, gentle language with wonder and magic. Include friendly characters and reassuring moments. End with comfort and hope.",
        "Mysterious": "Use atmospheric, shadowy descriptions. Create suspense with pauses and unanswered questions. Let secrets unfold slowly like morning fog lifting.",
        "Humorous": "Weave wit and clever observations throughout. Include amusing misunderstandings, playful dialogue, and situations that make readers smile."
    }
    
    tone_guide = tone_instructions.get(tone, f"Write with a {tone} style that matches the mood described.")
    
    # Language instruction
    language_instruction = ""
    if language and language.lower() != "english":
        language_instruction = f"\n\n🗣️ **IMPORTANT - WRITE THE ENTIRE STORY IN {language.upper()}** (not English)"
    
    # Special handling for Mythology, Legend, Historical Story, and Literature - must be factually accurate
    factual_instruction = ""
    requires_factual_accuracy = False
    story_type_lower = story_type.lower()
    if story_type_lower in ["mythology", "legend", "historical story"]:
        requires_factual_accuracy = True
        if story_type_lower == "mythology":
            story_type_name = "MYTHOLOGY"
            examples = "Ramayana, Mahabharata, Greek/Norse myths, Egyptian mythology"
        elif story_type_lower == "legend":
            story_type_name = "LEGEND"
            examples = "King Arthur, Robin Hood, Vikram-Betal, Akbar-Birbal, local folk heroes"
        else:
            story_type_name = "HISTORICAL"
            examples = "Chandragupta Maurya, Ashoka, Shivaji, Rani Lakshmibai, Alexander the Great"
        
        factual_instruction = f"""

**CRITICAL - {story_type_name} ACCURACY REQUIREMENT**:
Since this is a {story_type_name} story, you MUST follow these strict guidelines:

DO NOT HALLUCINATE OR INVENT:
- DO NOT create fictional characters, events, or places
- DO NOT invent dialogues or scenes that contradict historical/mythological records
- DO NOT modify established facts, relationships, timelines, or outcomes
- DO NOT mix different mythologies or historical periods incorrectly

YOU MUST:
- Base the story on REAL, well-documented figures and events (e.g., {examples})
- Use ACCURATE names, dates, relationships, and facts as recorded in authentic sources
- Follow the ACTUAL narrative as it exists in traditional texts and historical records
- Include only authentic elements, places, and cultural attributes of that era
- If adding descriptive detail (weather, emotions), ensure it doesn't contradict known facts
- Cite the source tradition if relevant (e.g., "from the Mahabharata", "according to Greek tradition")

This is a FAITHFUL RETELLING with beautiful language - NOT a creative reimagining."""
    
    prompt = f"""You are a legendary storyteller, the kind whose voice makes listeners forget time itself. Your tales have been passed down through generations because they touch the soul.{language_instruction}{factual_instruction}

CREATE A UNIQUE {story_type.upper()} from {culture_short} culture that will make the reader FEEL deeply.

TONE: {tone}
{tone_guide}

CULTURAL SOUL:
{culture_context}

THIS STORY'S UNIQUE ELEMENTS:
- Central theme: {chosen_seed}
- Emotional journey: {chosen_emotion}
- Sensory focus: {sensory_focus}
{f'- Special request: {custom_prompt}' if custom_prompt else ''}

STORYTELLING REQUIREMENTS:

1. **EMOTIONAL DEPTH**: Make the reader's heart race, ache, or soar. Show characters' inner struggles. Use the emotional journey of "{chosen_emotion}" as an undercurrent.

2. **SENSORY IMMERSION**: Transport readers there! Describe how things look, sound, smell, feel. Focus especially on: {sensory_focus}

3. **AUTHENTIC VOICE**: Write as if this tale has been told by firelight for a thousand years. Use rhythms, phrases, and wisdom authentic to {culture_short} storytelling traditions.

4. **LIVING CHARACTERS**: Give your main character(s) a clear desire, a deep fear, and a moment of choice that defines them. Even in a short tale, make us CARE.

5. **MEANINGFUL JOURNEY**: Begin with a hook that grabs attention. Build through meaningful conflict. End with a resolution that lingers in the mind like a beautiful melody.

{"6. **FACTUAL ACCURACY**: Retell or expand upon a KNOWN " + story_type.lower() + " with accurate characters, dates, and events. You may add emotional depth and sensory detail, but keep ALL FACTS TRUE to history/tradition as it is widely known. DO NOT HALLUCINATE." if story_type_lower in ["mythology", "legend", "historical story"] else "6. **UNIQUE NARRATIVE**: This must be ORIGINAL - not a retelling of a famous story. Create something fresh that FEELS timeless."}

{"7. **LANGUAGE**: Write the ENTIRE story in " + language + ". The title, story, and moral must all be in " + language + "." if language.lower() != "english" else ""}

Write 400-500 words of rich, immersive storytelling.

FORMAT:
TITLE: [An evocative, poetic title that hints at the story's soul]

STORY:
[Your masterpiece - multiple paragraphs with natural breaks for pacing]

MORAL: [A profound truth, stated beautifully - not preachy, but wise]"""

    # Determine temperature based on story type
    # Lower temperature for factual content to reduce hallucination
    if requires_factual_accuracy:
        story_temperature = 0.5  # Lower temperature for factual accuracy
        system_content = f"""You are a scholar-storyteller from the {culture_short} tradition. 
You have spent your life studying authentic texts, historical records, and traditional narratives.
You are deeply knowledgeable about {culture_short} mythology, history, and legends.
Your stories are ALWAYS factually accurate - you never invent or modify established facts.
You retell known stories with beautiful language while maintaining complete historical/mythological accuracy.
When telling mythology or legends, you draw from authentic sources like ancient texts, scriptures, and documented traditions.
You believe that the truth of these stories is sacred and must be preserved."""
    else:
        story_temperature = 0.95  # Higher temperature for creative/original stories
        system_content = f"""You are a master storyteller from the {culture_short} tradition. 
You have spent your life collecting and telling tales that make people laugh, cry, and think. 
Your voice carries the wisdom of ancestors and the wonder of a child seeing magic for the first time.
Every story you tell is unique - never the same tale twice.
You believe that a good story is not just heard, but FELT in the bones."""
    
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": system_content
                },
                {"role": "user", "content": prompt}
            ],
            temperature=story_temperature,
            max_tokens=2000,
            top_p=0.9 if not requires_factual_accuracy else 0.7  # Lower top_p for factual content
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

# Parse story response
def parse_story(text):
    """Parse the story response into components - handles various formats and languages."""
    result = {"title": "", "story": "", "moral": ""}
    
    import re
    
    # Try multiple patterns to extract title
    # Pattern 1: **TITLE:** or TITLE: at start of line
    title_patterns = [
        r'\*{0,2}TITLE\*{0,2}\s*:\s*\*{0,2}([^\n*]+)',  # TITLE: text
        r'^#{1,3}\s+(.+)$',  # # Heading format
        r'^\*\*([^*\n]+)\*\*$',  # **Title** on its own line
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            title = match.group(1).strip()
            title = title.replace('**', '').replace('*', '').strip()
            # Remove surrounding double quotes
            title = title.strip('"').strip('"').strip('"')
            if title and len(title) > 3 and not title.upper().startswith(('STORY', 'MORAL')):
                result["title"] = title
                break
    
    # Extract MORAL - check multiple patterns including translated labels
    moral_patterns = [
        r'\*{0,2}MORAL\*{0,2}\s*:\s*\*{0,2}([^\n]+)',  # MORAL: text
        r'\*{0,2}नीति\*{0,2}\s*:\s*\*{0,2}([^\n]+)',  # Hindi
        r'\*{0,2}নীতিকথা\*{0,2}\s*:\s*\*{0,2}([^\n]+)',  # Bengali
        r'\*{0,2}Moraleja\*{0,2}\s*:\s*\*{0,2}([^\n]+)',  # Spanish
        r'\*{0,2}Morale\*{0,2}\s*:\s*\*{0,2}([^\n]+)',  # French/Italian
        r'The moral of (?:the|this) story (?:is|:)\s*([^\n]+)',  # Common English pattern
        r'Moral of the story\s*:\s*([^\n]+)',  # Another English pattern
        r'\*{0,2}Lesson\*{0,2}\s*:\s*\*{0,2}([^\n]+)',  # Lesson: format
        r'\*{0,2}Teaching\*{0,2}\s*:\s*\*{0,2}([^\n]+)',  # Teaching: format
    ]
    
    for pattern in moral_patterns:
        moral_match = re.search(pattern, text, re.IGNORECASE)
        if moral_match:
            moral = moral_match.group(1).strip()
            moral = moral.replace('**', '').replace('*', '').strip()
            result["moral"] = moral
            break
    
    # Extract story - between STORY: and MORAL: (or end)
    story_match = re.search(r'\*{0,2}STORY\*{0,2}\s*:\s*\n(.*?)(?=\*{0,2}MORAL\*{0,2}\s*:|$)', text, re.IGNORECASE | re.DOTALL)
    if story_match:
        story = story_match.group(1).strip()
    else:
        # Fallback: everything after TITLE line
        story = text
        # Remove TITLE line
        story = re.sub(r'\*{0,2}TITLE\*{0,2}\s*:[^\n]*\n?', '', story, flags=re.IGNORECASE)
        # Remove STORY: marker
        story = re.sub(r'\*{0,2}STORY\*{0,2}\s*:\s*\n?', '', story, flags=re.IGNORECASE)
    
    # Remove all moral-related lines from story
    moral_removal_patterns = [
        r'\*{0,2}MORAL\*{0,2}\s*:[^\n]*\n?',  # MORAL: text
        r'\*{0,2}नीति\*{0,2}\s*:[^\n]*\n?',  # Hindi
        r'\*{0,2}নীতিকথা\*{0,2}\s*:[^\n]*\n?',  # Bengali
        r'\*{0,2}Moraleja\*{0,2}\s*:[^\n]*\n?',  # Spanish
        r'\*{0,2}Morale\*{0,2}\s*:[^\n]*\n?',  # French/Italian
        r'The moral of (?:the|this) story (?:is|:)[^\n]*\n?',  # Common English pattern
        r'Moral of the story\s*:[^\n]*\n?',  # Another English pattern
        r'\*{0,2}Lesson\*{0,2}\s*:[^\n]*\n?',  # Lesson: format
        r'\*{0,2}Teaching\*{0,2}\s*:[^\n]*\n?',  # Teaching: format
    ]
    for pattern in moral_removal_patterns:
        story = re.sub(pattern, '', story, flags=re.IGNORECASE)
    
    # Clean story
    story = story.replace('**', '').strip()
    
    # Remove title from story if it appears at the beginning
    if result["title"]:
        lines = story.split('\n')
        if lines and lines[0].strip().replace('*', '') == result["title"]:
            story = '\n'.join(lines[1:]).strip()
    
    result["story"] = story
    
    # If still no title, take first non-empty line as title
    if not result["title"] and result["story"]:
        lines = result["story"].split('\n')
        for i, line in enumerate(lines):
            line_clean = line.replace('**', '').replace('*', '').strip()
            if line_clean and 3 < len(line_clean) < 200:
                if not line_clean.upper().startswith(('TITLE', 'STORY', 'MORAL', 'IN THE', 'ONCE', 'LONG AGO')):
                    result["title"] = line_clean
                    result["story"] = '\n'.join(lines[i+1:]).strip()
                break
    
    # Final fallback - generate title from first sentence
    if not result["title"] and result["story"]:
        first_sentence = result["story"].split('.')[0]
        if first_sentence and len(first_sentence) < 100:
            result["title"] = first_sentence[:60] + "..." if len(first_sentence) > 60 else first_sentence
    
    if not result["title"]:
        result["title"] = "A Unique Tale"
    
    if not result["story"]:
        result["story"] = text
    
    return result

# Translate story function using GROQ
def translate_story(story_text, title, moral, target_language):
    """Translate the story to target language using GROQ API."""
    
    prompt = f"""Translate the following story into {target_language}. 
Maintain the emotional tone, cultural essence, and storytelling style.
Translate ONLY the content, do not add any explanations or notes.

TITLE (translate this):
{title}

STORY (translate this):
{story_text}

MORAL (translate this):
{moral}

Provide the translation in this exact format:
TITLE: [translated title]

STORY:
[translated story]

MORAL: [translated moral]
"""
    
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are an expert translator specializing in {target_language}. Translate with cultural sensitivity and maintain the storytelling essence."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more accurate translation
            max_tokens=3000
        )
        return response.choices[0].message.content, None
    except Exception as e:
        return None, str(e)

# Analyze text sentiment for voice selection
def analyze_story_mood(text):
    """Analyze story mood using TextBlob for voice selection."""
    if TEXTBLOB_AVAILABLE:
        try:
            blob = TextBlob(text[:1000])  # Analyze first 1000 chars
            polarity = blob.sentiment.polarity
            if polarity > 0.2:
                return "positive"
            elif polarity < -0.2:
                return "dramatic"
            return "neutral"
        except:
            return "neutral"
    return "neutral"

# Generate audio function with natural neural voices
def generate_audio(text, output_path, voice_id=None, language=None):
    """Generate audio using Edge TTS (Microsoft neural voices) or gTTS fallback.
    
    Args:
        text: The text to convert to speech
        output_path: Path to save the audio file
        voice_id: Specific voice ID to use (e.g., 'en-US-JennyNeural') - only used for English
        language: The language of the text (e.g., 'bengali', 'hindi') - overrides voice_id for non-English
    """
    
    # Determine the correct voice based on language
    lang_lower = (language or "english").lower().strip()
    gtts_lang = "en"  # Default for gTTS fallback
    
    # Check if we have a language-specific voice
    if lang_lower in LANGUAGE_VOICES and lang_lower != "english":
        # Use language-specific voice for non-English stories
        voice = LANGUAGE_VOICES[lang_lower][0]
        gtts_lang = LANGUAGE_VOICES[lang_lower][1]
    elif voice_id:
        # Use provided voice for English
        voice = voice_id
    else:
        # Default English voice
        voice = "en-US-JennyNeural"
    
    rate = "+0%"
    
    # Try Edge TTS first (much more natural sounding)
    if EDGE_TTS_AVAILABLE:
        try:
            # Create async function for edge-tts
            async def generate():
                communicate = edge_tts.Communicate(text, voice, rate=rate)
                await communicate.save(output_path)
            
            # Run the async function
            asyncio.run(generate())
            return output_path, None
            
        except Exception as e:
            # Fall back to gTTS
            pass
    
    # Fallback to gTTS
    try:
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        tts.save(output_path)
        return output_path, None
    except Exception as e:
        return None, str(e)

# Generate video function with FFmpeg for high quality
def generate_video(story_data, output_dir, voice_id=None, language=None):
    """Generate a high-quality story video using FFmpeg with transitions.
    
    Args:
        story_data: dict with title, story, etc.
        output_dir: directory to save output files
        voice_id: optional voice ID for narration
        language: optional language for narration (e.g., 'bengali', 'hindi')
    """
    
    title = story_data['title']
    story = story_data['story']
    culture = st.session_state.get('culture', '🇮🇳 Indian')
    
    # Split story into scenes (paragraphs)
    paragraphs = [p.strip() for p in story.split('\n') if p.strip()]
    if not paragraphs:
        paragraphs = [story[:300]]
    
    # Limit to 5 scenes
    scenes = paragraphs[:5]
    
    try:
        # Create temp directory
        temp_dir = Path(output_dir)
        temp_dir.mkdir(exist_ok=True)
        
        # Generate audio first with selected voice and language
        audio_path = temp_dir / "narration.mp3"
        generate_audio(story, str(audio_path), voice_id=voice_id, language=language)
        
        # Get audio duration - try multiple methods
        audio_duration = 30  # Default fallback
        
        # Try MoviePy first (most reliable)
        if MOVIEPY_AVAILABLE:
            try:
                audio_clip = AudioFileClip(str(audio_path))
                audio_duration = audio_clip.duration
                audio_clip.close()
            except:
                pass
        # Try FFmpeg probe as backup
        elif FFMPEG_AVAILABLE:
            try:
                probe = ffmpeg.probe(str(audio_path))
                audio_duration = float(probe['streams'][0]['duration'])
            except:
                pass
        
        scene_duration = audio_duration / len(scenes)
        
        # Generate a SINGLE AI scenery image for the entire video
        culture_short = culture.split(' ', 1)[1] if ' ' in culture else culture
        image_paths = []
        
        # Create a single background image for the whole video
        single_img_path = temp_dir / "background.png"
        
        # Generate artistic background image for video
        bg_img = generate_cultural_background(culture_short, width=854, height=480, title=title)
        bg_img.save(str(single_img_path), quality=95)
        
        # Use the same image for all scenes
        for i in range(len(scenes)):
            image_paths.append(str(single_img_path))
        
        # Generate SRT subtitle file - one sentence at a time
        srt_path = temp_dir / "captions.srt"
        
        # Format time as HH:MM:SS,mmm
        def format_srt_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
        # Split all text into sentences
        import re
        all_sentences = []
        for scene_text in scenes:
            # Split by sentence-ending punctuation
            sentences = re.split(r'(?<=[.!?])\s+', scene_text.strip())
            sentences = [s.strip() for s in sentences if s.strip()]
            all_sentences.extend(sentences)
        
        # Calculate time per sentence based on word count (better sync)
        # Estimate speaking rate: ~150 words per minute = 2.5 words per second
        total_words = sum(len(s.split()) for s in all_sentences)
        if total_words > 0:
            time_per_word = audio_duration / total_words
        else:
            time_per_word = 0.4  # Default: 0.4 seconds per word
        
        with open(srt_path, 'w', encoding='utf-8') as srt_file:
            current_time = 0
            for i, sentence in enumerate(all_sentences):
                word_count = len(sentence.split())
                sentence_duration = word_count * time_per_word
                
                # Exact timing - no overlap, no lead time
                start_time = current_time
                end_time = current_time + sentence_duration - 0.05  # Small gap to prevent overlap
                current_time = current_time + sentence_duration
                
                # Write SRT entry - one sentence at a time
                srt_file.write(f"{i + 1}\n")
                srt_file.write(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n")
                srt_file.write(f"{sentence}\n\n")
        
        video_path = temp_dir / "story_video.mp4"
        
        # Try Movis first for best quality with animations
        if MOVIS_AVAILABLE:
            try:
                # Create composition with movis
                composition = mv.Composition(size=(1280, 720), duration=audio_duration)
                
                # Add each scene with zoom animation and crossfade
                for i, img_path in enumerate(image_paths):
                    start_time = i * scene_duration
                    
                    # Create image layer with Ken Burns zoom effect
                    layer = mv.layer.Image(img_path, duration=scene_duration + 0.5)  # Slight overlap for crossfade
                    
                    # Add subtle zoom animation (1.0 to 1.1 scale)
                    layer.scale.enable_motion().extend([0, scene_duration], [1.0, 1.05])
                    
                    # Add layer to composition
                    composition.add_layer(layer, name=f"scene_{i}", offset=start_time)
                    
                    # Add crossfade by controlling opacity
                    if i > 0:
                        layer.opacity.enable_motion().extend([0, 0.5], [0, 1.0])  # Fade in
                
                # Add audio track
                audio_layer = mv.layer.Audio(str(audio_path))
                composition.add_layer(audio_layer, name="narration")
                
                # Export video
                video_path = temp_dir / "story_video.mp4"
                composition.write_video(str(video_path), fps=30, codec="libx264", audio_codec="aac")
                
                # Cleanup images
                for img_path in image_paths:
                    if os.path.exists(img_path):
                        os.remove(img_path)
                
                return str(video_path), str(srt_path), None
                
            except Exception as e:
                pass  # Fall back to MoviePy
        
        # Fallback to MoviePy
        if MOVIEPY_AVAILABLE:
            try:
                audio_clip = AudioFileClip(str(audio_path))
                
                clips = []
                for i, img_path in enumerate(image_paths):
                    clip = ImageClip(img_path).with_duration(scene_duration)
                    clips.append(clip)
                
                final_clip = concatenate_videoclips(clips, method="compose")
                final_clip = final_clip.with_audio(audio_clip)
                
                # Export video
                video_path = temp_dir / "story_video.mp4"
                final_clip.write_videofile(
                    str(video_path),
                    fps=24,
                    codec='libx264',
                    audio_codec='aac',
                    logger=None
                )
                
                final_clip.close()
                audio_clip.close()
                
                # Cleanup images
                for img_path in image_paths:
                    if os.path.exists(img_path):
                        os.remove(img_path)
                
                return str(video_path), str(srt_path), None
                
            except Exception as e:
                pass  # Try next method
        
        # Fallback to imageio
        if IMAGEIO_AVAILABLE:
            video_path = temp_dir / "story_video.mp4"
            writer = imageio.get_writer(str(video_path), fps=24)
            
            for img_path in image_paths:
                img = imageio.imread(img_path)
                for _ in range(int(scene_duration * 24)):
                    writer.append_data(img)
            
            writer.close()
            
            # Cleanup images
            for img_path in image_paths:
                if os.path.exists(img_path):
                    os.remove(img_path)
            
            return str(video_path), str(srt_path), None
        
        return None, None, "No video library available"
        
    except Exception as e:
        return None, None, str(e)

# Initialize session state
if 'story_data' not in st.session_state:
    st.session_state['story_data'] = None
if 'audio_path' not in st.session_state:
    st.session_state['audio_path'] = None
if 'video_path' not in st.session_state:
    st.session_state['video_path'] = None
if 'vtt_content' not in st.session_state:
    st.session_state['vtt_content'] = None
if 'translated_story' not in st.session_state:
    st.session_state['translated_story'] = None
if 'show_captions' not in st.session_state:
    st.session_state['show_captions'] = True

# Main generate button
if st.sidebar.button("Generate Story", type="primary", use_container_width=True):
    # --- Guardrail: check if custom prompt is on-topic ---
    prompt_is_relevant, off_topic_reason = is_prompt_on_topic(custom_prompt)
    if not prompt_is_relevant:
        st.warning("WARNING!! " + off_topic_reason)
        st.info(
            "**Tip:** Ikshanam is your gateway to the world's cultural heritage. "
            "Try prompts like:\n"
            "- *\"A tale of a wise old turtle\"*\n"
            "- *\"Story about a festival of lights\"*\n"
            "- *\"A warrior who learned humility\"*"
        )
    else:
      with st.spinner("Weaving your cultural tale..."):
        # Always generate story in English first
        story_text, error = generate_story(culture, story_type, tone, "English", custom_prompt)
        
        if error:
            st.error(f"Error generating story: {error}")
        else:
            # Parse the English story
            parsed_story = parse_story(story_text)
            
            # Translate if non-English language selected (silently, as part of generation)
            if story_language and story_language.lower() != "english" and TRANSLATOR_AVAILABLE:
                try:
                    # Create translator with target language
                    translator = GoogleTranslator(source='en', target=story_language.lower())
                    
                    # Translate title
                    if parsed_story['title'] and parsed_story['title'] != "A Unique Tale":
                        translated_title = translator.translate(parsed_story['title'])
                        if translated_title:
                            parsed_story['title'] = translated_title
                    
                    # Translate story in chunks (Google Translate has character limits)
                    if parsed_story['story']:
                        full_story = parsed_story['story']
                        # Split into smaller chunks (max ~4000 chars each)
                        chunks = []
                        current_chunk = ""
                        for para in full_story.split('\n'):
                            if len(current_chunk) + len(para) < 4000:
                                current_chunk += para + '\n'
                            else:
                                if current_chunk:
                                    chunks.append(current_chunk)
                                current_chunk = para + '\n'
                        if current_chunk:
                            chunks.append(current_chunk)
                        
                        # Translate each chunk
                        translated_chunks = []
                        for chunk in chunks:
                            if chunk.strip():
                                translated = translator.translate(chunk.strip())
                                if translated:
                                    translated_chunks.append(translated)
                        
                        parsed_story['story'] = '\n'.join(translated_chunks)
                    
                    # Translate moral
                    if parsed_story.get('moral'):
                        translated_moral = translator.translate(parsed_story['moral'])
                        if translated_moral:
                            parsed_story['moral'] = translated_moral
                            
                except Exception as e:
                    pass  # Silently fall back to English if translation fails
            
            # Store in session state - reset media
            st.session_state['story_data'] = parsed_story
            st.session_state['culture'] = culture
            st.session_state['story_type'] = story_type
            st.session_state['tone'] = tone
            st.session_state['story_language'] = story_language
            st.session_state['audio_path'] = None
            st.session_state['video_path'] = None
            st.session_state['translated_story'] = None
            st.session_state['dictionary_input'] = ""  # Clear dictionary search field
            st.session_state['translation_input'] = ""  # Clear translation language field
            st.session_state['custom_image_prompt'] = ""  # Clear custom image prompt field
            st.session_state['generated_image'] = None  # Clear generated image
            
            # Auto-generate AI story background image
            import base64
            culture_short = culture.split(' ', 1)[1] if ' ' in culture else culture
            story_title = parsed_story.get('title', '')
            bg_prompt = (
                f"{culture_short} cultural scene, {story_title}, "
                f"traditional folklore art, vibrant colors, detailed illustration, cinematic"
            )
            bg_data_url, _bg_err = generate_ai_image(
                prompt=bg_prompt,
                hf_token=hf_token,
                width=800,
                height=400,
                fallback_culture=culture_short,
                fallback_title=story_title,
            )
            st.session_state['bg_image_url'] = bg_data_url
      # (end of the else block from the on-topic guardrail)

# Display story if available, otherwise show welcome page
if st.session_state.get('story_data'):
    data = st.session_state['story_data']
    current_culture = st.session_state.get('culture', culture)
    current_type = st.session_state.get('story_type', story_type)
    current_tone = st.session_state.get('tone', tone)
    bg_image_url = st.session_state.get('bg_image_url', '')
    
    # IKSHANAM branding header (smaller version of welcome page)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h1 style="font-family: 'Permanent Marker', cursive; font-size: 2rem; letter-spacing: 3px; margin-bottom: 0; color: #D4AF37;">IKSHANAM</h1>
        <h2 style="font-family: 'Old English Text MT', 'UnifrakturMaguntia', 'Luminari', fantasy; font-size: 1rem; margin-top: 5px; margin-bottom: 0; font-weight: normal; color: #FFFFFF;">A Smart Cultural Storyteller</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Title with custom styling
    st.markdown(f'<h2 class="story-title">{data["title"]}</h2>', unsafe_allow_html=True)
    st.markdown(f'<p class="story-meta">{current_culture} • {current_type} • {current_tone}</p>', unsafe_allow_html=True)
    
    # Display background image if available
    if bg_image_url:
        st.markdown(f'''
        <div style="margin: 1rem 0; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.3); position: relative; z-index: 1;">
            <img src="{bg_image_url}" style="width: 100%; height: auto; display: block; position: relative;" alt="AI-Generated Story Illustration">
        </div>
        <p style="text-align: center; color: #888; font-size: 0.9rem; margin-top: -0.5rem;">AI-Generated Story Illustration</p>
        ''', unsafe_allow_html=True)
    
    # Story content
    st.markdown(f"""
    <div class="story-box">
        {data['story'].replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)
    
    # Moral - with translated label based on selected language
    if data['moral']:
        # Dictionary of "Moral" translations
        moral_translations = {
            "english": "Moral",
            "hindi": "नीति",
            "bengali": "নীতিকথা",
            "tamil": "நீதி",
            "telugu": "నీతి",
            "marathi": "नीति",
            "gujarati": "નીતિ",
            "kannada": "ನೀತಿ",
            "malayalam": "സാരാംശം",
            "punjabi": "ਸਿੱਖਿਆ",
            "odia": "ନୀତି",
            "sanskrit": "नीतिः",
            "urdu": "سبق",
            "maithili": "नीति",
            "spanish": "Moraleja",
            "french": "Morale",
            "german": "Moral",
            "italian": "Morale",
            "portuguese": "Moral",
            "russian": "Мораль",
            "japanese": "教訓",
            "chinese": "寓意",
            "korean": "교훈",
            "arabic": "العبرة",
            "persian": "درس",
            "turkish": "Ders",
            "greek": "Ηθικό δίδαγμα",
            "dutch": "Moraal",
            "swedish": "Moral",
            "polish": "Morał",
        }
        
        # Get the selected language and find translation
        selected_lang = st.session_state.get('story_language', 'English').lower()
        moral_label = moral_translations.get(selected_lang, "Moral")
        
        st.markdown(f"""
        <div class="moral-box">
            <strong> {moral_label}:</strong> {data['moral']}
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Media section header
    st.markdown('<h3 class="media-header">Generate Media</h3>', unsafe_allow_html=True)
    
    # Voice selection for narration using radio buttons (truly non-editable)
    st.markdown('<p style="color: #90EE90; font-weight: bold; margin-bottom: 5px;">Choose Narrator Voice:</p>', unsafe_allow_html=True)
    selected_voice_name = st.radio(
        "voice_selector",
        list(NARRATION_VOICES.keys()),
        index=0,
        horizontal=True,
        label_visibility="collapsed"
    )
    selected_voice = NARRATION_VOICES[selected_voice_name]
    
    # Media generation buttons - 2 columns (Audio & Video only)
    col1, col2 = st.columns(2)
    
    with col1:
        audio_btn = st.button("Generate Audio", use_container_width=True, key="audio_btn")
    
    with col2:
        video_btn = st.button("Generate Video", use_container_width=True, key="video_btn")
    
    # Handle audio generation
    if audio_btn:
        with st.spinner("Creating audio narration..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                story_lang = st.session_state.get('story_language', 'English')
                audio_path, error = generate_audio(data['story'], fp.name, voice_id=selected_voice, language=story_lang)
                if error:
                    st.error(f"Audio error: {error}")
                else:
                    st.session_state['audio_path'] = audio_path
                    st.rerun()
    
    # Handle video generation
    if video_btn:
        with st.spinner("Creating story video... This may take a minute."):
            with tempfile.TemporaryDirectory() as temp_dir:
                story_lang = st.session_state.get('story_language', 'English')
                video_path, srt_path, error = generate_video(data, temp_dir, voice_id=selected_voice, language=story_lang)
                if error:
                    st.error(f"Video error: {error}")
                else:
                    # Copy to persistent location
                    output_dir = Path("outputs")
                    output_dir.mkdir(exist_ok=True)
                    import shutil
                    
                    # Save video
                    final_video = output_dir / "story_video.mp4"
                    shutil.copy(video_path, str(final_video))
                    st.session_state['video_path'] = str(final_video)
                    
                    # Mark that we have a new video (to reset playback position)
                    st.session_state['new_video_generated'] = True
                    
                    # Convert SRT to VTT and store content for HTML5 video subtitles
                    if srt_path and os.path.exists(srt_path):
                        final_srt = output_dir / "captions.srt"
                        shutil.copy(srt_path, str(final_srt))
                        
                        # Convert SRT to VTT format for HTML5 video
                        with open(srt_path, 'r', encoding='utf-8') as f:
                            srt_content = f.read()
                        
                        # Convert SRT to VTT
                        vtt_content = "WEBVTT\n\n"
                        # Replace comma with period in timestamps (SRT uses comma, VTT uses period)
                        vtt_content += srt_content.replace(',', '.')
                        st.session_state['vtt_content'] = vtt_content
                    
                    st.rerun()
    
    # Display audio player
    if st.session_state.get('audio_path') and os.path.exists(st.session_state['audio_path']):
        st.markdown('<h4 class="section-header">Audio Narration</h4>', unsafe_allow_html=True)
        st.audio(st.session_state['audio_path'])
        with open(st.session_state['audio_path'], 'rb') as f:
            st.download_button("Download Audio", f.read(), "story_audio.mp3", "audio/mpeg", key="dl_audio")
    
    # Display video player with caption toggle
    has_video = st.session_state.get('video_path') and os.path.exists(st.session_state['video_path'])
    has_captions = st.session_state.get('vtt_content') is not None
    
    if has_video:
        st.markdown('<h4 class="section-header">Story Video</h4>', unsafe_allow_html=True)
        
        # Caption toggle with lime green styling - text and toggle on same line
        caption_col1, caption_col2 = st.columns([3, 1])
        with caption_col1:
            st.markdown('<p style="color: #90EE90; font-weight: bold; margin: 0; padding-top: 5px;">Show Captions</p>', unsafe_allow_html=True)
        with caption_col2:
            show_captions = st.toggle("", value=st.session_state.get('show_captions', True), key="caption_toggle", label_visibility="collapsed")
        st.session_state['show_captions'] = show_captions
        
        video_path = st.session_state['video_path']
        
        # Read video file and encode to base64 for HTML5 player
        import base64
        with open(video_path, 'rb') as f:
            video_bytes = f.read()
        video_base64 = base64.b64encode(video_bytes).decode('utf-8')
        
        # Create VTT data URL if captions are available
        vtt_track = ""
        if has_captions and show_captions:
            vtt_content = st.session_state['vtt_content']
            vtt_base64 = base64.b64encode(vtt_content.encode('utf-8')).decode('utf-8')
            vtt_track = f'''<track kind="subtitles" src="data:text/vtt;base64,{vtt_base64}" srclang="en" label="English" default>'''
        
        # Custom HTML5 video player with subtitle support and position persistence
        video_html = f'''
        <style>
            .video-container {{
                position: relative;
                width: 100%;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }}
            .video-container video {{
                width: 100%;
                display: block;
            }}
            .video-container video::cue {{
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                font-size: 22px;
                font-family: "Times New Roman", Times, serif;
                padding: 6px 12px;
                border-radius: 4px;
                line-height: 1.4;
            }}
            /* Position captions at very bottom of video */
            video::cue {{
                position: relative;
            }}
        </style>
        <div class="video-container">
            <video id="storyVideo" controls>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                {vtt_track}
                Your browser does not support the video tag.
            </video>
        </div>
        <script>
            (function() {{
                var video = document.getElementById('storyVideo');
                var timeKey = 'storyVideoTime';
                var playingKey = 'storyVideoPlaying';
                var newVideoKey = 'newVideoGenerated';
                
                // Check if this is a newly generated video
                var isNewVideo = {str(st.session_state.get('new_video_generated', False)).lower()};
                
                if (isNewVideo) {{
                    // Clear saved position for new video
                    localStorage.removeItem(timeKey);
                    localStorage.removeItem(playingKey);
                    video.currentTime = 0;
                }} else {{
                    // Restore saved position on load
                    var savedTime = localStorage.getItem(timeKey);
                    var wasPlaying = localStorage.getItem(playingKey) === 'true';
                    
                    if (savedTime) {{
                        video.currentTime = parseFloat(savedTime);
                    }}
                    
                    // Auto-play if video was playing before toggle
                    if (wasPlaying) {{
                        video.play().catch(function(e) {{
                            console.log('Autoplay prevented:', e);
                        }});
                    }}
                }}
                
                // Save position and playing state
                video.addEventListener('timeupdate', function() {{
                    localStorage.setItem(timeKey, video.currentTime);
                }});
                
                video.addEventListener('play', function() {{
                    localStorage.setItem(playingKey, 'true');
                }});
                
                video.addEventListener('pause', function() {{
                    localStorage.setItem(timeKey, video.currentTime);
                    localStorage.setItem(playingKey, 'false');
                }});
                
                // Clear saved state when video ends
                video.addEventListener('ended', function() {{
                    localStorage.removeItem(timeKey);
                    localStorage.removeItem(playingKey);
                }});
            }})();
        </script>
        '''
        
        components.html(video_html, height=450)
        
        # Reset the new video flag after rendering
        if st.session_state.get('new_video_generated', False):
            st.session_state['new_video_generated'] = False
        
        # Download button
        with open(video_path, 'rb') as f:
            st.download_button(
                "Download Video",
                f.read(), 
                "story_video.mp4", 
                "video/mp4", 
                key="dl_video"
            )
    
    st.divider()
    
    # Generate Image section
    st.markdown('<h3 class="media-header">Generate Image</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #CCCCCC; font-size: 0.9rem;">Create a custom AI-generated image based on the story or your own prompt</p>', unsafe_allow_html=True)
    
    # Image generation input
    img_col1, img_col2 = st.columns([3, 1])
    
    with img_col1:
        custom_image_prompt = st.text_input(
            "Custom image prompt",
            placeholder="Optional: Enter custom instructions for the image...",
            label_visibility="collapsed",
            key="custom_image_prompt"
        )
    
    with img_col2:
        generate_image_btn = st.button("Generate", use_container_width=True, key="generate_image_btn")
    
    # Handle image generation
    if generate_image_btn:
        with st.spinner("Generating AI image..."):
            current_culture = st.session_state.get('culture', culture)
            culture_short = current_culture.split(' ', 1)[1] if ' ' in current_culture else current_culture
            story_title = data.get('title', '')

            # Build prompt: prefer user-supplied text, otherwise derive from story context
            if custom_image_prompt and custom_image_prompt.strip():
                img_prompt = custom_image_prompt.strip()
            else:
                img_prompt = (
                    f"{culture_short} cultural art style, {story_title}, "
                    f"traditional folklore illustration, vibrant colors, "
                    f"detailed mythological scene, cinematic lighting"
                )

            data_url, err = generate_ai_image(
                prompt=img_prompt,
                hf_token=hf_token,
                width=800,
                height=400,
                fallback_culture=culture_short,
                fallback_title=story_title,
            )
            if err:
                st.warning(f"AI image unavailable — showing gradient instead. ({err})")
            st.session_state['generated_image'] = data_url
            st.rerun()

    # Display generated image if available
    if st.session_state.get('generated_image'):
        st.markdown(f'''
        <div style="text-align: center; margin: 1rem 0;">
            <img src="{st.session_state['generated_image']}" style="max-width: 60%; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);" alt="Generated Image">
        </div>
        ''', unsafe_allow_html=True)
    
    st.divider()
    
    # Dictionary Lookup Section
    st.markdown('<h3 class="media-header">Dictionary Lookup</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #CCCCCC; font-size: 0.9rem;">Stuck somewhere? Look up the meaning of any word.</p>', unsafe_allow_html=True)
    
    # Dictionary input
    dict_col1, dict_col2 = st.columns([3, 1])
    
    with dict_col1:
        word_to_lookup = st.text_input(
            "Enter a word",
            placeholder="Type a word to find its meaning...",
            label_visibility="collapsed",
            key="dictionary_input"
        )
    
    with dict_col2:
        lookup_btn = st.button("Look Up", use_container_width=True, key="lookup_btn")
    
    # Handle dictionary lookup
    if lookup_btn and word_to_lookup:
        with st.spinner(f"Looking up '{word_to_lookup}'..."):
            try:
                # Use Free Dictionary API
                dict_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_to_lookup.strip().lower()}"
                dict_response = requests.get(dict_url, timeout=10)
                
                if dict_response.status_code == 200:
                    dict_data = dict_response.json()
                    if dict_data and len(dict_data) > 0:
                        word_info = dict_data[0]
                        word = word_info.get('word', word_to_lookup)
                        
                        # Get phonetic - try main phonetic first, then phonetics array
                        phonetic = word_info.get('phonetic', '')
                        if not phonetic:
                            phonetics = word_info.get('phonetics', [])
                            for p in phonetics:
                                if p.get('text'):
                                    phonetic = p.get('text')
                                    break
                        
                        # Build definition display with CYAN color scheme
                        st.markdown(f"""
                        <div style="background: rgba(0, 50, 60, 0.8); border-radius: 12px; padding: 1.5rem; border-left: 4px solid #00CED1; margin-top: 1rem;">
                            <h4 style="color: #00CED1; margin: 0 0 0.5rem 0;">{word.capitalize()}</h4>
                            <p style="color: #00FFFF; font-size: 1.2rem; font-style: italic; margin: 0 0 1rem 0;">{phonetic if phonetic else ''}</p>
                        """, unsafe_allow_html=True)
                        
                        # Display meanings by part of speech
                        meanings = word_info.get('meanings', [])
                        for meaning in meanings[:3]:  # Limit to 3 parts of speech
                            part_of_speech = meaning.get('partOfSpeech', '')
                            definitions = meaning.get('definitions', [])
                            
                            if definitions:
                                st.markdown(f"""
                                <p style="color: #FFD700; font-weight: bold; margin: 0.5rem 0;">{part_of_speech.capitalize()}</p>
                                """, unsafe_allow_html=True)
                                
                                for idx, defn in enumerate(definitions[:2], 1):  # Limit to 2 definitions per type
                                    definition_text = defn.get('definition', '')
                                    example = defn.get('example', '')
                                    
                                    st.markdown(f"""
                                    <p style="color: #FFFFFF; margin: 0.25rem 0 0.25rem 1rem;">{idx}. {definition_text}</p>
                                    """, unsafe_allow_html=True)
                                    
                                    if example:
                                        st.markdown(f"""
                                        <p style="color: #888888; font-style: italic; margin: 0 0 0.5rem 1.5rem;">Example: "{example}"</p>
                                        """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning(f"No definition found for '{word_to_lookup}'")
                else:
                    st.warning(f"Could not find '{word_to_lookup}' in the dictionary. Try another word.")
            except Exception as e:
                st.error(f"Error looking up word: Please try again.")
    
    st.divider()
    
    # Translation section
    st.markdown('<h3 class="media-header">Translate Story</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color: #CCCCCC; font-size: 0.9rem;">Feel the essence as if at home! Translate the story into the language of your choice</p>', unsafe_allow_html=True)
    # Translation input
    trans_col1, trans_col2 = st.columns([3, 1])
    
    with trans_col1:
        target_language = st.text_input(
            "Enter target language",
            placeholder="Enter the language of your choice, e.g. Maithili, French, etc...",
            label_visibility="collapsed",
            key="translation_input"
        )
    
    with trans_col2:
        translate_btn = st.button("Translate", use_container_width=True, key="translate_btn")
    
    # Handle translation
    if translate_btn and target_language:
        with st.spinner(f"Translating to {target_language}..."):
            translated_text, error = translate_story(
                data['story'],
                data['title'],
                data.get('moral', ''),
                target_language
            )
            if error:
                st.error(f"Translation error: {error}")
            else:
                # Parse the translated text
                translated_data = parse_story(translated_text)
                st.session_state['translated_story'] = translated_data
                st.session_state['translation_language'] = target_language
                st.rerun()
    
    # Display translated story if available
    if st.session_state.get('translated_story'):
        trans_data = st.session_state['translated_story']
        trans_lang = st.session_state.get('translation_language', 'Translated')
        
        st.markdown(f'<h4 class="section-header">Story in {trans_lang}</h4>', unsafe_allow_html=True)
        
        # Translated title
        st.markdown(f'<h3 style="color: #FFD700;">{trans_data["title"]}</h3>', unsafe_allow_html=True)
        
        # Translated story
        st.markdown(f"""
        <div class="story-box" style="background: rgba(255,200,100,0.08);">
            {trans_data['story'].replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        
        # Translated moral - use translated label for "Moral"
        if trans_data.get('moral'):
            # Get the translated word for "Moral"
            trans_moral_label = moral_translations.get(trans_lang.lower(), "Moral")
            st.markdown(f"""
            <div class="moral-box">
                <strong> {trans_moral_label}:</strong> {trans_data['moral']}
            </div>
            """, unsafe_allow_html=True)

else:
    # Welcome Page - shown when no story has been generated yet
    # Display the Ikshanam logo image at the top - fits width, no stretching
    import base64
    with open("Ikshanam.png", "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()
    st.markdown(f'''
    <div style="text-align: center; width: 100%;">
        <img src="data:image/png;base64,{img_base64}" style="max-width: 100%; height: auto; display: block; margin: 0 auto;" alt="Ikshanam">
    </div>
    ''', unsafe_allow_html=True)
    
    # Header text below the image
    st.markdown("""
    <div class="main-header" style="text-align: center; margin-top: 1rem;">
        <h1 style="font-family: 'Permanent Marker', cursive; font-size: 3.5rem; letter-spacing: 5px; margin-bottom: 0; text-align: center;">IKSHANAM</h1>
        <h2 style="font-family: 'Old English Text MT', 'UnifrakturMaguntia', 'Luminari', fantasy; font-size: 1.5rem; margin-top: 5px; margin-bottom: 10px; font-weight: normal; text-align: center;">A Smart Cultural Storyteller</h2>
        <p style="font-family: 'Times New Roman', Times, serif; font-size: 1.125rem; margin-top: 0; color: #90EE90; text-align: center;">AI-Powered Tales from Around the World</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">~ 📚 ~ ✨ ~ 🌍 ~</div>
        <h2 style="color: #FFD700; margin-bottom: 1rem;">Welcome to Ikshanam!</h2>
        <div style="color: #90EE90; font-size: 1.1rem; font-style: italic; margin-bottom: 2rem; max-width: 800px; margin-left: auto; margin-right: auto; line-height: 1.8; text-align: justify;">
            <p>Remember the golden days, where we, as children, eagerly waited to meet our grandparents and nudge them to narrate wondrous, captivating stories as we listened to them with fascination?</p>
            <p style="margin-top: 1rem;">Let us embark on this new journey of revisiting and recreating those moments, in a manner never seen before. With the power of AI coupled with the cultures and traditions flowing through generations, we are to explore enchanting stories, and nurture that inner child within ourselves.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features section
    st.markdown("""
    <div style="background: rgba(255,255,255,0.05); border-radius: 15px; padding: 2rem; margin: 1rem 0;">
        <h3 style="text-align: center; color: #FFFFFF; margin-bottom: 1.5rem;">What You Can Do</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2.5rem;">🎭</div>
                <h4 style="color: #FFD700; margin: 0.5rem 0;">Generate Stories</h4>
                <p style="color: #CCCCCC; font-size: 0.9rem;">AI-powered tales from cultures around the world, including Indian, Japanese, Greek, and more</p>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2.5rem;">🔊</div>
                <h4 style="color: #FFD700; margin: 0.5rem 0;">Audio Narration</h4>
                <p style="color: #CCCCCC; font-size: 0.9rem;">Listen to your stories with 12 natural-sounding AI voices</p>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2.5rem;">🎬</div>
                <h4 style="color: #FFD700; margin: 0.5rem 0;">Image and Video Creation</h4>
                <p style="color: #CCCCCC; font-size: 0.9rem;">Generate beautiful images and videos with the help of AI</p>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 2.5rem;">🌐</div>
                <h4 style="color: #FFD700; margin: 0.5rem 0;">Dictionary Look-up & Translation</h4>
                <p style="color: #CCCCCC; font-size: 0.9rem;">Translate stories into various languages instantly, along with lingual support</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Getting started section
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255,215,0,0.1), rgba(144,238,144,0.1)); border-radius: 15px; padding: 2rem; margin: 1rem 0; border: 1px solid rgba(255,215,0,0.3);">
        <h3 style="text-align: center; color: #90EE90; margin-bottom: 1rem;">Getting Started</h3>
        <div style="color: #FFFFFF; text-align: center;">
            <p style="font-size: 1.1rem; margin-bottom: 1rem;">
                <strong> Use the sidebar</strong> to customize your story:
            </p>
            <ol style="text-align: left; max-width: 400px; margin: 0 auto; line-height: 2;">
                <li>Choose a <strong>Culture</strong> (Indian, Japanese, Greek, etc.)</li>
                <li>Select a <strong>Story Type</strong> (Mythology, Folk Tale, Legend, etc.)</li>
                <li>Pick a <strong>Tone</strong> (Dramatic, Child-friendly, Mysterious, etc.)</li>
                <li>Pick a <strong>Language</strong> (English, Bengali, Sanskrit, Italian, etc.)</li>
                <li>Click <strong style="color: #90EE90;">Generate Story</strong></li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Cultural icons
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <p style="color: #888; font-size: 0.9rem; margin-bottom: 1rem;">A realm of cultural stories from around the world</p>
        <div style="font-size: 2rem; letter-spacing: 15px;">
            🌍 🇮🇳 🇯🇵 🇨🇳 🏛️ 🏜️ 🦅
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #CCCCCC; padding: 1rem;">
    <small>Powered by GROQ AI (Llama 3.3) • Built for Learning, by Anushtup Dutta</small>
</div>
""", unsafe_allow_html=True)
