import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from .controls import check_controls, is_paused
from .http import fetch_url
from .discovery import discover_assets, clean_url
from .seo import extract_seo_tags
from .models import categorize_status, get_classification, determine_severity
from .database import db_add_page

def check_resource_task(session, url, kind, page_url, netloc, timeout):
    result = fetch_url(session, url, netloc, timeout=timeout, stream=True, is_page=False)
    classification = get_classification(url, netloc, kind)
    status_cat = categorize_status(result["initial_status"])
    severity = determine_severity(status_cat, classification, kind)
    return {
        "page_url": page_url, "resource_url": url, "resource_type": kind,
        "initial_status": result["initial_status"], "final_status": result["final_status"],
        "status_category": status_cat, "redirect_chain": result["redirect_chain"], 
        "final_url": result["final_url"], "content_type": result["content_type"], 
        "response_time": result["response_time"], "error": result["error"], 
        "classification": classification, "severity": severity,
        "seo_title": "", "seo_desc": "", "seo_canonical": "", "seo_robots": "", "seo_h1": ""
    }

def process_queue(session, queue, checked_pages, discovered_pages, checked_resources, netloc, conn, c, mode, workers, max_pages, max_resources, timeout, delay):
    started = time.perf_counter()
    initial_checked_count = len(checked_pages)
    
    # Track images specific count
    initial_img_count = len(checked_resources)
    img_checked_session = 0
    
    print("\nControls:")
    print("  P       -> Pause / Resume")
    print("  Ctrl+C  -> Stop and save safely")
    print("=" * 60)
    print(f"\n[PHASE 2] Crawling {len(discovered_pages)} discovered pages...\n")
    
    while queue and len(checked_pages) < max_pages:
        check_controls()
        if is_paused():
            time.sleep(0.5)
            continue
            
        page_url = queue.popleft()
        c.execute("DELETE FROM queue WHERE url=?", (page_url,))
        
        if page_url in checked_pages:
            conn.commit()
            continue
            
        checked_pages.add(page_url)
        c.execute("INSERT OR IGNORE INTO checked_pages VALUES (?)", (page_url,))
        
        session_checked = len(checked_pages) - initial_checked_count
        elapsed = time.perf_counter() - started
        
        if mode == "images":
            img_checked_session = len(checked_resources) - initial_img_count
            if elapsed < 1.0 and img_checked_session <= 1: rate = 0
            else: rate = img_checked_session / elapsed * 60 if elapsed else 0
            
            # Simple progress bar logic for images
            total_discovered = len(checked_resources) + len(queue) # Rough estimate
            total = max(100, total_discovered)
            pct = min(100, len(checked_resources) / total * 100) if total else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            eta = (total_discovered - len(checked_resources)) / rate if rate else 0
            
            c.execute("SELECT COUNT(*) FROM results WHERE resource_type != 'Page' AND (initial_status >= 400 OR initial_status == 0)")
            broken_cnt = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM results WHERE resource_type != 'Page' AND classification = 'Potential legacy/staging domain'")
            suspicious_cnt = c.fetchone()[0]
            
            print(f"\nImages discovered: {total_discovered} | Checked: {len(checked_resources)} | Broken: {broken_cnt} | Suspicious: {suspicious_cnt}")
            print(f"Progress: {bar} {pct:.0f}% | Rate: {rate:.1f} imgs/min | ETA: ~{eta:.1f} m")
            print(f"Currently checking: {page_url}")
        else:
            if elapsed < 1.0 and session_checked <= 1: rate = 0
            else: rate = session_checked / elapsed * 60 if elapsed else 0
            
            denominator = max(len(discovered_pages), len(checked_pages))
            pct = len(checked_pages) / denominator * 100 if denominator else 0
            eta = (denominator - len(checked_pages)) / rate if rate else 0
            print(f"[{pct:6.2f}%] Pages {len(checked_pages)}/{denominator} | Discovered {len(discovered_pages)} | Resources {len(checked_resources)} | {rate:.1f} p/min | ETA {eta:.1f} m")
            print(f"  -> {page_url}")
        
        # In content mode, skip deep asset fetching completely
        if mode == "content":
            result = fetch_url(session, page_url, netloc, timeout=timeout, stream=False, is_page=True)
            html_content = result["html"]
        else:
            result = fetch_url(session, page_url, netloc, timeout=timeout, stream=False, is_page=True)
            html_content = result["html"]
            
        seo_data = extract_seo_tags(html_content) if mode in ("full", "seo") else {"seo_title": "", "seo_desc": "", "seo_canonical": "", "seo_robots": "", "seo_h1": ""}
        
        cls_page = get_classification(page_url, netloc, "Page")
        status_cat_page = categorize_status(result["initial_status"])
        severity_page = determine_severity(status_cat_page, cls_page, "Page")
        
        row_tpl = (
            page_url, page_url, "Page", result["initial_status"], result["final_status"], status_cat_page,
            result["redirect_chain"], result["final_url"], result["content_type"], result["response_time"], result["error"],
            cls_page, severity_page,
            seo_data["seo_title"], seo_data["seo_desc"], seo_data["seo_canonical"], seo_data["seo_robots"], seo_data["seo_h1"]
        )
        # If mode is images, we still save the page to avoid fetching it again
        c.execute("INSERT INTO results VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", row_tpl)
        
        if not html_content or mode == "content":
            conn.commit()
            time.sleep(delay)
            continue
            
        assets = discover_assets(result["final_url"] or page_url, html_content, mode)
        tasks = []
        
        for u, kind in assets:
            path = urlparse(u).path.lower()
            if kind == "Link" and mode in ("full", "links", "seo"):
                if is_same_domain(u, netloc) and not path.startswith("/wp-json/") and "/oembed/" not in path and not (path.endswith(".xml") or "sitemap" in path):
                    db_add_page(c, u, discovered_pages, queue, "queue")
            
            # If mode is SEO, we only care about links, not heavy assets
            if mode == "seo" and kind != "Link":
                continue
                
            key = (u, kind)
            if key in checked_resources or len(checked_resources) >= max_resources:
                continue
                
            checked_resources.add(key)
            tasks.append((u, kind))

        if tasks:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_task = {executor.submit(check_resource_task, session, u, kind, page_url, netloc, timeout): u for u, kind in tasks}
                for future in as_completed(future_to_task):
                    check_controls()
                    while is_paused():
                        check_controls()
                        time.sleep(0.5)
                    try:
                        r = future.result()
                        c.execute("INSERT OR IGNORE INTO checked_resources VALUES (?, ?)", (r["resource_url"], r["resource_type"]))
                        res_tpl = (
                            r["page_url"], r["resource_url"], r["resource_type"], r["initial_status"], r["final_status"], r["status_category"],
                            r["redirect_chain"], r["final_url"], r["content_type"], r["response_time"], r["error"],
                            r["classification"], r["severity"],
                            r["seo_title"], r["seo_desc"], r["seo_canonical"], r["seo_robots"], r["seo_h1"]
                        )
                        c.execute("INSERT INTO results VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", res_tpl)
                    except Exception:
                        pass
                        
        conn.commit()
        time.sleep(delay)
