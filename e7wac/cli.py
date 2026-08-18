import argparse
import os
import re
import sys
import time
from datetime import datetime
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import VERSION, DEFAULT_URL, USER_AGENT, TIMEOUT, DELAY, MAX_PAGES, MAX_RESOURCES, MAX_WORKERS
from .database import setup_db, get_state, db_add_page
from .discovery import discover_wp_and_sitemaps, clean_url
from .crawler import process_queue
from .reports import generate_reports_from_db
from .controls import is_paused

def main():
    parser = argparse.ArgumentParser(description="Eagle7 Website Audit Crawler - An enterprise-grade SEO and technical audit tool.")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL, help="Target URL to audit")
    parser.add_argument("--mode", choices=["full", "images", "links", "seo", "technical", "content"], default="full", 
                        help="Audit mode: full (default), images, links, seo, technical, content")
    parser.add_argument("--new", action="store_true", help="Force a fresh scan, bypassing any existing scan folders")
    parser.add_argument("--resume", action="store_true", help="Force resume an existing scan")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help="Number of concurrent workers for resource checking")
    parser.add_argument("--timeout", type=int, default=TIMEOUT, help="Timeout in seconds for HTTP requests")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES, help="Maximum number of pages to crawl")
    parser.add_argument("--max-resources", type=int, default=MAX_RESOURCES, help="Maximum number of resources to check")
    parser.add_argument("--ignore-robots", action="store_true", help="Ignore robots.txt crawling directives")
    parser.add_argument("--delay", type=float, default=DELAY, help="Delay in seconds between page requests")

    args = parser.parse_args()

    root = args.url
    if not root.startswith(("http://", "https://")): root = "https://" + root
    root = clean_url(root)
    if not root.endswith("/"): root += "/"
        
    netloc = urlparse(root).netloc
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^A-Za-z0-9.-]", "_", netloc)
    
    respect_robots = not args.ignore_robots

    folders = [e.name for e in os.scandir('.') if e.is_dir() and e.name.startswith(f"{safe_name}_website_audit_")]
    is_resume = False
    
    if folders:
        folder_name = sorted(folders)[-1]
        if args.new:
            print("\n-> Starting a fresh scan (--new flag provided)...")
            is_resume = False
            folder_name = f"{safe_name}_website_audit_{stamp}"
            os.makedirs(folder_name, exist_ok=True)
        elif args.resume:
            print(f"\n-> Resuming existing scan: {folder_name} (--resume flag provided)...")
            is_resume = True
        else:
            print(f"\n[!] Existing scan found: {folder_name}")
            import msvcrt
            print("Press 'N' within 10 seconds to start a NEW scan instead...")
            start_time = time.perf_counter()
            start_new = False
            while time.perf_counter() - start_time < 10:
                if msvcrt.kbhit():
                    char = msvcrt.getch()
                    if char.lower() == b'n':
                        start_new = True
                        break
                        
            if start_new:
                print("\n-> Starting a fresh scan...")
                folder_name = f"{safe_name}_website_audit_{stamp}"
                os.makedirs(folder_name, exist_ok=True)
                is_resume = False
            else:
                print("\n-> Resuming existing scan...")
                is_resume = True
    else:
        folder_name = f"{safe_name}_website_audit_{stamp}"
        os.makedirs(folder_name, exist_ok=True)
        
    db_name = os.path.join(folder_name, f"{safe_name}_audit.db")
    
    conn, c = setup_db(db_name, root, netloc, args.mode, args.workers, args.max_pages, args.max_resources, respect_robots, args.delay)
    
    discovered_pages, checked_pages, checked_resources, queue = get_state(c)
    
    if not is_resume or not discovered_pages:
        db_add_page(c, root, discovered_pages, queue, "queue")
        conn.commit()
        
    retry_strategy = Retry(total=3, status_forcelist=[429, 500, 502, 503, 504], backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "*/*", "Accept-Language": "en-GB,en;q=0.9"})
    
    started = time.perf_counter()
    
    print("\nE7 WAC")
    print("Eagle7 Website Audit Crawler")
    print(f"Version {VERSION}")
    print("=" * 60)
    print(f"Target: {root}")
    print(f"Mode:   {args.mode.upper()}")
    
    try:
        if not is_resume and args.mode in ("full", "seo", "images", "content", "technical"):
            print("\n[PHASE 1] Discovering content via WP REST, Sitemaps & Robots...")
            discover_wp_and_sitemaps(session, root, netloc, lambda u, table: db_add_page(c, u, discovered_pages, queue, table), respect_robots, args.timeout)
            conn.commit()
            
        process_queue(session, queue, checked_pages, discovered_pages, checked_resources, netloc, conn, c, args.mode, args.workers, args.max_pages, args.max_resources, args.timeout, args.delay)
            
    except KeyboardInterrupt:
        print("\n" + "="*60)
        print("SCAN STOPPED SAFELY")
        print("="*60)
        print("\nThe scan was stopped by the user.")
        print("All completed results have been saved.")
        print("The scan can be resumed using the same database.\n")
        
    elapsed = time.perf_counter() - started
    if not is_paused() and queue:
        print("Generating partial reports...")
    else:
        print("\n" + "=" * 60 + "\nSCAN COMPLETE\n" + "=" * 60)
        print("Generating Reports...")
        
    generate_reports_from_db(db_name, root, stamp, safe_name, elapsed, folder_name, args.mode)
