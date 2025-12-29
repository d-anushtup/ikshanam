"""
Video Generation Service - Uses MoviePy to create story videos
"""
import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    ImageClip, TextClip, CompositeVideoClip, AudioFileClip,
    concatenate_videoclips, ColorClip
)
from gtts import gTTS
import tempfile


# Cultural color themes
CULTURAL_THEMES = {
    "indian": {
        "primary": "#FF6B35",      # Saffron
        "secondary": "#1A472A",     # Deep Green
        "accent": "#FFD700",        # Gold
        "background": "#2D1B00",    # Dark Brown
        "text": "#FFFFFF"
    },
    "japanese": {
        "primary": "#DC143C",       # Crimson
        "secondary": "#FFB7C5",     # Cherry Blossom
        "accent": "#FFFFFF",        # White
        "background": "#1A1A2E",    # Dark Navy
        "text": "#FFFFFF"
    },
    "african": {
        "primary": "#E07C24",       # Orange
        "secondary": "#8B4513",     # Saddle Brown
        "accent": "#FFD700",        # Gold
        "background": "#1C1C1C",    # Almost Black
        "text": "#FFFFFF"
    },
    "celtic": {
        "primary": "#228B22",       # Forest Green
        "secondary": "#4169E1",     # Royal Blue
        "accent": "#C0C0C0",        # Silver
        "background": "#0D1B2A",    # Dark Blue
        "text": "#FFFFFF"
    },
    "chinese": {
        "primary": "#DC143C",       # Red
        "secondary": "#FFD700",     # Gold
        "accent": "#FFFFFF",        # White
        "background": "#1A0A0A",    # Dark Red-Black
        "text": "#FFFFFF"
    },
    "greek": {
        "primary": "#0066CC",       # Greek Blue
        "secondary": "#FFFFFF",     # White
        "accent": "#FFD700",        # Gold
        "background": "#0A1628",    # Dark Navy
        "text": "#FFFFFF"
    },
    "arabian": {
        "primary": "#C19A6B",       # Desert Sand
        "secondary": "#006400",     # Dark Green
        "accent": "#FFD700",        # Gold
        "background": "#1A1A2E",    # Dark Purple
        "text": "#FFFFFF"
    },
    "native_american": {
        "primary": "#CD853F",       # Peru/Tan
        "secondary": "#8B0000",     # Dark Red
        "accent": "#40E0D0",        # Turquoise
        "background": "#1C1C1C",    # Almost Black
        "text": "#FFFFFF"
    }
}


def get_theme(culture: str) -> dict:
    """Get color theme for a culture."""
    culture_lower = culture.lower().replace(" ", "_")
    return CULTURAL_THEMES.get(culture_lower, CULTURAL_THEMES["indian"])


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def create_scene_image(scene_text: str, scene_number: int, total_scenes: int,
                       title: str, culture: str, size: tuple = (1280, 720)) -> Image.Image:
    """Create a beautiful scene image with text overlay."""
    theme = get_theme(culture)
    width, height = size
    
    # Create gradient background
    img = Image.new('RGB', size, hex_to_rgb(theme['background']))
    draw = ImageDraw.Draw(img)
    
    # Add decorative elements
    primary_rgb = hex_to_rgb(theme['primary'])
    accent_rgb = hex_to_rgb(theme['accent'])
    
    # Top decorative bar
    draw.rectangle([0, 0, width, 8], fill=primary_rgb)
    
    # Bottom decorative bar
    draw.rectangle([0, height - 8, width, height], fill=primary_rgb)
    
    # Side accents
    draw.rectangle([0, 0, 4, height], fill=accent_rgb)
    draw.rectangle([width - 4, 0, width, height], fill=accent_rgb)
    
    # Try to load a nice font, fall back to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 48)
        scene_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 32)
        text_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 28)
    except:
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            scene_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            scene_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
    
    # Draw title at top
    title_text = title[:50] + "..." if len(title) > 50 else title
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 40), title_text, fill=accent_rgb, font=title_font)
    
    # Draw scene indicator
    scene_indicator = f"Scene {scene_number} of {total_scenes}"
    scene_bbox = draw.textbbox((0, 0), scene_indicator, font=scene_font)
    scene_width = scene_bbox[2] - scene_bbox[0]
    draw.text(((width - scene_width) // 2, 100), scene_indicator, fill=primary_rgb, font=scene_font)
    
    # Wrap and draw main text
    wrapped_text = textwrap.fill(scene_text, width=50)
    text_lines = wrapped_text.split('\n')
    
    # Calculate starting Y position to center text vertically
    line_height = 40
    total_text_height = len(text_lines) * line_height
    start_y = (height - total_text_height) // 2 + 20
    
    text_rgb = hex_to_rgb(theme['text'])
    for i, line in enumerate(text_lines):
        line_bbox = draw.textbbox((0, 0), line, font=text_font)
        line_width = line_bbox[2] - line_bbox[0]
        x = (width - line_width) // 2
        y = start_y + i * line_height
        draw.text((x, y), line, fill=text_rgb, font=text_font)
    
    # Draw culture indicator at bottom
    culture_text = f"🌍 {culture.replace('_', ' ').title()} Cultural Tale"
    culture_bbox = draw.textbbox((0, 0), culture_text, font=scene_font)
    culture_width = culture_bbox[2] - culture_bbox[0]
    draw.text(((width - culture_width) // 2, height - 60), culture_text, 
              fill=hex_to_rgb(theme['secondary']), font=scene_font)
    
    return img


def generate_audio(text: str, output_path: str) -> str:
    """Generate TTS audio from text using gTTS."""
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)
        return output_path
    except Exception as e:
        raise Exception(f"Audio generation failed: {str(e)}")


def create_story_video(story_data: dict, output_dir: str = "outputs") -> dict:
    """
    Create a complete story video with scenes and narration.
    
    Args:
        story_data: dict with 'title', 'story', 'scenes', 'culture'
        output_dir: directory to save output files
    
    Returns:
        dict with paths to generated audio and video files
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    title = story_data.get('title', 'Cultural Story')
    story = story_data.get('story', '')
    scenes = story_data.get('scenes', [])
    culture = story_data.get('culture', 'indian')
    
    # Generate safe filename
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')[:30]
    
    results = {
        "title": title,
        "audio_path": None,
        "video_path": None
    }
    
    # Generate audio narration
    audio_path = os.path.join(output_dir, f"{safe_title}_narration.mp3")
    try:
        generate_audio(story, audio_path)
        results["audio_path"] = audio_path
    except Exception as e:
        print(f"Warning: Audio generation failed: {e}")
    
    # If no scenes, create default scenes from story
    if not scenes:
        paragraphs = story.split('\n\n')
        scenes = paragraphs[:5] if paragraphs else [story[:200]]
    
    # Create video clips for each scene
    clips = []
    
    try:
        # Get audio duration for timing
        if results["audio_path"] and os.path.exists(results["audio_path"]):
            audio_clip = AudioFileClip(results["audio_path"])
            total_duration = audio_clip.duration
            scene_duration = total_duration / len(scenes)
        else:
            scene_duration = 5  # Default 5 seconds per scene
            total_duration = scene_duration * len(scenes)
        
        for i, scene_text in enumerate(scenes):
            # Create scene image
            img = create_scene_image(
                scene_text, 
                i + 1, 
                len(scenes), 
                title, 
                culture
            )
            
            # Save temporary image
            temp_img_path = os.path.join(output_dir, f"temp_scene_{i}.png")
            img.save(temp_img_path)
            
            # Create video clip from image
            clip = ImageClip(temp_img_path).set_duration(scene_duration)
            
            # Add fade effects
            clip = clip.crossfadein(0.5)
            if i < len(scenes) - 1:
                clip = clip.crossfadeout(0.5)
            
            clips.append(clip)
            
            # Clean up temp image
            try:
                os.remove(temp_img_path)
            except:
                pass
        
        # Concatenate all clips
        final_clip = concatenate_videoclips(clips, method="compose")
        
        # Add audio if available
        if results["audio_path"] and os.path.exists(results["audio_path"]):
            audio = AudioFileClip(results["audio_path"])
            final_clip = final_clip.set_audio(audio)
        
        # Write video file
        video_path = os.path.join(output_dir, f"{safe_title}_video.mp4")
        final_clip.write_videofile(
            video_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            logger=None  # Suppress verbose output
        )
        
        results["video_path"] = video_path
        
        # Cleanup
        final_clip.close()
        if 'audio' in dir():
            audio.close()
        
    except Exception as e:
        results["error"] = str(e)
        print(f"Video generation error: {e}")
    
    return results


def generate_audio_only(text: str, output_dir: str = "outputs", filename: str = "narration.mp3") -> str:
    """Generate just the audio narration."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    audio_path = os.path.join(output_dir, filename)
    generate_audio(text, audio_path)
    return audio_path
