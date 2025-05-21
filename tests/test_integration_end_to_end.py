#!/usr/bin/env python3
"""
Integration tests for transcript_extractor.py
Tests the script's end-to-end functionality using a real YouTube video.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

class TestTranscriptExtractorIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.script_path = Path(__file__).parent.parent / "transcript_extractor.py"
        self.test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        self.test_url = f"https://www.youtube.com/watch?v={self.test_video_id}"
        
    def tearDown(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()
        
    def test_end_to_end_extraction(self):
        """Test that the script successfully extracts a transcript from a real video."""
        # Change to temporary directory
        original_dir = os.getcwd()
        os.chdir(self.temp_dir.name)
        
        try:
            # Run the script
            result = subprocess.run(
                ["python", str(self.script_path), "--url", self.test_url],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check exit code
            self.assertEqual(result.returncode, 0, 
                f"Script failed with exit code {result.returncode}. Output: {result.stdout}\nError: {result.stderr}")
            
            # Find the output file
            output_files = list(Path(".").glob("*_transcript.txt"))
            self.assertEqual(len(output_files), 1, 
                f"Expected exactly one transcript file, found {len(output_files)}")
            
            # Read and verify transcript content
            transcript_path = output_files[0]
            transcript_text = transcript_path.read_text()
            
            # Basic content checks
            self.assertGreater(len(transcript_text), 100, 
                "Transcript should be longer than 100 characters")
            self.assertIn("never gonna give you up", transcript_text.lower(), 
                "Transcript should contain expected lyrics")
            
            # Verify file naming
            self.assertTrue(transcript_path.name.startswith("rick_astley"), 
                "Filename should be slugified from video title")
            self.assertTrue(transcript_path.name.endswith("_transcript.txt"), 
                "Filename should end with _transcript.txt")
            
        finally:
            # Restore original directory
            os.chdir(original_dir)
            
    def test_language_specific_extraction(self):
        """Test that the script handles language specification correctly."""
        os.chdir(self.temp_dir.name)
        
        try:
            # Run with English language specified
            result = subprocess.run(
                ["python", str(self.script_path), "--url", self.test_url, "--lang", "en"],
                capture_output=True,
                text=True,
                check=True
            )
            
            self.assertEqual(result.returncode, 0, 
                f"Script failed with English language. Output: {result.stdout}\nError: {result.stderr}")
            
            # Verify transcript exists and has content
            output_files = list(Path(".").glob("*_transcript.txt"))
            self.assertEqual(len(output_files), 1)
            transcript_text = output_files[0].read_text()
            self.assertGreater(len(transcript_text), 100)
            
        finally:
            os.chdir(original_dir)
            
    def test_invalid_url_handling(self):
        """Test that the script properly handles invalid URLs."""
        os.chdir(self.temp_dir.name)
        
        try:
            # Run with invalid URL
            result = subprocess.run(
                ["python", str(self.script_path), "--url", "https://youtube.com/invalid"],
                capture_output=True,
                text=True
            )
            
            # Should exit with code 2 (Invalid URL)
            self.assertEqual(result.returncode, 2, 
                f"Expected exit code 2 for invalid URL, got {result.returncode}")
            self.assertIn("Invalid YouTube URL", result.stderr)
            
        finally:
            os.chdir(original_dir)

if __name__ == '__main__':
    unittest.main() 