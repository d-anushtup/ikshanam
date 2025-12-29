"""
Smart Cultural Storyteller - Flask Application
A web app that generates cultural stories with text, audio, and video
"""
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv

from story_service import generate_story, get_available_cultures, initialize_ai
from video_service import create_story_video, generate_audio_only

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Ensure outputs directory exists
OUTPUTS_DIR = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# Global model instance
ai_model = None


def get_model():
    """Get or initialize AI model."""
    global ai_model
    if ai_model is None:
        try:
            ai_model = initialize_ai()
        except ValueError as e:
            return None, str(e)
    return ai_model, None


@app.route('/')
def index():
    """Render the main page."""
    cultures = get_available_cultures()
    return render_template('index.html', cultures=cultures)


@app.route('/api/cultures', methods=['GET'])
def api_cultures():
    """Get available cultures."""
    return jsonify({"cultures": get_available_cultures()})


@app.route('/api/generate-story', methods=['POST'])
def api_generate_story():
    """Generate a cultural story."""
    data = request.json
    prompt = data.get('prompt', '')
    culture = data.get('culture', 'indian')
    
    if not prompt:
        return jsonify({"error": "Please provide a story prompt"}), 400
    
    model, error = get_model()
    if error:
        return jsonify({"error": error}), 500
    
    try:
        result = generate_story(prompt, culture, model)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-audio', methods=['POST'])
def api_generate_audio():
    """Generate audio narration for a story."""
    data = request.json
    text = data.get('text', '')
    title = data.get('title', 'story')
    
    if not text:
        return jsonify({"error": "No text provided for audio generation"}), 400
    
    try:
        # Create safe filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:30]
        filename = f"{safe_title}_audio.mp3"
        
        audio_path = generate_audio_only(text, str(OUTPUTS_DIR), filename)
        return jsonify({
            "success": True,
            "audio_url": f"/outputs/{filename}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-video', methods=['POST'])
def api_generate_video():
    """Generate a story video."""
    data = request.json
    
    required_fields = ['title', 'story', 'scenes', 'culture']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        result = create_story_video(data, str(OUTPUTS_DIR))
        
        if "error" in result:
            return jsonify({"error": result["error"]}), 500
        
        # Convert paths to URLs
        response = {"success": True}
        
        if result.get("audio_path"):
            audio_filename = os.path.basename(result["audio_path"])
            response["audio_url"] = f"/outputs/{audio_filename}"
        
        if result.get("video_path"):
            video_filename = os.path.basename(result["video_path"])
            response["video_url"] = f"/outputs/{video_filename}"
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/outputs/<filename>')
def serve_output(filename):
    """Serve generated output files."""
    file_path = OUTPUTS_DIR / filename
    if file_path.exists():
        return send_file(file_path)
    return jsonify({"error": "File not found"}), 404


@app.route('/api/check-config', methods=['GET'])
def check_config():
    """Check if API key is configured."""
    api_key = os.getenv('AI_API_KEY') or os.getenv('GEMINI_API_KEY')
    return jsonify({
        "configured": bool(api_key),
        "message": "Ready to generate stories!" if api_key else "Please set AI_API_KEY environment variable"
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌍 Smart Cultural Storyteller")
    print("="*60)
    
    # Check API key
    if not (os.getenv('AI_API_KEY') or os.getenv('GEMINI_API_KEY')):
        print("\n⚠️  WARNING: AI_API_KEY not set!")
        print("   Get a free API key from your AI provider")
        print("   Then run: export AI_API_KEY='your-key-here'")
    else:
        print("\n✅ AI API key configured")
    
    print(f"\n📁 Output files will be saved to: {OUTPUTS_DIR}")
    print("\n🚀 Starting server at http://localhost:5001")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
