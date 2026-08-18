import time
import requests
from urllib.parse import urlparse, urljoin
from .config import HEAVY_EXTENSIONS

def is_same_domain(u, root_netloc):
    parsed = urlparse(u)
    return parsed.scheme in ("http", "https") and parsed.netloc.lower() == root_netloc.lower()

def fetch_url(session, url, root_netloc, timeout=20, stream=False, is_page=False):
    started = time.perf_counter()
    current_url = url
    redirect_chain = []
    initial_status = None
    final_status = 0
    final_url = url
    content_type = ""
    html_text = None
    error_msg = ""
    
    try:
        while True:
            path = urlparse(current_url).path.lower()
            ext = path[path.rfind('.'):] if '.' in path else ''
            is_heavy = ext in HEAVY_EXTENSIONS
            is_external = not is_same_domain(current_url, root_netloc)
            
            req_kwargs = {"timeout": timeout, "allow_redirects": False}
            if not is_page and (is_heavy or is_external):
                r = session.head(current_url, **req_kwargs)
                if r.status_code == 405:
                    r = session.get(current_url, stream=True, **req_kwargs)
            else:
                r = session.get(current_url, stream=stream, **req_kwargs)
                
            if initial_status is None:
                initial_status = r.status_code
                
            if 300 <= r.status_code < 400 and 'Location' in r.headers:
                from .discovery import clean_url # avoiding circular imports
                next_url = urljoin(current_url, r.headers['Location'])
                redirect_chain.append(current_url)
                current_url = clean_url(next_url)
                if len(redirect_chain) > 10:
                    error_msg = "Redirect Loop Detected"
                    break
            else:
                final_status = r.status_code
                final_url = r.url if hasattr(r, 'url') else current_url
                content_type = r.headers.get("Content-Type", "")
                if not stream and ("text/html" in content_type.lower() or "text/css" in content_type.lower()) and hasattr(r, 'text'):
                    html_text = r.text
                break
                
        redirect_chain_str = " -> ".join(redirect_chain + [final_url]) if redirect_chain else ""
        return {
            "initial_status": initial_status or 0, "final_status": final_status, 
            "final_url": final_url, "redirect_chain": redirect_chain_str, 
            "content_type": content_type, "response_time": round(time.perf_counter() - started, 3), 
            "error": error_msg, "html": html_text
        }
    except requests.RequestException as e:
        return {
            "initial_status": 0, "final_status": 0, "final_url": "", "redirect_chain": "",
            "content_type": "", "response_time": round(time.perf_counter() - started, 3), 
            "error": str(e), "html": None
        }
