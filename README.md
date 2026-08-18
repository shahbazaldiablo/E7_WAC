# Eagle7 Website Audit Crawler

An enterprise-grade, lightweight SEO and technical website audit crawler written in Python. 

Built for robustness and speed, this crawler is uniquely tailored to surface deep architectural data (like WordPress REST API discovery and legacy/staging domain leaks) while providing massive-scale stability through SQLite persistence and safe pause/resume states.

## Features

- **Proactive Discovery**: Automatically parses `robots.txt`, XML sitemaps, and the WordPress REST API (`/wp-json/wp/v2/types`) to find orphan pages before crawling even begins.
- **SQLite Persistence & Safe Resume**: Your crawl state is streamed to a local SQLite database in real-time. Hit `Ctrl+C` to safely stop a 3-hour scan, and resume it seamlessly hours later without losing a single URL.
- **On-Page SEO Extraction**: Automatically extracts `<title>`, `<meta name="description">`, `<link rel="canonical">`, `<meta name="robots">`, and `<h1>` tags into a dedicated SEO reporting tab.
- **Deduplication & Unique Issues**: Missing a font on 400 pages? The crawler intelligently deduplicates occurrences into a `Unique Issues` tab so you aren't overwhelmed by inflated error counts.
- **Accurate Redirect Chains**: Manual tracking of 3xx redirects to map out `Initial Status` -> `Redirect Chain` -> `Final Status`, giving you a clear picture of redirect loops and lost link juice.
- **Polite External & Heavy Resource Handling**: Uses `HEAD` requests for external domains and heavy file extensions (`.pdf`, `.mp4`, `.zip`, etc.) to save bandwidth and prevent blocking.
- **Staging & Legacy Domain Detection**: Automatically surfaces and flags forgotten development, QA, and staging domains linked on production.
- **Rich Excel & CSV Reporting**: Generates heavily categorized, auto-formatted `.xlsx` workbooks and `.csv` files stored in dedicated timestamped run folders.

## Requirements

- Python 3.7+
- Recommended: Run inside a virtual environment.

```bash
pip install -r requirements.txt
```

## Usage

Run the crawler with the target URL. 
By default, the crawler will safely prompt you to resume if it detects an existing database for the target domain.

```bash
# Basic run (Includes a 10-second prompt if an existing scan is found)
python website_audit_crawler_v0.7.py https://example.com

# Force a brand new scan (ignores old data)
python website_audit_crawler_v0.7.py https://example.com --new

# Force resume an existing scan (skips the prompt)
python website_audit_crawler_v0.7.py https://example.com --resume
```

### Controls

During a scan on Windows, you can interact with the crawler safely:
- **Press `P`**: Pause / Resume the crawl. Active threads will wait safely.
- **Press `Ctrl+C`**: Stop the scan gracefully. Commits the SQLite transactions, generates partial reports, and safely shuts down so you can resume later.

## Output

For each new scan, a dedicated folder is created (e.g., `example.com_website_audit_20260818_153000/`). 
Inside, you'll find:
- **`*.db`**: The SQLite database storing the state and results.
- **`*.csv`**: The complete raw data output.
- **`*.xlsx`**: The formatted Excel workbook separated into tabs (`Summary`, `Unique Issues`, `On-Page SEO`, `200 OK`, `3xx Redirects`, `4xx Errors`, `External Links`, `Sitemaps`, etc.).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
