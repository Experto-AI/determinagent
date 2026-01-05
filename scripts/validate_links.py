#!/usr/bin/env python3
"""
Link validation script for Markdown documentation.
Checks internal relative links and external HTTP(S) links.
"""

import os
import re
import sys
import concurrent.futures
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Tuple, Set

# Configuration
DOCS_DIR = Path("docs")
IGNORE_PATTERNS = [
    r"^mailto:",
    r"^#",  # Internal anchors on same page
]
# GitHub link construction for this project
REPO_URL = "https://github.com/Experto-AI/determinagent"
BRANCH = "main"

def get_markdown_files(root_dir: Path) -> List[Path]:
    return list(root_dir.rglob("*.md"))

def extract_links(file_path: Path) -> List[Tuple[str, int]]:
    """Extract links from markdown file. Returns list of (url, line_number)."""
    links = []
    content = file_path.read_text(encoding="utf-8")
    
    # Regex for standard markdown links [text](url)
    # This is a simple regex and might miss complex cases or catch false positives in code blocks
    link_pattern = re.compile(r'\[.*?\]\((.*?)\)')
    
    for i, line in enumerate(content.splitlines(), 1):
        matches = link_pattern.findall(line)
        for url in matches:
            # Clean url (remove title part if present: "url "title"")
            url = url.split(' "')[0].strip()
            links.append((url, i))
    return links

def is_ignored(url: str) -> bool:
    for pattern in IGNORE_PATTERNS:
        if re.match(pattern, url):
            return True
    return False

def check_external_link(url: str) -> Tuple[str, bool, str]:
    """Check if external URL is accessible. Returns (url, is_valid, error_msg)."""
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'DeterminAgent-LinkChecker/1.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status >= 400:
                return url, False, f"Status {response.status}"
            return url, True, ""
    except urllib.error.HTTPError as e:
        return url, False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return url, False, f"URL Error: {e.reason}"
    except Exception as e:
        return url, False, str(e)

def check_internal_link(file_path: Path, link: str) -> Tuple[str, bool, str]:
    """Check if internal relative link resolves to a file."""
    # Remove anchor
    path_part = link.split('#')[0]
    
    if not path_part:
        # Just an anchor on same page, ignored by regex filter usually but check here
        return link, True, ""

    # Resolve path relative to the file
    target_path = (file_path.parent / path_part).resolve()
    
    # Check if inside project
    try:
        # We allow linking to files outside docs/ (e.g., ../LICENSE)
        # But target must exist
        if not target_path.exists():
            return link, False, f"File not found: {target_path}"
        return link, True, ""
    except Exception as e:
        return link, False, str(e)

def validate_links():
    md_files = get_markdown_files(DOCS_DIR)
    all_links = []
    
    print(f"🔍 Scanning {len(md_files)} files in {DOCS_DIR}...")
    
    for file_path in md_files:
        links = extract_links(file_path)
        for url, line in links:
            if not is_ignored(url):
                all_links.append((file_path, url, line))

    print(f"found {len(all_links)} links. Validating...")
    
    errors = []
    external_links = set()
    
    # First pass: Internal links and collect external ones
    for file_path, url, line in all_links:
        if url.startswith("http://") or url.startswith("https://"):
            external_links.add(url)
        else:
            _, valid, msg = check_internal_link(file_path, url)
            if not valid:
                errors.append(f"{file_path}:{line} -> {url} : {msg}")

    # Second pass: Check unique external links in parallel
    print(f"Checking {len(external_links)} unique external links...")
    link_status = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_external_link, url): url for url in external_links}
        for future in concurrent.futures.as_completed(future_to_url):
            url, valid, msg = future.result()
            link_status[url] = (valid, msg)

    # Report external link errors
    for file_path, url, line in all_links:
        if url in link_status:
            valid, msg = link_status[url]
            if not valid:
                errors.append(f"{file_path}:{line} -> {url} : {msg}")

    if errors:
        print("\n❌ Found Broken Links:")
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("\n✅ All links validated successfully!")

if __name__ == "__main__":
    validate_links()
