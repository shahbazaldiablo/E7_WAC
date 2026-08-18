# Eagle7 Website Audit Crawler

An enterprise-grade, lightweight SEO and technical website audit crawler written in Python. 

Built for absolute robustness, precision, and speed, this crawler is uniquely tailored to surface deep architectural data (like WordPress REST API discovery and legacy/staging domain leaks) while providing massive-scale stability through SQLite persistence and safe pause/resume states. It produces actionable, deduplicated data formatted seamlessly into Excel and CSV files.

---

## 🚀 Deep Feature Set

### 1. Advanced Discovery Mechanics
Standard crawlers just click links. Eagle7 goes deeper to find "orphan" pages and hidden endpoints before the standard HTML crawl even begins:
*   **WordPress REST API Probing**: Queries `/wp-json/wp/v2/types` to discover every public Post, Page, and Custom Post Type directly from the database.
*   **Sitemap & Robots.txt Parsing**: Automatically checks `robots.txt` for sitemap directives and parses `sitemap.xml` and `sitemap_index.xml` to seed the crawl queue.
*   **Comprehensive Asset Extraction**: Parses `<a>` links, `<img>` (including `srcset`), `<source>`, `<script>`, `<link rel="stylesheet">`, inline CSS `style=""`, and CSS `url(...)`.

### 2. Intelligent Deduplication ("Unique Issues")
If your site has a broken footer image or a missing font appearing on 1,000 different pages, the crawler will not bloat your error reports with 1,000 separate issues.
*   The system differentiates between **Unique URLs** and **Total Occurrences**. 
*   It generates a dedicated **Unique Issues** report, showing you the exact broken resource, its HTTP status, how many times it occurred across the site, and the very first page it was found on.

### 3. Accurate 3xx Redirect Chain Tracking
Most basic crawlers blindly follow a redirect and report a `200 OK` final destination, hiding the redirect completely. Eagle7 disables automatic redirects and manually walks the chain. For every redirected URL, it records:
*   **Initial Status** (e.g., 301)
*   **Redirect Chain** (e.g., `/old-page/` -> `/middle-page/` -> `/new-page/`)
*   **Final Status** (e.g., 200 OK)
*   **Final URL**

### 4. Legacy, Staging & Environment Detection
Post-migration sites often accidentally leave links pointing to development environments. Eagle7 actively scans URLs against known environment patterns (`staging.`, `dev.`, `.local`, `localhost`, `127.0.0.1`, `preview.`, etc.) and automatically classifies them.
*   Instead of marking these as standard links or arbitrarily labeling them "bad", they are isolated into a **Potential Legacy/Staging Domain** classification for your investigation.

### 5. On-Page SEO Extraction
During the HTML crawl phase, the crawler extracts critical on-page SEO metrics and compiles them into a dedicated tab:
*   `<title>` tags
*   `<meta name="description">`
*   `<link rel="canonical">`
*   `<meta name="robots">` (Catch accidental `noindex` tags instantly)
*   `<h1>` headers (Flags pages with missing or multiple H1s)

### 6. Bulletproof Stability & SQLite Streaming
Designed for websites with tens of thousands of resources, this crawler does not rely on holding data in RAM.
*   **Real-time Database Writing**: Every discovered queue item, checked page, and resource result is immediately written to a local `.db` file.
*   **Safe Resume Support**: If your computer restarts or you hit `Ctrl+C` midway through a 3-hour scan, simply run the command again. The crawler will detect the existing `.db` file and seamlessly resume exactly where it left off, reusing the original timestamped folder.

### 7. Crawl Politeness & Performance
*   **Automatic Retries**: A built-in `urllib3` retry adapter with exponential backoff silently handles intermittent `500` server errors and `429 Too Many Requests` rate limits.
*   **Heavy File & External Domain Skipping**: Uses lightweight `HEAD` requests for external links and heavy file extensions (`.pdf`, `.mp4`, `.zip`) to check their status without wasting bandwidth or triggering CDN security blocks.
*   **Concurrent Threading**: Evaluates up to 10 resources simultaneously per page using thread pools, massively accelerating the crawl rate.
*   **Smoothed ETA**: Progress calculation relies on a rolling average of the last 50 processed pages, separating discovery phases from the crawl phase to give you a stable, trustworthy estimated time of completion.

---

## 💻 Installation

- Python 3.7+
- Recommended: Run inside a virtual environment.

```bash
git clone https://github.com/YOUR_USERNAME/Eagle7-Website-Audit-Crawler.git
cd Eagle7-Website-Audit-Crawler
pip install -r requirements.txt
```

---

## 🛠️ Usage & Commands

Run the crawler with your target URL. 

```bash
# Standard Run: Gives a 10-second prompt to start fresh or resume an existing scan
python website_audit_crawler_v0.7.py https://example.com

# Force a brand new scan (Bypasses prompt, ignores old data)
python website_audit_crawler_v0.7.py https://example.com --new

# Force resume an existing scan (Bypasses prompt, resumes safely)
python website_audit_crawler_v0.7.py https://example.com --resume
```

### Windows Keyboard Controls
When running in Windows PowerShell or CMD, the crawler has built-in asynchronous controls:
*   **Press `P`**: Pause or Resume the crawl. Active network requests will cleanly finish and wait.
*   **Press `Ctrl+C`**: Stop the scan gracefully. Commits pending SQLite transactions, safely shuts down threads, generates partial reports for whatever is finished, and exits so you can resume later.

---

## 📁 Output Structure

For every new scan, a completely isolated, timestamped directory is generated (e.g., `example.com_website_audit_20260818_153000/`).

Inside, you will find:
1. **`*.db`**: The authoritative SQLite database acting as the engine for the crawl.
2. **`*.csv`**: A raw, flattened dump of every single checked resource.
3. **`*.xlsx`**: The master Excel workbook, highly categorized with auto-filters and frozen headers:
    *   **Summary**: A high-level overview of total pages, resources, runtimes, and status counts (breaking down *occurrences* vs *unique URLs*).
    *   **Unique Issues**: Every 4xx/5xx/Error deduplicated to its root URL.
    *   **On-Page SEO**: Title, Meta, H1, Canonical, and Robots data for every `200 OK` page.
    *   **200 OK, 3xx Redirects, 4xx Client Errors, 5xx Server Errors, Connection Errors**
    *   **External Links**: Resources hosted off-domain.
    *   **Sitemaps**: All XML sitemap files discovered.
    *   **WP Technical**: WordPress JSON and oEmbed URLs.
    *   **Potential Staging Domains**: Any flagged dev/legacy environments.

---

## 📄 License & Terms of Use

Use this tool for whatever you'd like, including for processing images as part of a commercial project! 

*   You **MAY NOT** repackage this tool and sell it, and any variations or improvements of this tool that are released must remain under the same license, and must include the name **"Eagle7 Website Audit Crawler"**.
*   You **MAY NOT** offer inference with this model as a paid API service. 

If you run a commercial software package or inference service and wish to incorporate this tool into your software, shoot us an email to work out an agreement! We promise we're easy to work with: [shahbaz@eagle7.in](mailto:shahbaz@eagle7.in). 

Outside of the stipulations listed above, this license is effectively a variation of [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).
