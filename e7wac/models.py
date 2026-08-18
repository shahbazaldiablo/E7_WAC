import re
from urllib.parse import urlparse

class IssueSeverity:
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"

def categorize_status(status_code):
    if status_code == 200: return "200 OK"
    if status_code == 0: return "Connection Errors"
    if 300 <= status_code < 400: return "3xx Redirects"
    if 400 <= status_code < 500: return "4xx Client Errors"
    if 500 <= status_code < 600: return "5xx Server Errors"
    return "Other"

def get_classification(url, root_netloc, kind=""):
    path = urlparse(url).path.lower()
    host = urlparse(url).netloc.lower()
    
    if path.endswith(".xml") or "sitemap" in path:
        return "Sitemap"
        
    if "/wp-json/" in path or "/oembed/" in path:
        return "WP Technical"
        
    if host != root_netloc.lower():
        text = host + path
        patterns = [
            r"\bstaging\b", r"\bstage\b", r"\bdev\b", r"\bdevelopment\b",
            r"\btest\b", r"\btesting\b", r"\bqa\b", r"\buat\b", r"\bpreview\b",
            r"\blocalhost\b", r"\b127\.0\.0\.1\b", r"\.local\b", r"\.dev\b"
        ]
        if any(re.search(p, text) for p in patterns):
            return "Potential legacy/staging domain"
        return "External"
        
    return "Standard"

def determine_severity(status_category, classification, resource_type):
    if status_category == "5xx Server Errors" and resource_type == "Page":
        return IssueSeverity.CRITICAL
    if status_category == "4xx Client Errors" and resource_type == "Page":
        return IssueSeverity.HIGH
    if status_category in ["4xx Client Errors", "5xx Server Errors", "Connection Errors"]:
        return IssueSeverity.MEDIUM
    if status_category == "3xx Redirects":
        return IssueSeverity.INFO
    if classification == "Potential legacy/staging domain":
        return IssueSeverity.LOW
    return IssueSeverity.INFO
