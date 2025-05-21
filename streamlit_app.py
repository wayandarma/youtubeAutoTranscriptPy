#!/usr/bin/env python3
"""
YouTube Transcript Extractor Web App

A Streamlit-based web interface for extracting transcripts from YouTube videos.
Provides a user-friendly way to extract and download video transcripts.
"""

import io
from pathlib import Path
from typing import Optional

import streamlit as st
from transcript_extractor import (
    extract_transcript,
    slugify,
    TranscriptError,
    InvalidURL,
    NoTranscriptAvailable,
    LanguageNotAvailable,
    VideoNotAvailable,
)

# Constants
VERSION = "1.0.0"
AUTHOR = "Darma_Vibe Code"
REPO_URL = "https://github.com/wayandarma/youtubeAutoTranscriptPy.git"

# Common languages for selection
LANGUAGES = {
    "Auto / Original": None,
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Polish": "pl",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh",
}

def display_about_sidebar() -> None:
    """Display app information in the sidebar."""
    with st.sidebar:
        st.title("About")
        st.write(f"Version: {VERSION}")
        st.write(f"Author: {AUTHOR}")
        st.write(f"[GitHub Repository]({REPO_URL})")

def get_transcript_snippet(text: str, lines: int = 3) -> str:
    """Get first N lines of transcript text."""
    return "\n".join(text.split("\n")[:lines])

def main() -> None:
    """Main Streamlit app entry point."""
    st.title("YouTube Transcript Extractor")
    st.write("Extract and download transcripts from YouTube videos.")
    
    # URL input
    url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste a YouTube video URL here",
    )
    
    # Language selection
    selected_lang = st.selectbox(
        "Caption Language",
        options=list(LANGUAGES.keys()),
        help="Select the desired caption language",
    )
    lang_code = LANGUAGES[selected_lang]
    
    # Extract button
    if st.button("Extract Transcript"):
        if not url:
            st.error("Please enter a YouTube URL")
            return
            
        try:
            with st.spinner("Extracting transcript..."):
                title, transcript = extract_transcript(url, lang_code)
                
            # Create in-memory file
            filename = f"{slugify(title)}_transcript.txt"
            transcript_file = io.StringIO(transcript)
            
            # Download button
            st.download_button(
                "Download Transcript",
                transcript_file.getvalue(),
                file_name=filename,
                mime="text/plain",
            )
            
            # Success message with snippet
            st.success(f"Transcript extracted successfully: {filename}")
            st.text("Preview:")
            st.text(get_transcript_snippet(transcript))
            
        except InvalidURL:
            st.error("Invalid YouTube URL format")
        except NoTranscriptAvailable:
            st.error("No transcript is available for this video")
        except LanguageNotAvailable:
            st.error(f"No transcript available in {selected_lang}")
        except VideoNotAvailable:
            st.error("Video is private, deleted, or geo-blocked")
        except TranscriptError as e:
            st.error(f"Failed to extract transcript: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    display_about_sidebar()
    main() 