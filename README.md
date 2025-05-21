# YouTube Transcript Extractor

A robust Python CLI tool for extracting transcripts from YouTube videos. Uses the official YouTube timed-text API via `youtube-transcript-api` for reliable, quota-free transcript retrieval.

## Features

- Extract full transcripts from any public YouTube video
- Support for auto-generated captions
- Language selection with graceful fallback
- Clean, slugified filenames
- Progress indication and informative error messages
- Comprehensive error handling

## Installation

```bash
# Create and activate virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install youtube-transcript-api
```

## Usage

Basic usage:

```bash
python transcript_extractor.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

With language specification:

```bash
python transcript_extractor.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --lang en
```

Output:

- Creates `<video_title>_transcript.txt` in current directory
- Shows progress spinner during extraction
- Displays final file path on success

## Error Handling

Exit codes:

- 0: Success
- 1: Unknown error
- 2: Invalid URL
- 3: No transcript available
- 4: Language not available
- 5: Video unavailable (private/deleted/geo-blocked)
- 6: Network error

## Edge Cases & Notes

- URLs supported: youtube.com/watch?v=, youtu.be/, embed URLs
- Falls back to English if requested language unavailable
- Handles network issues with retries
- Truncates filenames to 100 chars
- Preserves Unicode characters in titles
- No YouTube Data API quota required

## Development

### Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m unittest discover tests
```

### Project Structure

```
transcript_extractor.py  # Main script
tests/
  ├── test_slugify.py           # Unit tests
  └── test_integration_end_to_end.py  # Integration tests
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Testing

- Unit tests: `python -m unittest tests/test_slugify.py`
- Integration tests: `python -m unittest tests/test_integration_end_to_end.py`
- Test coverage: `coverage run -m unittest discover tests`

## License

MIT License - see LICENSE file for details

## Running the Web App

The transcript extractor is also available as a user-friendly web application built with Streamlit.

### Installation

```bash
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run streamlit_app.py
```

This will start a local web server and open the application in your default browser. The web interface provides:

- A simple form to paste YouTube URLs
- Language selection dropdown
- One-click transcript extraction
- Direct download of transcripts as text files
- Preview of extracted content

![Web App Screenshot](screenshots/web_app.png)

_Note: Replace the screenshot placeholder with an actual screenshot of your web app once deployed._
