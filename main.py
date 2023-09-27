import streamlit as st
import requests
from pydub import AudioSegment
import os
from io import BytesIO
from dotenv import load_dotenv
from elevenlabs import generate, set_api_key, voices

# Load environment variables from .env file
load_dotenv()

# Use the API key in your script
API_KEY = os.environ.get("ELEVEN_API_KEY")
set_api_key(API_KEY)
HEADERS = {
    "Authorization": "Bearer YOUR_API_TOKEN"
}


def generate_audio(character, gender, line):
    """
    Use the Eleven Labs API to generate audio for the given line using a gender-specific voice.
    """
    
    # Get available voices
    available_voices = voices()
    print(available_voices)
    
    # Choose a voice based on gender. This is a simplified approach and can be further enhanced.
    # For now, we'll pick the first available voice that matches the gender (male/female).
    if gender[:3].lower() == "fem":
        voice = available_voices[0]
    else:
        voice = available_voices[1]        
    
    # Generate audio using Eleven Labs SDK
    audio_data = generate(text=line, voice=voice)
    
    # Assuming the audio_data is in bytes representing an mp3 format (adjust as needed)
    return AudioSegment.from_mp3(BytesIO(audio_data))

def combine_audio_segments(segments):
    """
    Combine multiple audio segments into a single segment.
    """
    combined = AudioSegment.empty()
    for segment in segments:
        combined += segment
    return combined

def main():
    st.title("Dialogue to Audio App")

    # Upload dialogue text or directly paste
    uploaded_file = st.file_uploader("Upload your dialogue text file:", type="txt")
    pasted_content = st.text_area("Or paste your dialogue content here:")

    if uploaded_file:
        content = uploaded_file.read().decode()
    elif pasted_content:
        content = pasted_content
    else:
        content = None
    if uploaded_file:
        content = uploaded_file.read().decode()

    if content:
        # Split and parse the content
        lines = content.split("\n")[1:]  # Skipping the title
        audio_segments = []

        for line in lines:
            if not line.strip():  # Skip empty lines
                continue

            # Extract character, gender, and line of text
            character, rest = line.split("] [")
            character = character[1:]
            gender, text = rest.split("] - ")
            text = text.replace('"', '')

            audio_segment = generate_audio(character, gender, text)
            audio_segments.append(audio_segment)

        # Combine audio segments
        combined_audio = combine_audio_segments(audio_segments)

        # Save combined audio to a temporary file
        combined_filename = "combined_audio.mp3"
        combined_audio.export(combined_filename, format="mp3")

        # Allow user to listen to the audio
        st.audio(combined_filename, format="audio/mp3")
        st.markdown(f"[Download the combined audio]({combined_filename})")


if __name__ == "__main__":
    main()
