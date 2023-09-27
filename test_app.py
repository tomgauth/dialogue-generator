import pytest
from main import generate_audio

# Mocking the generate function from ElevenLabs
def mock_generate(text, voice):
    return text.encode()

@pytest.fixture
def mock_eleven_generate(monkeypatch):
    monkeypatch.setattr("main.generate", mock_generate)

def test_generate_audio_female(mock_eleven_generate):
    character = "Alice"
    gender = "Female"
    line = "Hello, Bob!"
    audio = generate_audio(character, gender, line)
    
    # Check if the audio is not None
    assert audio is not None

    # Check if the returned audio data contains the line (since our mock returns the text)
    assert line in audio.decode()

def test_generate_audio_male(mock_eleven_generate):
    character = "Bob"
    gender = "Male"
    line = "Hi, Alice!"
    audio = generate_audio(character, gender, line)
    
    # Check if the audio is not None
    assert audio is not None

    # Check if the returned audio data contains the line (since our mock returns the text)
    assert line in audio.decode()

