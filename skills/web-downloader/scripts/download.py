#!/usr/bin/env python3
"""
Web Downloader Script
Downloads content from a given URL, extracts readable text, and outputs it.
Usage: python3 download.py <URL> [--output FILE]
"""

import argparse
import sys
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def extract_readable_text(html: str, url: str = "") -> str:
    """Extract readable text content from HTML."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content elements
    for tag in soup(["script", "style", "nav", "footer", "header",
                      "noscript", "iframe", "form", "aside", "svg"]):
        tag.decompose()

    # Try main content areas first
    main_tags = soup.find_all(["article", "main", "[role=main]"])
    if main_tags:
        content = " ".join(t.get_text(separator="\n", strip=True) for t in main_tags)
        if len(content) > 200:
            return content

    # Fallback: extract all text
    text = soup.get_text(separator="\n", strip=True)

    # Clean up: remove excessive blank lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


def fetch_url(url: str, timeout: int = 30) -> str:
    """Fetch content from URL."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def main():
    parser = argparse.ArgumentParser(description="Download and extract readable content from a URL.")
    parser.add_argument("url", help="The URL to download content from")
    parser.add_argument("--output", "-o", help="Save output to file instead of stdout")
    args = parser.parse_args()

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    print(f"Fetching: {url}", file=sys.stderr)

    try:
        html = fetch_url(url)
        text = extract_readable_text(html, url)

        if not text.strip():
            print("Warning: No readable content extracted.", file=sys.stderr)
            sys.exit(1)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Content saved to: {args.output}", file=sys.stderr)
        else:
            print(text)

    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after 30 seconds.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"Error: Failed to connect to the URL. Check the address and try again.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP {e.response.status_code} - {e.response.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
