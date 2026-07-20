---
name: web-downloader
description: Use this skill when you need to download content from a URL, extract readable text, and understand its content.
---

# Web Downloader Skill

Use this skill whenever you need to fetch content from a web URL, extract the meaningful text, and analyze/understand its content.

## When to use

* User provides a URL and asks you to read/understand/summarize what's on that page
* You need to fetch online documentation, articles, or web pages as data sources
* You need to compare information from different URLs
* You want to extract structured text content from a web page for further analysis

## How to use

### Step 1: Prepare the download script

The script is located at `/skills/web-downloader/scripts/download.py` (read-only virtual path).
Before running it, copy it to a writable temp location:

```bash
cp /skills/web-downloader/scripts/download.py /tmp/web_downloader.py
```

Alternatively, write the script content directly to `/tmp/web_downloader.py` using `write_file`.

### Step 2: Download the content

Run the download script with the target URL:

```bash
python3 /tmp/web_downloader.py <URL>
```

Optional: save to a file for further analysis:

```bash
python3 /tmp/web_downloader.py <URL> --output /tmp/web_content.txt
```

The script will:
- Fetch the HTML content with proper headers
- Extract and clean readable text (removing scripts, styles, navigation, etc.)
- Prefer main content areas (`<article>`, `<main>`, etc.)
- Output the cleaned text to stdout (or to a file with `--output`)

### Step 3: Understand the content

After downloading, read and analyze the extracted content:

- If saved to a file: use `read_file("/tmp/web_content.txt")` to read it
- If output to stdout: the content is already in the result

Then summarize, answer questions, or perform analysis based on the content.

## Error handling

If the script fails, common issues and solutions:
- **Timeout**: network issue, try again or check the URL
- **Connection Error**: URL may be incorrect or unreachable
- **HTTP Error**: site may require authentication or block automated access
- **No content extracted**: site may be JavaScript-rendered (e.g. SPA) — try fetching a different page

## Limitations

- This skill works best with **static HTML pages** (articles, documentation, blogs)
- **Single-page applications (SPAs)** that rely heavily on JavaScript rendering may not yield meaningful text
- **Login-protected pages** (paywalls, authenticated dashboards) cannot be accessed
- Very large pages may produce substantial output — use `--output` to save to file and `read_file` with `offset`/`limit` for paginated reading

## Examples

### Example 1: Fetch and summarize an article

```bash
# First copy the script
cp /skills/web-downloader/scripts/download.py /tmp/web_downloader.py
# Then fetch the URL
python3 /tmp/web_downloader.py "https://example.com/some-article"
```

Then read the output and provide a summary to the user.

### Example 2: Save to file, then read in chunks

```bash
# First copy the script
cp /skills/web-downloader/scripts/download.py /tmp/web_downloader.py
# Then fetch the URL and save to file
python3 /tmp/web_downloader.py "https://example.com/long-doc" --output /tmp/web_content.txt
```

Then:
- `read_file("/tmp/web_content.txt", limit=100)` to read first 100 lines
- `read_file("/tmp/web_content.txt", offset=100, limit=100)` for next chunk

### Example 3: Compare two pages

Launch parallel tasks to download both URLs simultaneously, then compare the results.
