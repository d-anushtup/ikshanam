/**
 * Smart Cultural Storyteller - Frontend Application
 */

// State management
const state = {
    currentStory: null,
    isGenerating: false,
    hasAudio: false,
    hasVideo: false
};

// DOM Elements
const elements = {
    cultureSelect: document.getElementById('culture-select'),
    storyPrompt: document.getElementById('story-prompt'),
    generateBtn: document.getElementById('generate-btn'),
    configWarning: document.getElementById('config-warning'),
    configMessage: document.getElementById('config-message'),
    loadingSection: document.getElementById('loading-section'),
    loadingText: document.getElementById('loading-text'),
    outputSection: document.getElementById('output-section'),
    storyTitle: document.getElementById('story-title'),
    storyCulture: document.getElementById('story-culture'),
    storyContent: document.getElementById('story-content'),
    storyMoral: document.getElementById('story-moral'),
    audioBtn: document.getElementById('audio-btn'),
    videoBtn: document.getElementById('video-btn'),
    mediaLoading: document.getElementById('media-loading'),
    mediaLoadingText: document.getElementById('media-loading-text'),
    audioContainer: document.getElementById('audio-container'),
    audioPlayer: document.getElementById('audio-player'),
    videoContainer: document.getElementById('video-container'),
    videoPlayer: document.getElementById('video-player')
};

// Culture display names with emojis
const cultureNames = {
    indian: '🇮🇳 Indian',
    japanese: '🇯🇵 Japanese',
    african: '🌍 African',
    celtic: '☘️ Celtic',
    chinese: '🇨🇳 Chinese',
    greek: '🏛️ Greek',
    arabian: '🏜️ Arabian',
    native_american: '🦅 Native American'
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    checkConfiguration();
    setupEventListeners();
});

// Check if API is configured
async function checkConfiguration() {
    try {
        const response = await fetch('/api/check-config');
        const data = await response.json();

        if (!data.configured) {
            elements.configWarning.classList.remove('hidden');
            elements.configMessage.textContent = data.message;
        }
    } catch (error) {
        console.error('Configuration check failed:', error);
    }
}

// Setup event listeners
function setupEventListeners() {
    elements.generateBtn.addEventListener('click', generateStory);
    elements.audioBtn.addEventListener('click', generateAudio);
    elements.videoBtn.addEventListener('click', generateVideo);

    // Enable Enter key to submit (with Shift+Enter for new lines)
    elements.storyPrompt.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            generateStory();
        }
    });
}

// Show loading state
function showLoading(message = 'Weaving your tale...') {
    elements.loadingSection.classList.remove('hidden');
    elements.loadingText.textContent = message;
    elements.outputSection.classList.add('hidden');
    elements.generateBtn.disabled = true;
    state.isGenerating = true;
}

// Hide loading state
function hideLoading() {
    elements.loadingSection.classList.add('hidden');
    elements.generateBtn.disabled = false;
    state.isGenerating = false;
}

// Show media loading
function showMediaLoading(message = 'Generating...') {
    elements.mediaLoading.classList.remove('hidden');
    elements.mediaLoadingText.textContent = message;
    elements.audioBtn.disabled = true;
    elements.videoBtn.disabled = true;
}

// Hide media loading
function hideMediaLoading() {
    elements.mediaLoading.classList.add('hidden');
    elements.audioBtn.disabled = false;
    elements.videoBtn.disabled = false;
}

// Generate story
async function generateStory() {
    const prompt = elements.storyPrompt.value.trim();
    const culture = elements.cultureSelect.value;

    if (!prompt) {
        alert('Please enter a story idea!');
        elements.storyPrompt.focus();
        return;
    }

    showLoading('Weaving your cultural tale...');

    try {
        const response = await fetch('/api/generate-story', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt, culture })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate story');
        }

        if (data.error) {
            throw new Error(data.error);
        }

        // Store current story
        state.currentStory = data;
        state.hasAudio = false;
        state.hasVideo = false;

        // Display the story
        displayStory(data);

    } catch (error) {
        console.error('Story generation error:', error);
        alert(`Error: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Display story in UI
function displayStory(data) {
    // Update title and culture
    elements.storyTitle.textContent = data.title || 'Untitled Story';
    elements.storyCulture.textContent = cultureNames[data.culture] || data.culture;

    // Format and display story content
    const storyText = data.story || '';
    const paragraphs = storyText.split('\n\n').filter(p => p.trim());
    elements.storyContent.innerHTML = paragraphs
        .map(p => `<p>${escapeHtml(p.trim())}</p>`)
        .join('');

    // Display moral if available
    if (data.moral) {
        elements.storyMoral.innerHTML = `<strong>✨ Moral:</strong> ${escapeHtml(data.moral)}`;
    } else {
        elements.storyMoral.innerHTML = '';
    }

    // Reset media containers
    elements.audioContainer.classList.add('hidden');
    elements.videoContainer.classList.add('hidden');

    // Show output section
    elements.outputSection.classList.remove('hidden');

    // Scroll to output
    elements.outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Generate audio narration
async function generateAudio() {
    if (!state.currentStory || !state.currentStory.story) {
        alert('Please generate a story first!');
        return;
    }

    showMediaLoading('Generating audio narration...');

    try {
        const response = await fetch('/api/generate-audio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: state.currentStory.story,
                title: state.currentStory.title
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate audio');
        }

        // Display audio player
        elements.audioPlayer.src = data.audio_url + '?t=' + Date.now(); // Cache bust
        elements.audioContainer.classList.remove('hidden');
        state.hasAudio = true;

        // Scroll to audio player
        elements.audioContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });

    } catch (error) {
        console.error('Audio generation error:', error);
        alert(`Error: ${error.message}`);
    } finally {
        hideMediaLoading();
    }
}

// Generate video
async function generateVideo() {
    if (!state.currentStory) {
        alert('Please generate a story first!');
        return;
    }

    showMediaLoading('Creating your story video... This may take a minute.');

    try {
        const response = await fetch('/api/generate-video', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(state.currentStory)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate video');
        }

        // Display video player
        if (data.video_url) {
            elements.videoPlayer.src = data.video_url + '?t=' + Date.now(); // Cache bust
            elements.videoContainer.classList.remove('hidden');
            state.hasVideo = true;
        }

        // Also update audio if generated
        if (data.audio_url && !state.hasAudio) {
            elements.audioPlayer.src = data.audio_url + '?t=' + Date.now();
            elements.audioContainer.classList.remove('hidden');
            state.hasAudio = true;
        }

        // Scroll to video player
        elements.videoContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });

    } catch (error) {
        console.error('Video generation error:', error);
        alert(`Error: ${error.message}`);
    } finally {
        hideMediaLoading();
    }
}

// Utility: Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
