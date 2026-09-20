# webcrawler

An asynchronous web crawler written in Python. Starting from a single URL, it follows links within the same domain, extracts basic information from each page, and writes the results to a JSON report.

## Features

- Concurrent crawling with `asyncio` and `aiohttp`
- Configurable maximum concurrency and maximum number of pages
- Stays on the starting domain (external links are ignored)
- URL normalization to avoid visiting the same page twice (case and trailing slashes are ignored)
- Skips pages that return HTTP errors (4xx/5xx) or non-HTML content
- Extracts the heading, first paragraph, outgoing links and image URLs of every page
- Writes a sorted JSON report to `report.json`

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) (recommended) or `pip`

Dependencies (pinned in `pyproject.toml`):

- `aiohttp`
- `beautifulsoup4`
- `requests`

## Installation

```bash
git clone https://github.com/LilacRose1/webcrawler
cd webcrawler
uv sync
```

## Usage

```bash
uv run python main.py <base_url> <max_concurrency> <max_pages>
```

| Argument          | Description                                             |
| ----------------- | ------------------------------------------------------- |
| `base_url`        | The URL to start crawling from                          |
| `max_concurrency` | Maximum number of requests in flight at the same time   |
| `max_pages`       | Maximum number of pages to crawl before stopping        |

All three arguments are required.

### Example

```bash
uv run python main.py https://example.com 5 50
```

This crawls up to 50 pages of `example.com`, with at most 5 concurrent requests, and writes the results to `report.json` in the current directory.

## Output

`report.json` contains a list of page objects sorted by URL:

```json
[
  {
    "url": "https://example.com/",
    "heading": "Example Domain",
    "first_paragraph": "This domain is for use in illustrative examples in documents.",
    "outgoing_links": ["https://www.iana.org/domains/example"],
    "image_urls": []
  }
]
```

| Field             | Description                                                            |
| ----------------- | ---------------------------------------------------------------------- |
| `url`             | The URL of the page                                                    |
| `heading`         | Text of the first `<h1>`, or the first `<h2>` if there is no `<h1>`   |
| `first_paragraph` | First `<p>` inside `<main>`, falling back to the first `<p>` on the page |
| `outgoing_links`  | Absolute URLs of all `<a href>` links on the page                      |
| `image_urls`      | Absolute URLs of all `<img src>` images on the page                    |

## Project structure

| File             | Purpose                                                          |
| ---------------- | ---------------------------------------------------------------- |
| `main.py`        | Command-line entry point                                         |
| `crawl.py`       | `AsyncCrawler` class, URL normalization and HTML extraction helpers |
| `json_report.py` | Writes the crawl results to a JSON file                          |
| `test_crawl.py`  | Unit tests for the URL and HTML helpers                          |

## Running the tests

```bash
uv run python -m unittest
```

## How it works

1. `AsyncCrawler` fetches the start page and extracts its data.
2. Each outgoing link is scheduled as a new task via `asyncio.create_task`.
3. A semaphore limits the number of concurrent requests to `max_concurrency`.
4. A lock-protected `visited` set ensures each normalized URL is crawled only once and enforces the `max_pages` limit.
5. When all tasks finish, the collected data is written to `report.json`.
