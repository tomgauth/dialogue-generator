import streamlit as st
import genanki
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


model_id = 1607392319  # This can be any unique number. You can also randomize this as per the documentation.
dialogue_model = genanki.Model(
  model_id,
  'Dialogue Comprehension Model',
  fields=[
    {'name': 'Audio'},
    {'name': 'Text'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Audio}}',
      'afmt': '{{FrontSide}}<hr id="answer">{{Text}}',
    },
  ])

deck_id = 2059400110  # Again, this can be any unique number or randomized.
dialogue_deck = genanki.Deck(deck_id, 'DialogueDeck')

def add_dialogue_to_deck(audio_file, dialogue_text):
    global dialogue_deck
    note = genanki.Note(
      model=dialogue_model,
      fields=[f'[sound:{audio_file}]', dialogue_text])
    dialogue_deck.add_note(note)

def generate_anki_package(output_file, media_files=[]):
    my_package = genanki.Package(dialogue_deck)
    my_package.media_files = media_files
    my_package.write_to_file(output_file)

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
        media_files = []  # list to store media files for the Anki package


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

            # Save the individual audio segment with unique name
            audio_filename = f"{character}_{text[:10]}.mp3"  # taking first 10 chars of text for simplicity
            audio_segment.export(audio_filename, format="mp3")
            media_files.append(audio_filename)

            # Add to Anki deck
            add_dialogue_to_deck(audio_filename, text)            

        # Combine audio segments
        combined_audio = combine_audio_segments(audio_segments)

        # Save combined audio to a temporary file
        combined_filename = "combined_audio.mp3"
        combined_audio.export(combined_filename, format="mp3")

        # Allow user to listen to the audio
        st.audio(combined_filename, format="audio/mp3")
        st.markdown(f"[Download the combined audio]({combined_filename})")

        # Add button for generating Anki flashcards
        if st.button("Generate Anki Flashcards"):
            output_file = "dialogues_deck.apkg"
            generate_anki_package(output_file, media_files)
            st.success(f"Flashcards generated! [Download the Anki Package]({output_file})")



if __name__ == "__main__":
    main()
