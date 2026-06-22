"""
ingest.py — Document ingestion, cleaning, and chunking for the LA Parks Unofficial Guide.

Fetches all 10 sources, cleans the content, and produces chunks according to the
strategy in planning.md:
  - Reddit: one chunk per comment; prepend thread topic for context; skip <20 words;
    split >500 words with 50-word overlap
  - Reviews (Yelp/TripAdvisor): one chunk per review; prepend park name from # section
    headers so every chunk is self-identifying
  - Articles: sentence-boundary chunks of ~300 words with ~75-word sentence overlap
    (avoids mid-sentence cuts that lose the park name)

Saves raw text to documents/<name>.txt and all chunks to chunks.json.

MANUAL FALLBACK: Tripadvisor and Yelp block automated scrapers. If a source fails,
save the page text manually to documents/<name>.txt and re-run — the script will
use the file instead of fetching.

Reddit files may be saved as either:
  - Raw Reddit JSON (starts with "[{") — parsed automatically
  - Plain text with comments separated by "---" lines
"""

import json
import re
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

DOCUMENTS_DIR = Path("documents")
CHUNKS_FILE = Path("chunks.json")
HEADERS = {"User-Agent": "la-parks-guide/1.0 (student project)"}

SOURCES = [
    {
        "id": 1,
        "name": "reddit_la_parks_ranked",
        "type": "reddit",
        "url": "https://www.reddit.com/r/LosAngeles/comments/1tq8bqp/la_parks_are_now_ranked_93rd_out_of_100_of_the/",
    },
    {
        "id": 2,
        "name": "reddit_scenic_parks",
        "type": "reddit",
        "url": "https://www.reddit.com/r/AskLosAngeles/comments/1k6krhx/best_scenic_parks_in_la/",
    },
    {
        "id": 3,
        "name": "reddit_picnic_parks",
        "type": "reddit",
        "url": "https://www.reddit.com/r/AskLosAngeles/comments/1omxq33/best_parks_for_picnics/",
    },
    {
        "id": 4,
        "name": "discover_la_parks_guide",
        "type": "article",
        "url": "https://www.discoverlosangeles.com/things-to-do/the-guide-to-los-angeles-parks",
    },
    {
        "id": 5,
        "name": "lacity_parks_directory",
        "type": "article",
        "url": "https://recreation.parks.lacity.gov/parks",
    },
    {
        "id": 6,
        "name": "latimes_chill_parks",
        "type": "article",
        "url": "https://www.latimes.com/lifestyle/list/chill-los-angeles-parks-for-hanging-out-and-relaxing",
    },
    {
        "id": 7,
        "name": "tripadvisor_la_parks",
        "type": "article",
        "url": "https://www.tripadvisor.com/Attractions-g32655-Activities-c57-t70-Los_Angeles_California.html",
    },
    {
        "id": 8,
        "name": "yelp_la_parks",
        "type": "article",
        "url": "https://www.yelp.com/search?find_desc=Parks&find_loc=Los+Angeles%2C+CA",
    },
    {
        "id": 9,
        "name": "modern_luxury_la_parks",
        "type": "article",
        "url": "https://www.modernluxury.com/best-parks-los-angeles/",
    },
    {
        "id": 10,
        "name": "hotels_com_la_parks",
        "type": "article",
        "url": "http://de.hotels.com/go/usa/best-parks-los-angeles",
    },
]


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def _reddit_json_url(url):
    """Strip UTM params and append .json to a Reddit thread URL."""
    parsed = urlparse(url)
    clean = urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "", ""))
    return clean + ".json"


def _parse_reddit_data(data, source):
    """Extract text segments from a parsed Reddit JSON response (list of two Listings)."""
    segments = []
    try:
        post = data[0]["data"]["children"][0]["data"]
        title = post.get("title", "").strip()
        body = post.get("selftext", "").strip()
        if title:
            segments.append(f"[POST] {title}")
        if body and body not in ("[deleted]", "[removed]"):
            segments.append(clean_text(body))
    except (KeyError, IndexError):
        pass

    try:
        for child in data[1]["data"]["children"]:
            if child.get("kind") != "t1":
                continue
            comment = child["data"].get("body", "").strip()
            if comment and comment not in ("[deleted]", "[removed]"):
                segments.append(clean_text(comment))
    except (KeyError, IndexError):
        pass

    return segments


def fetch_reddit(source):
    """Return a list of text segments by fetching Reddit's JSON API."""
    json_url = _reddit_json_url(source["url"])
    try:
        res = requests.get(json_url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"  [!] Failed to fetch {source['name']}: {e}")
        return []
    return _parse_reddit_data(data, source)


def load_reddit_file(path, source):
    """
    Load a manually saved Reddit file. Handles three formats:
      - Raw Reddit JSON (file starts with '[') — parsed directly
      - Corrupted Reddit JSON — regex-extracts "body" and "title" values
      - Plain text with segments separated by '---' lines
    """
    content = path.read_text(encoding="utf-8").strip()

    if content.startswith("[") or content.startswith("{"):
        print(f"  Detected raw Reddit JSON — parsing.")
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                data = [data]
            return _parse_reddit_data(data, source)
        except json.JSONDecodeError as e:
            print(f"  [!] JSON parse error: {e} — extracting body/title fields via regex.")
            segments = _extract_reddit_text_fields(content)
            if segments:
                print(f"  Extracted {len(segments)} text segments via regex fallback.")
                return segments
            print(f"  [!] Regex extraction failed — falling back to text split.")

    # Plain text fallback: split on --- separators
    segments = [seg.strip() for seg in re.split(r"\n\s*---\s*\n", content) if seg.strip()]
    return [clean_text(seg) for seg in segments]


def _extract_reddit_text_fields(content):
    """
    Regex fallback for corrupted Reddit JSON: extract all "body" and "title" string values.
    Handles multi-line values and escaped characters.
    """
    segments = []
    # Match "body": "..." or "title": "..." with the JSON string value
    # JSON strings can contain escaped sequences; we grab everything up to the closing unescaped "
    pattern = re.compile(r'"(?:body|title|selftext)"\s*:\s*"((?:[^"\\]|\\.)*)"', re.DOTALL)
    for m in pattern.finditer(content):
        raw = m.group(1)
        # Decode JSON string escapes
        try:
            text = json.loads(f'"{raw}"')
        except (json.JSONDecodeError, ValueError):
            text = raw.replace("\\n", "\n").replace('\\"', '"')
        text = clean_text(text)
        if text and text not in ("[deleted]", "[removed]"):
            segments.append(text)
    return segments


def fetch_article(source):
    """Fetch a web page and return its main text content."""
    try:
        res = requests.get(source["url"], headers=HEADERS, timeout=15)
        res.raise_for_status()
    except Exception as e:
        print(f"  [!] Failed to fetch {source['name']}: {e}")
        return ""

    soup = BeautifulSoup(res.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
        tag.decompose()

    container = soup.find("article") or soup.find("main") or soup.find("body")
    if not container:
        return ""

    paragraphs = [
        p.get_text(separator=" ", strip=True)
        for p in container.find_all("p")
        if len(p.get_text(strip=True).split()) > 5
    ]
    return clean_text("\n\n".join(paragraphs))


# ---------------------------------------------------------------------------
# Cleaning — generic
# ---------------------------------------------------------------------------

def clean_text(text):
    """Normalize whitespace and strip markdown/HTML noise."""
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\*{1,2}|_{1,2}|~~", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Cleaning — source-specific
# ---------------------------------------------------------------------------

def clean_yelp(text):
    """
    Remove Yelp reviewer metadata lines, leaving only park headers and review content.

    Strips: reviewer names, cities, 'Elite 26', 'All-Star', dates, photo/check-in
    counts, upvote numbers, sponsored blocks, and 'See all photos' lines.
    """
    EXACT_JUNK = {
        "Elite 26", "All-Star", "Read more",
        "You Might Also Consider", "Sponsored",
        "By continuing, you agree to Yelp's Terms of Service and acknowledge Yelp's Privacy Policy.",
    }

    lines = text.split("\n")
    cleaned = []

    for line in lines:
        s = line.strip()

        if not s:
            cleaned.append("")
            continue

        # Keep park section headers
        if s.startswith("#"):
            cleaned.append(s)
            continue

        # Reviewer name line (e.g. "Lily W.", "Noriega C.") — marks a new review
        if re.match(r"^[A-Z]\w+(?:\s+[A-Z]\w*)* [A-Z]\.$", s):
            cleaned.append("---")
            continue

        if s in EXACT_JUNK:
            continue

        # Pure numbers (vote counts, page numbers, phone numbers)
        if re.match(r"^\[?O?\d[\d\s]*$", s):
            continue

        # "X photos", "X check-ins"
        if re.match(r"^\d+\s+(photos?|check-?ins?)$", s, re.IGNORECASE):
            continue

        # "X other reviews that are not currently recommended"
        if "other reviews that are not currently recommended" in s:
            continue

        # "See all photos from X for Y"
        if s.startswith("See all photos from"):
            continue

        # Date lines: "Mar 3, 2023" or "Jun 2025"
        if re.match(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d", s):
            continue

        # Reviewer location: "Culver City, CA" or "Los Angeles, CA"
        if re.match(r"^[A-Z][^,\n]+,\s+[A-Z]{2}$", s):
            continue

        # "X Leisure reviews", "X Recreation reviews"
        if re.match(r"^\d+\s+\w+\s+reviews?$", s, re.IGNORECASE):
            continue

        # Sponsored rating blocks: "5.0 (3 reviews)"
        if re.match(r"^\d+\.\d+\s+\(\d+\s+reviews?\)", s):
            continue

        # "X.X miles away from Y"
        if re.match(r"^\d+\.\d+\s+miles?\s+away", s, re.IGNORECASE):
            continue

        # "1 of 10" pagination
        if re.match(r"^\d+\s+of\s+\d+$", s):
            continue

        # Category labels like "in Fishing", "in Parks"
        if re.match(r"^in [A-Z][a-z]+$", s):
            continue

        cleaned.append(s)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned)).strip()


def clean_tripadvisor(text):
    """
    Remove TripAdvisor reviewer metadata and boilerplate.

    Strips: contributor counts, vote numbers, trip-type lines, 'Written [date]'
    disclaimers, 'Read more', 'See all X photos', and blank lines of spaces.
    """
    BOILERPLATE = "This review is the subjective opinion of a Tripadvisor member"

    lines = text.split("\n")
    cleaned = []

    for line in lines:
        s = line.strip()

        if not s:
            cleaned.append("")
            continue

        if s.startswith("#"):
            cleaned.append(s)
            continue

        # Disclaimer line
        if BOILERPLATE in s:
            continue

        # "Written Month DD, YYYY"
        if re.match(r"^Written\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", s):
            continue

        # Trip-type lines: "Mar 2025 • Solo", "Feb 2026"
        if re.match(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}", s):
            continue

        # Reviewer metadata: "City, StateX,XXX contributions"
        if re.search(r"\d[\d,]+\s+contributions?", s):
            continue

        # Pure numbers (upvote counts)
        if re.match(r"^\d+$", s):
            continue

        # "See all X photos"
        if re.match(r"^See all \d+ photos?$", s, re.IGNORECASE):
            continue

        if s == "Read more":
            continue

        cleaned.append(s)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned)).strip()


def clean_hotels(text):
    """
    Remove Hotels.com German UI elements, keeping English park descriptions.

    Strips: 'Toll für:', 'Öffnungszeiten:', 'Lage:', 'Telefon:', 'Karte',
    'Unterkünfte in der Nähe anzeigen', 'Mehr anzeigen', image card labels, etc.
    """
    GERMAN_PATTERNS = [
        r"^Toll für:",
        r"^Öffnungszeiten:",
        r"^Lage:",
        r"^Telefon:",
        r"^Unterkünfte in der Nähe anzeigen$",
        r"^Karte$",
        r"^Auch interessant$",
        r"^Franchise Card Image$",
        r"^Destination card image$",
        r"Hotels? entdecken",
        r"Hotels? in der Nähe ansehen",
        r"^Mehr anzeigen$",
    ]

    lines = text.split("\n")
    cleaned = []

    for line in lines:
        s = line.strip()
        if not s:
            cleaned.append("")
            continue
        if any(re.search(p, s) for p in GERMAN_PATTERNS):
            continue
        cleaned.append(s)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned)).strip()


def apply_source_cleaner(text, source_name):
    """Apply a source-specific cleaner if one exists, then run generic clean_text."""
    if source_name == "yelp_la_parks":
        text = clean_yelp(text)
    elif source_name == "tripadvisor_la_parks":
        text = clean_tripadvisor(text)
    elif source_name == "hotels_com_la_parks":
        text = clean_hotels(text)
    return clean_text(text)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def chunk_reddit(segments, source):
    """
    One chunk per comment. Prepends thread topic (from [POST] title) to every
    comment so queries like "scenic parks" can match anonymous recommendations.
    Skip segments < 20 words. Split segments > 500 words with 50-word overlap.
    """
    thread_topic = None
    for seg in segments:
        if seg.startswith("[POST]"):
            thread_topic = seg[7:].strip()
            break

    chunks = []
    for seg in segments:
        # [POST] lines are just the title — use for context but skip as standalone chunk
        if seg.startswith("[POST]"):
            continue
        word_list = seg.split()
        if len(word_list) < 20:
            continue
        final = f"Thread topic: {thread_topic}. Comment: {seg}" if thread_topic else seg
        final_words = final.split()
        if len(final_words) <= 500:
            chunks.append(_make_chunk(final, source))
        else:
            for sub in _split_with_overlap(final_words, chunk_size=400, overlap=50):
                chunks.append(_make_chunk(sub, source))
    return chunks


REVIEW_SOURCES = {"tripadvisor_la_parks", "yelp_la_parks"}


def chunk_reviews(text, source):
    """
    One chunk per review with the park name prepended.

    Parses # section headers as park name anchors (kept by clean_yelp /
    clean_tripadvisor). Within each section, splits on '---' markers (Yelp
    reviewer boundaries) or double newlines (TripAdvisor paragraphs).
    Prepends 'Park: <name>.' to every chunk so reviews are self-identifying
    even when the reviewer never mentions the park by name.
    """
    chunks = []
    current_park = None

    # Split on single-# headers only (## and ### are inline markers, not park names)
    parts = re.split(r'\n(#(?!#)[^\n]+)', '\n' + text)
    # parts alternates: [pre-header text, header, content, header, content, ...]

    for part in parts:
        if part.startswith('#'):
            raw = part.lstrip('#').strip()
            # Strip leading ordinal "1. " or "2. "
            current_park = re.sub(r'^\d+\.\s*', '', raw)
        else:
            if not part.strip():
                continue
            if '---' in part:
                raw_reviews = re.split(r'\n---\n', part)
            else:
                raw_reviews = part.split('\n\n')

            for review in raw_reviews:
                review_text = ' '.join(review.split())
                if len(review_text.split()) < 20:
                    continue
                final = f"Park: {current_park}. {review_text}" if current_park else review_text
                final_words = final.split()
                if len(final_words) <= 500:
                    chunks.append(_make_chunk(final, source))
                else:
                    for sub in _split_with_overlap(final_words, chunk_size=400, overlap=50):
                        chunks.append(_make_chunk(sub, source))

    return chunks


def _split_sentences(text):
    """Split on sentence-ending punctuation followed by whitespace."""
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]


def chunk_article(text, source):
    """
    Sentence-boundary chunks of ~300 words with ~75-word sentence overlap.

    Splitting on sentence boundaries (rather than raw word counts) prevents
    chunks from starting mid-sentence, which previously caused the opening
    park name to be cut into the preceding chunk.
    """
    sentences = _split_sentences(text)
    chunks = []
    current = []
    word_count = 0

    for sent in sentences:
        current.append(sent)
        word_count += len(sent.split())

        if word_count >= 300:
            chunks.append(_make_chunk(" ".join(current), source))
            # Roll back to ~75 words of overlap, keeping whole sentences
            overlap = []
            overlap_wc = 0
            for s in reversed(current):
                wc = len(s.split())
                if overlap_wc + wc > 75:
                    break
                overlap.insert(0, s)
                overlap_wc += wc
            current = overlap
            word_count = overlap_wc

    if word_count >= 20:
        chunks.append(_make_chunk(" ".join(current), source))

    return chunks


def _split_with_overlap(word_list, chunk_size=400, overlap=50):
    start = 0
    while start < len(word_list):
        yield " ".join(word_list[start : start + chunk_size])
        if start + chunk_size >= len(word_list):
            break
        start += chunk_size - overlap


def _make_chunk(text, source):
    return {
        "text": text.strip(),
        "source_name": source["name"],
        "source_type": source["type"],
        "source_url": source["url"],
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def save_raw(name, content):
    path = DOCUMENTS_DIR / f"{name}.txt"
    path.write_text(content, encoding="utf-8")
    return path


def main():
    DOCUMENTS_DIR.mkdir(exist_ok=True)
    all_chunks = []

    for source in SOURCES:
        print(f"\n[{source['id']}] {source['name']}")

        manual_path = DOCUMENTS_DIR / f"{source['name']}.txt"

        if source["type"] == "reddit":
            if manual_path.exists():
                print(f"  Using manually saved file.")
                segments = load_reddit_file(manual_path, source)
            else:
                segments = fetch_reddit(source)
                if segments:
                    save_raw(source["name"], "\n\n---\n\n".join(segments))
                    print(f"  Saved raw text → {manual_path}")

            if not segments:
                print(f"  [!] No content — skipping.")
                continue

            chunks = chunk_reddit(segments, source)

        else:  # article
            if manual_path.exists():
                print(f"  Using manually saved file.")
                raw_text = manual_path.read_text(encoding="utf-8")
            else:
                raw_text = fetch_article(source)
                if not raw_text:
                    print(f"  [!] No content retrieved.")
                    print(f"  --> Save text manually to {manual_path} and re-run.")
                    continue
                save_raw(source["name"], raw_text)
                print(f"  Saved raw text → {manual_path}")

            cleaned_text = apply_source_cleaner(raw_text, source["name"])
            if source["name"] in REVIEW_SOURCES:
                chunks = chunk_reviews(cleaned_text, source)
            else:
                chunks = chunk_article(cleaned_text, source)

        print(f"  {len(chunks)} chunks produced")
        all_chunks.extend(chunks)
        time.sleep(0.5)

    CHUNKS_FILE.write_text(
        json.dumps(all_chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n{'='*50}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Saved to: {CHUNKS_FILE}")
    print(f"\nChunks by source:")
    for name, count in Counter(c["source_name"] for c in all_chunks).items():
        print(f"  {name}: {count}")
    print(f"\nSample chunk:")
    if all_chunks:
        sample = all_chunks[0]
        print(f"  source: {sample['source_name']}")
        print(f"  words:  {len(sample['text'].split())}")
        print(f"  text:   {sample['text'][:200]}...")


if __name__ == "__main__":
    main()
