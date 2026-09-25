import re
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
from .http import is_same_domain
from .config import IMAGE_EXTENSIONS

def clean_url(u):
    if not u: return ""
    u, _ = urldefrag(u.strip())
    parsed = urlparse(u)
    if parsed.scheme:
        u = parsed._replace(scheme=parsed.scheme.lower(), netloc=parsed.netloc.lower()).geturl()
    if parsed.path == "" and parsed.netloc:
        u += "/"
    return u

def extract_css_urls(text):
    if not text: return []
    return [match.strip().strip("'\"") for match in re.findall(r"url\(\s*([^)]*)\)", text, re.IGNORECASE)
            if match.strip() and not match.strip().lower().startswith("data:")]

def detect_cms(html_content, headers=None):
    if not html_content: return "Unknown"
    soup = BeautifulSoup(html_content, "html.parser")
    generator = soup.find("meta", attrs={"name": re.compile(r"^generator$", re.I)})
    if generator:
        gen_content = generator.get("content", "").lower()
        if "typo3" in gen_content: return "TYPO3"
        if "wordpress" in gen_content: return "WordPress"
        if "joomla" in gen_content: return "Joomla"
        if "drupal" in gen_content: return "Drupal"
    
    html_str = html_content.lower()
    if "wp-content/themes" in html_str or "wp-content/plugins" in html_str or "wp-includes" in html_str: return "WordPress"
    if "typo3temp/" in html_str or "typo3conf/" in html_str: return "TYPO3"
    if "cdn.shopify.com" in html_str: return "Shopify"
    if "magento" in html_str: return "Magento"
    if 'id="__next"' in html_str or '_next/static' in html_str: return "Next.js"
    if "squarespace.com" in html_str: return "Squarespace"
    if "wix.com" in html_str: return "Wix"
    if "webflow.com" in html_str: return "Webflow"
    
    return "Unknown"

def discover_assets(page_url, html_content, mode):
    found = []
    if not html_content: return found
    soup = BeautifulSoup(html_content, "html.parser")
    
    base_tag = soup.find("base", href=True)
    base_href = base_tag["href"].strip() if base_tag else page_url

    def add_asset(raw_url, kind):
        if not raw_url: return
        raw = raw_url.strip()
        if raw.lower().startswith(("data:", "javascript:", "mailto:", "tel:", "#")): return
        u = clean_url(urljoin(base_href, raw))
        if urlparse(u).scheme in ("http", "https"):
            found.append((u, kind))

    # Images mode specific constraints
    if mode == "images":
        for tag in soup.find_all("img"):
            add_asset(tag.get("src"), "Image")
            for x in (tag.get("srcset") or "").split(","):
                if x.strip(): add_asset(x.strip().split()[0], "Image srcset")
        for tag in soup.find_all("source"):
            add_asset(tag.get("src"), "Source")
            for x in (tag.get("srcset") or "").split(","):
                if x.strip(): add_asset(x.strip().split()[0], "Source srcset")
        for tag in soup.find_all(style=True):
            for x in extract_css_urls(tag.get("style")): add_asset(x, "CSS URL")
        for tag in soup.find_all("style"):
            for x in extract_css_urls(tag.string): add_asset(x, "CSS URL")
        for tag in soup.find_all("link", href=True):
            rel = " ".join(tag.get("rel", [])).lower()
            if "stylesheet" in rel:
                add_asset(tag["href"], "Stylesheet")
        return found
        
    # Links/Full modes
    for tag in soup.find_all(["a", "area"], href=True): add_asset(tag["href"], "Link")
    for tag in soup.find_all("img"):
        add_asset(tag.get("src"), "Image")
        for x in (tag.get("srcset") or "").split(","):
            if x.strip(): add_asset(x.strip().split()[0], "Image srcset")
    for tag in soup.find_all("source"):
        add_asset(tag.get("src"), "Source")
        for x in (tag.get("srcset") or "").split(","):
            if x.strip(): add_asset(x.strip().split()[0], "Source srcset")
    for tag in soup.find_all("script", src=True): add_asset(tag["src"], "Script")
    for tag in soup.find_all("link", href=True):
        rel = " ".join(tag.get("rel", [])).lower()
        add_asset(tag["href"], "Stylesheet" if "stylesheet" in rel else "Link resource")
    for tag in soup.find_all(style=True):
        for x in extract_css_urls(tag.get("style")): add_asset(x, "CSS URL")
    for tag in soup.find_all("style"):
        for x in extract_css_urls(tag.string): add_asset(x, "CSS URL")

    return found

def discover_wp_and_sitemaps(session, root_url, netloc, add_page_callback, respect_robots, timeout):
    import time
    from .controls import check_controls, is_paused
    
    # Try CMS Detection on homepage
    cms = "Unknown"
    try:
        r = session.get(root_url, timeout=timeout)
        if r.status_code == 200:
            cms = detect_cms(r.text, r.headers)
    except Exception:
        pass
    
    print(f"  [CMS] Detected: {cms}")
    
    robots_url = urljoin(root_url, "/robots.txt")
    sitemaps = []
    
    # Even if respect_robots is False, we use it for discovery
    try:
        r = session.get(robots_url, timeout=timeout)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    sitemaps.append(line.split(":", 1)[1].strip())
    except Exception:
        pass
        
    if not sitemaps:
        sitemaps.extend([urljoin(root_url, "/sitemap.xml"), urljoin(root_url, "/sitemap_index.xml")])
        
    print(f"  [SEO] Checking {len(sitemaps)} potential sitemaps...")
    for sm in sitemaps:
        try:
            r = session.get(sm, timeout=timeout)
            if r.status_code == 200:
                for loc in re.findall(r"<loc>(.*?)</loc>", r.text, re.IGNORECASE):
                    u = clean_url(loc)
                    if is_same_domain(u, netloc):
                        add_page_callback(u, "queue")
        except Exception:
            pass

    base_api = urljoin(root_url, "/wp-json/wp/v2/")
    try:
        r = session.get(urljoin(base_api, "types"), timeout=timeout)
        if r.status_code != 200: return cms
        types_data = r.json()
    except Exception:
        return cms

    endpoints = [(slug, info["rest_base"]) for slug, info in types_data.items() if info.get("rest_base")]
    known_bases = {x[1] for x in endpoints}
    if "posts" not in known_bases: endpoints.append(("post", "posts"))
    if "pages" not in known_bases: endpoints.append(("page", "pages"))
    
    print(f"  [WP API] Found {len(endpoints)} public REST post types")
    for typ, base_name in endpoints:
        endpoint = urljoin(base_api, base_name)
        page_no, count = 1, 0
        while True:
            check_controls()
            if is_paused():
                time.sleep(0.5)
                continue
                
            try:
                params = {"per_page": 100, "page": page_no, "_fields": "id,link,type,slug,status"}
                r = session.get(endpoint, params=params, timeout=timeout)
                if r.status_code != 200 or (r.status_code == 400 and page_no > 1): break
                data = r.json()
                total_pages = int(r.headers.get("X-WP-TotalPages", "1"))
            except Exception: break
                
            for item in data:
                u = clean_url(item.get("link", ""))
                if u and is_same_domain(u, netloc):
                    add_page_callback(u, "queue")
                    count += 1
            if page_no >= total_pages: break
            page_no += 1
            
        print(f"  [WP API] {typ}: {count} public URLs")
    return cms
