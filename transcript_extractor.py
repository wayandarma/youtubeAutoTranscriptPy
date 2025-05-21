#!/usr/bin/env python3
"""
YouTube Transcript Extractor

A command-line tool to extract transcripts from YouTube videos using the youtube-transcript-api.
Handles URL validation, transcript retrieval, and file persistence with proper error handling.
"""

import argparse
import asyncio
import logging
import os
import re
import sys
import time
import requests
from pathlib import Path
from typing import Optional, Tuple, List
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)

# Security constants
MAX_BATCH_SIZE = 100  # Maximum number of URLs to process in batch
MAX_FILENAME_LENGTH = 255  # Maximum filename length
ALLOWED_LANGUAGES = {'en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'pl', 'ru', 'ja', 'ko', 'zh'}  # Common languages

class TranscriptError(Exception):
    """Base exception for transcript-related errors."""
    pass

class InvalidURL(TranscriptError):
    """Raised when the YouTube URL is invalid."""
    pass

class NoTranscriptAvailable(TranscriptError):
    """Raised when no transcript is available for the video."""
    pass

class LanguageNotAvailable(TranscriptError):
    """Raised when the requested language is not available."""
    pass

class VideoNotAvailable(TranscriptError):
    """Raised when the video is private, deleted, or geo-blocked."""
    pass

class SecurityError(Exception):
    """Base class for security-related errors."""
    pass

class PathTraversalError(SecurityError):
    """Raised when path traversal is detected."""
    pass

class BatchSizeError(SecurityError):
    """Raised when batch size exceeds limit."""
    pass

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments containing url/batch and optional lang
    """
    parser = argparse.ArgumentParser(
        description="Extract transcripts from YouTube videos"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--url",
        help="YouTube video URL (e.g., https://www.youtube.com/watch?v=...)",
    )
    group.add_argument(
        "--batch",
        type=Path,
        help="Path to file containing YouTube URLs (one per line)",
    )
    parser.add_argument(
        "--lang",
        help="Optional: ISO 639-1 language code (e.g., 'en' for English)",
    )
    return parser.parse_args()

def validate_url(url: str) -> str:
    """
    Validate and extract video ID from YouTube URL.
    
    Args:
        url: YouTube video URL
        
    Returns:
        str: Video ID
        
    Raises:
        InvalidURL: If URL is invalid
    """
    logging.debug(f"Validating URL: {url}")
    
    # Common YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?]+)',  # Standard and shortened URLs
        r'youtube\.com\/embed\/([^&\n?]+)',  # Embed URLs
        r'youtube\.com\/v\/([^&\n?]+)',  # Old embed URLs
    ]
    
    for pattern in patterns:
        if match := re.search(pattern, url):
            video_id = match.group(1)
            logging.debug(f"Extracted video ID: {video_id}")
            return video_id
            
    raise InvalidURL("Invalid YouTube URL format. Expected formats: youtube.com/watch?v=VIDEO_ID or youtu.be/VIDEO_ID")

def get_video_id(url: str) -> str:
    """
    Extract video ID from validated YouTube URL.
    
    Args:
        url: Valid YouTube video URL
        
    Returns:
        str: Video ID
    """
    pass

def fetch_video_title(video_id: str) -> str:
    """
    Fetch the video title using YouTube's oEmbed endpoint.
    Args:
        video_id: YouTube video ID
    Returns:
        str: Video title
    Raises:
        Exception: If the title cannot be fetched
    """
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()["title"]

def extract_transcript(url: str, lang: Optional[str] = None) -> Tuple[str, str]:
    """
    Extract transcript from YouTube video.
    
    Args:
        url: YouTube video URL
        lang: Optional ISO 639-1 language code
        
    Returns:
        Tuple[str, str]: Video title and transcript text
        
    Raises:
        InvalidURL: If URL is invalid
        NoTranscriptAvailable: If no transcript is available
        LanguageNotAvailable: If requested language is not available
        VideoNotAvailable: If video is private/deleted/geo-blocked
    """
    try:
        # Validate URL and get video ID
        video_id = validate_url(url)
        logging.debug(f"Processing video ID: {video_id}")
        
        # Get video title
        title = fetch_video_title(video_id)
        logging.debug(f"Video title: {title}")
        
        # Get available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        logging.debug(f"Available transcripts: {[t.language_code for t in transcript_list]}")
        
        # Get transcript in requested language or fall back to available ones
        if lang:
            try:
                transcript = transcript_list.find_transcript([lang])
                logging.debug(f"Found transcript in requested language: {lang}")
            except NoTranscriptFound:
                logging.debug(f"Requested language {lang} not available, falling back to alternatives")
                raise LanguageNotAvailable(f"No transcript available in language '{lang}'")
        else:
            # Get the first available transcript
            transcript = transcript_list.find_transcript(['en'])
            logging.debug("Using English transcript as default")
        
        # Fetch and concatenate transcript segments
        transcript_data = transcript.fetch()
        transcript_text = " ".join(segment.text for segment in transcript_data)
        logging.debug(f"Successfully extracted transcript ({len(transcript_text)} chars)")
        
        return title, transcript_text
        
    except (NoTranscriptFound, TranscriptsDisabled) as e:
        logging.error(f"No transcript available: {str(e)}")
        raise NoTranscriptAvailable("No transcript is available for this video")
    except VideoUnavailable as e:
        logging.error(f"Video unavailable: {str(e)}")
        raise VideoNotAvailable("Video is private, deleted, or geo-blocked")
    except CouldNotRetrieveTranscript as e:
        logging.error(f"Failed to retrieve transcript: {str(e)}")
        raise TranscriptError("Failed to retrieve transcript from YouTube")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise TranscriptError(f"An unexpected error occurred: {str(e)}")

def slugify(title: str) -> str:
    """
    Convert video title to filesystem-safe slug.
    
    Args:
        title: Video title
        
    Returns:
        str: Sanitized slug (max 100 chars)
        
    Examples:
        >>> slugify("Hello World!")
        'hello_world'
        >>> slugify("Special & Characters @#$%")
        'special_characters'
        >>> slugify("  Multiple   Spaces  ")
        'multiple_spaces'
    """
    # Convert to lowercase and replace non-alphanumeric chars with underscore
    slug = re.sub(r'[^a-z0-9]+', '_', title.lower())
    # Remove leading/trailing underscores and collapse duplicates
    slug = re.sub(r'_+', '_', slug.strip('_'))
    # Truncate to 100 chars
    return slug[:100]

def sanitize_path(path: Path) -> Path:
    """
    Sanitize file path to prevent path traversal.
    
    Args:
        path: Path to sanitize
        
    Returns:
        Path: Sanitized absolute path
        
    Raises:
        PathTraversalError: If path traversal is detected
    """
    # Convert to absolute path
    abs_path = path.resolve()
    
    # Check if path is within current directory
    if not abs_path.is_relative_to(Path.cwd()):
        raise PathTraversalError(f"Path {path} is outside current directory")
    
    return abs_path

def validate_language(lang: Optional[str]) -> Optional[str]:
    """
    Validate language code against allowed list.
    
    Args:
        lang: Language code to validate
        
    Returns:
        Optional[str]: Validated language code
        
    Raises:
        ValueError: If language code is invalid
    """
    if lang is None:
        return None
    if lang not in ALLOWED_LANGUAGES:
        raise ValueError(f"Unsupported language code: {lang}")
    return lang

def save_text(slug: str, text: str) -> Path:
    """
    Save transcript text to file with security checks.
    
    Args:
        slug: Sanitized video title
        text: Transcript text
        
    Returns:
        Path: Path to saved file
        
    Raises:
        PathTraversalError: If path traversal is detected
        OSError: If file cannot be written
    """
    # Ensure slug is safe
    if not re.match(r'^[a-z0-9_-]+$', slug):
        raise ValueError("Invalid slug format")
    
    # Create filename
    filename = f"{slug}_transcript.txt"
    if len(filename) > MAX_FILENAME_LENGTH:
        filename = filename[:MAX_FILENAME_LENGTH-4] + ".txt"
    
    # Get safe path
    output_path = sanitize_path(Path(filename))
    
    # Write file with restricted permissions
    try:
        output_path.write_text(text)
        output_path.chmod(0o644)  # rw-r--r--
    except OSError as e:
        raise OSError(f"Failed to write transcript: {e}")
    
    return output_path

def process_batch_file(batch_path: Path) -> List[str]:
    """
    Process batch file with security checks.
    
    Args:
        batch_path: Path to batch file
        
    Returns:
        List[str]: List of valid URLs
        
    Raises:
        PathTraversalError: If path traversal is detected
        BatchSizeError: If batch size exceeds limit
        ValueError: If file is empty or contains invalid URLs
    """
    # Validate batch file path
    batch_path = sanitize_path(batch_path)
    
    # Read and validate URLs
    try:
        urls = [url.strip() for url in batch_path.read_text().splitlines() if url.strip()]
    except OSError as e:
        raise OSError(f"Failed to read batch file: {e}")
    
    if not urls:
        raise ValueError("No valid URLs found in batch file")
    
    if len(urls) > MAX_BATCH_SIZE:
        raise BatchSizeError(f"Batch size {len(urls)} exceeds limit of {MAX_BATCH_SIZE}")
    
    # Validate each URL
    valid_urls = []
    for url in urls:
        try:
            validate_url(url)
            valid_urls.append(url)
        except InvalidURL as e:
            logging.warning(f"Skipping invalid URL: {e}")
    
    if not valid_urls:
        raise ValueError("No valid URLs found in batch file")
    
    return valid_urls

def spinner(done: bool = False) -> str:
    """
    Simple spinner animation for progress indication.
    
    Args:
        done: Whether the operation is complete
        
    Returns:
        str: Spinner character or completion indicator
    """
    if done:
        return "✓"
    return "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[int(time.time() * 10) % 10]

async def extract_transcript_async(url: str, lang: Optional[str] = None) -> Tuple[str, str]:
    """
    Async version of extract_transcript.
    
    Args:
        url: YouTube video URL
        lang: Optional ISO 639-1 language code
        
    Returns:
        Tuple[str, str]: Video title and transcript text
        
    Raises:
        Same exceptions as extract_transcript
    """
    # TODO: Implement proper async version of YouTubeTranscriptApi
    # Currently using sync version in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extract_transcript, url, lang)

async def process_batch(urls: List[str], lang: Optional[str] = None) -> None:
    """
    Process a batch of URLs asynchronously.
    
    Args:
        urls: List of YouTube URLs to process
        lang: Optional language code
    """
    tasks = [extract_transcript_async(url, lang) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            logging.error(f"Failed to process {url}: {str(result)}")
            continue
            
        title, transcript = result
        slug = slugify(title)
        output_path = save_text(slug, transcript)
        logging.info(f"Saved transcript for {url} to: {output_path}")

def main() -> None:
    """
    Main entry point for the transcript extractor.
    Orchestrates CLI argument parsing, transcript extraction, and file saving.
    
    Exit codes:
        0: Success
        1: Unknown error
        2: Invalid URL
        3: No transcript available
        4: Language not available
        5: Video unavailable
        6: Network error
    """
    try:
        args = parse_args()
        
        # Validate language code
        try:
            lang = validate_language(args.lang)
        except ValueError as e:
            logging.error(str(e))
            sys.exit(2)
        
        if args.batch:
            # Experimental batch processing
            logging.warning("Batch processing is experimental and may be unstable")
            try:
                urls = process_batch_file(args.batch)
                logging.info(f"Processing {len(urls)} URLs from {args.batch}")
                asyncio.run(process_batch(urls, lang))
                sys.exit(0)
            except (PathTraversalError, BatchSizeError) as e:
                logging.error(f"Security error: {str(e)}")
                sys.exit(1)
            except Exception as e:
                logging.error(f"Batch processing failed: {str(e)}")
                sys.exit(1)
        else:
            # Single URL processing
            logging.info(f"Extracting transcript for URL: {args.url}")
            print("Working", end="", flush=True)
            start_time = time.time()
            
            while True:
                try:
                    title, transcript = extract_transcript(args.url, args.lang)
                    break
                except (InvalidURL, NoTranscriptAvailable, LanguageNotAvailable, 
                       VideoNotAvailable, TranscriptError) as e:
                    raise
                except Exception as e:
                    if time.time() - start_time > 10:
                        raise TranscriptError(f"Network error: {str(e)}")
                    time.sleep(1)
                    continue
            
            print(f"\rWorking {spinner(True)}", flush=True)
            slug = slugify(title)
            output_path = save_text(slug, transcript)
            logging.info(f"Transcript saved to: {output_path}")
            sys.exit(0)
            
    except InvalidURL as e:
        logging.error(str(e))
        sys.exit(2)
    except NoTranscriptAvailable as e:
        logging.error(str(e))
        sys.exit(3)
    except LanguageNotAvailable as e:
        logging.error(str(e))
        sys.exit(4)
    except VideoNotAvailable as e:
        logging.error(str(e))
        sys.exit(5)
    except TranscriptError as e:
        logging.error(str(e))
        sys.exit(6)
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 