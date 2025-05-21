Project Brief — YouTube Transcript Extractor (Python 3)
Prepared for: Darma
Objective version: 1.0 · Date: 21 May 2025

⸻

1. Purpose & Strategic Fit

Extracting transcripts at scale is a foundational capability for knowledge distillation pipelines (summarisation, sentiment mining, topic modelling, RAG, etc.). Automating this step prevents context-loss from manual copy-paste and creates a clean, reusable text asset. A bullet-proof extractor also future-proofs your workflow against API changes and the exponential growth of long-form YouTube content you will analyse with large-language models such as Gemini.

2. Technology Stack & Rationale

Layer Choice Rationale
Runtime Python ≥ 3.9 Mature typing, f-strings, zoneinfo, and solid LLM ecosystem.
Transcript Library youtube-transcript-api Zero-config, no YouTube Data v3 quota, supports auto-generated captions, multiple languages, raises granular exceptions.
CLI Parsing argparse (std-lib) Formal CLI > input() prompts for automation and testability.
Filename Slugging pathlib + re Cross-platform paths, sanitises titles into safe slugs.
Logging logging (std-lib) Centralised debug / info / error messages; no print-sprawl.

Strong opinion: Avoid Selenium or unofficial scraping APIs; they are brittle, slower, and violate TOS. youtube-transcript-api relies on YouTube’s public timed-text endpoints and is more stable.

Installation Commands

python -m venv .venv # recommended isolation
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install youtube-transcript-api

(Add python-dotenv if you later externalise settings.)

⸻

3. Functional Requirements

# Requirement Acceptance Criteria

F-1 Accept a YouTube URL via CLI flag (--url) Passing a valid URL triggers extraction; missing flag shows usage help.
F-2 Optional --lang parameter (ISO 639-1) When provided, transcript language matches request or fails gracefully.
F-3 Download full transcript text 100 % of caption segments concatenated in chronological order.
F-4 Persist transcript as .txt in working directory File named <slug>\_transcript.txt; slug ≤ 255 chars, no forbidden filesystem symbols.
F-5 Informative console output Progress spinner or status lines; final success message with path.

⸻

4. Non-Functional Requirements

Aspect Requirement
Resilience Must handle all documented edge-cases without uncaught exceptions.
Portability No OS-specific code; must run on macOS, Linux, Windows.
Performance Sub-second startup; network wait is the only latency contributor.
Code Quality PEP 8 compliant, type-hinted, modular functions, docstrings.

⸻

5. File-Naming Strategy
   1. Retrieve video title via YouTubeTranscriptApi.get_transcript metadata or (safer) the lightweight API call YouTubeTranscriptApi.list_transcripts(video_id).video_title.
   2. Slugify:
      • Lower-case → optional
      • Replace runs of [^A-Za-z0-9-]+ with _
      • Trim leading/trailing _ and collapse duplicates
      • Truncate to 100 chars to avoid path limits
   3. Append \_transcript.txt.

Strong opinion: Do not include publication date in filename; titles are already unique enough when slugged with video-ID fallback.

⸻

6. Script Architecture

transcript_extractor.py
│
├── main() # orchestrates CLI → fetch → save
├── parse_args() # returns Namespace(url, lang)
├── extract_transcript(url, lang) -> (title, text)
│ ├─ validate_url()
│ ├─ get_video_id()
│ └─ youtube-transcript-api calls
├── slugify(title) -> str
└── save_text(slug, text) -> Path

Each function unit-tested in tests/ using pytest and unittest.mock for network isolation.

⸻

7. Error Handling Matrix

Scenario Exception Caught User-Facing Message Exit Code
Malformed URL ValueError (custom) “The URL appears invalid. Expect format https://youtu.be/… or https://www.youtube.com/watch?v=…” 2
No captions NoTranscriptFound “Transcript unavailable for this video.” 3
Language not found TranscriptsDisabled / CouldNotRetrieveTranscript “No transcript in requested language ‘{lang}’; try without –lang.” 4
Private / deleted VideoUnavailable “Video is private, deleted, or geo-blocked.” 5
Network issues RequestException “Network error: {reason}. Check connection and retry.” 6
Unknown crash unhandled Stacktrace logged, terse message shown; program exits 1.

Use logging.error(...) for diagnostics; send only concise info to stdout.

⸻

8. User Workflow (CLI)

python transcript_extractor.py --url https://www.youtube.com/watch?v=dQw4w9WgXcQ --lang en

[INFO] Extracting transcript for “Rick Astley - Never Gonna Give You Up (Official Music Video)” …
[INFO] Transcript saved to: Rick*Astley*-_Never_Gonna_Give_You_Up_(Official_Music_Video)\_transcript.txt

⸻

9. Testing & QA Plan
   1. Unit Tests: Mock YouTubeTranscriptApi to cover success, each error branch.
   2. Integration Tests: Hit a curated list of real video IDs: with captions, without captions, private, live stream.
   3. Cross-platform: Run on GitHub Actions matrix (ubuntu-latest, windows-latest, macos-latest).
   4. Static Analysis: ruff or flake8, mypy, bandit for security linting.
   5. User Acceptance: Non-technical tester runs script on three URLs and confirms .txt output.

⸻

10. Packaging & Distribution
    • Quick start: distribute the single script plus requirements.txt.
    • Scalable option: wrap with pipx-installable entry-point (setup.cfg, console_scripts = yt-transcript = transcript_extractor:main).
    • Docker for environments where Python is unavailable (alpine-slim + venv).

⸻

11. Road-Map & Future Enhancements

Priority Enhancement Notes
High Batch mode: accept .txt list of URLs Parallel extraction with asyncio + aiohttp.
Medium Output formats: JSON, SRT, VTT Facilitate downstream subtitle editing.
Medium Language auto-translation Pipe each caption chunk through Gemini / GPT-4o for pivot-language corpora.
Low GUI wrapper with Tkinter or Textual For non-CLI users.

⸻

12. Deliverables
    1.  transcript_extractor.py — fully-commented, PEP 8, MIT-licensed.
    2.  README.md — install, usage, common issues, contribution guide.
    3.  requirements.txt — pinned dependency versions.
    4.  tests/ — unit & integration test suite.
    5.  LICENSE — MIT (permissive, commercial-friendly).

⸻

Final Thoughts

Automating transcript retrieval is a deceptively small step that unlocks compounding leverage across your entire AI content pipeline. By insisting on rigorous error handling, CLI ergonomics, and unit-tested code today, you avoid silent data losses tomorrow when scaling to hundreds of videos. Stick to youtube-transcript-api, embrace typed functions, and treat the transcript file as a canonical artefact in your knowledge-graph.

— End of brief
