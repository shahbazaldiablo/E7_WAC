# Eagle7 Website Audit Crawler (E7_WAC)

Welcome! **E7_WAC** is a powerful but easy-to-use tool that scans your website for broken links, missing images, and SEO issues. Once it finishes, it hands you a beautifully formatted Excel report showing exactly what needs to be fixed.

Whether you are a beginner looking to check a single website or a developer needing deep technical data, this guide will get you up and running in minutes.

---

## 🟢 Quick Start Guide (For Beginners)

Don't know much about coding? No problem! Just follow these exact steps.

### Step 1: Install Python
You need a free program called Python installed on your computer to run this tool.
- Go to [Python.org](https://www.python.org/downloads/) and download the latest version.
- **IMPORTANT FOR WINDOWS USERS:** When running the installer, make sure you check the box that says **"Add Python to PATH"** before you click Install.

### Step 2: Download this Tool
- Scroll to the top of this GitHub page.
- Click the green **"<> Code"** button.
- Click **"Download ZIP"**.
- Extract/Unzip that downloaded folder somewhere on your computer (like your Desktop).

### Step 3: Open your Terminal / Command Prompt
- **On Windows:** Press the `Windows` key, type `cmd`, and hit Enter.
- **On Mac:** Press `Command + Space`, type `Terminal`, and hit Enter.

Now, navigate into the folder you just unzipped. (Tip: You can type `cd ` and then drag and drop the unzipped folder directly into the terminal window and press Enter!)

### Step 4: Install the Requirements
Run this command to install the required background files:
- **Windows:** `pip install -r requirements.txt`
- **Mac:** `pip3 install -r requirements.txt`

### Step 5: Run your First Audit!
You're ready! Just tell the tool which website you want to scan:
- **Windows:** `python website_audit_crawler.py https://yourwebsite.com`
- **Mac:** `python3 website_audit_crawler.py https://yourwebsite.com`

*Sit back and let it run! When it finishes, you will find a brand new folder containing your `.xlsx` Excel report right next to the script.*

---

## 🎯 How to Choose Your Audit Mode

A core philosophy of E7 WAC is: *"Don't use a hammer when a needle is needed."* 

If you have a 1,000-page website but only want to know which images are broken, you shouldn't have to wait hours for a full SEO scan. You can tell the tool exactly what you want using the `--mode` flag:

| What do you want to find? | Command to run |
| :--- | :--- |
| **I want everything!** (Full check) | `python website_audit_crawler.py https://website.com --mode full` |
| **Only broken images/logos.** | `python website_audit_crawler.py https://website.com --mode images` |
| **Only broken links/pages.** | `python website_audit_crawler.py https://website.com --mode links` |
| **Only check SEO tags (Titles/H1s).** | `python website_audit_crawler.py https://website.com --mode seo` |
| **Check server health & redirects.** | `python website_audit_crawler.py https://website.com --mode technical` |
| **Map sitemaps & WordPress posts.** | `python website_audit_crawler.py https://website.com --mode content` |

*(Mac users: Remember to use `python3` instead of `python`!)*

---

## 🛑 How to Pause, Stop, or Resume

Because large websites can take a long time to scan, we've made it incredibly safe to stop the tool.

- **To Stop:** Press **`Ctrl+C`** on your keyboard. The tool will safely save all your progress into the database and Excel file before shutting down. 
- **To Resume:** Just run the exact same command you used to start the scan! The tool will say `Existing scan found`, ask you if you want to start over, and if you wait 10 seconds, it will seamlessly pick up exactly where it left off.
- **To Pause (Windows Only):** Press the **`P`** key on your keyboard. The crawler will finish what it's doing, print `SCAN PAUSED`, and wait for you to press `P` again.

---

## 📊 Where is my Report?

For every scan, a dedicated folder is created automatically (for example: `example.com_website_audit_20260818_153000/`).

Inside that folder, you will find:
1. **The Excel Report (`.xlsx`)**: This is the file you want. It has multiple tabs separating your 404 errors, your SEO data, and your external links. It also features a **"Unique Issues"** tab, which groups errors together (so if one missing font appears on 400 pages, it only shows up as 1 single issue to fix!).
2. **The Database (`.db`)**: The memory of the crawler. Do not delete this if you plan on resuming your scan!
3. **The Raw Data (`.csv`)**: A giant, unformatted spreadsheet containing every single piece of data the tool found.

---

---

## ⚙️ Advanced Technical Details (For Developers)

For software engineers and technical SEOs, E7 WAC is an enterprise-grade auditing tool built for scale, precision, and stability. 

### Deep Discovery Mechanics
Standard crawlers just follow `<a>` tags. Eagle7 goes deeper to find "orphan" pages and hidden endpoints before the standard HTML crawl even begins:
*   **WordPress REST API Probing**: Queries `/wp-json/wp/v2/types` to discover every public Post, Page, and Custom Post Type directly from the database.
*   **Sitemap & Robots.txt Parsing**: Automatically checks `robots.txt` for sitemap directives and parses XML sitemaps to seed the queue.
*   **CSS Regex Extraction**: In `--mode images`, it actively downloads external `.css` stylesheets and uses Regex to extract and validate `background-image: url(...)` references.

### Staging & Legacy Domain Detection
Post-migration sites often accidentally leave links pointing to development environments. Eagle7 actively scans URLs against known environment patterns (`staging.`, `dev.`, `.local`, `localhost`, `127.0.0.1`, etc.).
*   Instead of marking these as standard links, they are isolated into a **Potential Legacy/Staging Domain** classification, **even if they return a 200 OK.** 

### Accurate 3xx Redirect Chain Tracking
Most basic crawlers blindly follow a redirect and report a `200 OK` final destination, hiding the redirect completely. Eagle7 disables automatic redirects in Python's `requests` library and manually walks the chain. For every redirected URL, it records the `Initial Status`, the `Redirect Chain`, and the `Final Status`.

### Bulletproof Stability & Performance
*   **Real-time SQLite Streaming**: Every discovered queue item and processed result is instantly written to disk. The crawler's RAM footprint remains flat regardless of site size.
*   **URLLib3 Retries**: Built-in HTTP adapters with exponential backoff silently handle intermittent `500` server errors and `429 Too Many Requests` rate limits.
*   **Smart HEAD Requests**: Uses lightweight `HEAD` requests for external domains and massive binaries (`.mp4`, `.zip`, `.pdf`) to check status without wasting bandwidth or triggering CDNs.
*   **Thread Pooling**: Evaluates up to 10 resources simultaneously per page using `concurrent.futures`.

### CLI Arguments
```bash
--mode [full|images|links|seo|technical|content]
--new              # Force a brand new scan (Bypasses the 10-second prompt)
--resume           # Force resume an existing scan
--workers 10       # Max concurrent threads
--timeout 20       # Request timeout in seconds
--ignore-robots    # Disregards robots.txt blocks
```

---

## 📄 License & Terms of Use

Use this tool for whatever you'd like, including for processing images as part of a commercial project! 

*   You **MAY NOT** repackage this tool and sell it, and any variations or improvements of this tool that are released must remain under the same license, and must include the name **"Eagle7 Website Audit Crawler"** or **"E7_WAC"**.
*   You **MAY NOT** offer inference with this model as a paid API service. 

If you run a commercial software package or inference service and wish to incorporate this tool into your software, shoot us an email to work out an agreement! We promise we're easy to work with: [shahbaz@eagle7.in](mailto:shahbaz@eagle7.in). 

Outside of the stipulations listed above, this license is effectively a variation of [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).
