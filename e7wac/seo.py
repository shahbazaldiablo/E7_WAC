import re
from bs4 import BeautifulSoup

def extract_seo_tags(html_content):
    if not html_content:
        return {"seo_title": "", "seo_desc": "", "seo_canonical": "", "seo_robots": "", "seo_h1": ""}
    
    soup = BeautifulSoup(html_content, "html.parser")
    title = soup.find("title")
    desc_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    canonical_tag = soup.find("link", rel=re.compile(r"^canonical$", re.I))
    robots_tag = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    h1_tag = soup.find("h1")
    
    h1_text = h1_tag.text.strip() if h1_tag else ""
    all_h1s = soup.find_all("h1")
    if len(all_h1s) > 1:
        h1_text = f"[MULTIPLE ({len(all_h1s)})] " + h1_text
        
    return {
        "seo_title": title.text.strip() if title else "",
        "seo_desc": desc_tag.get("content", "").strip() if desc_tag else "",
        "seo_canonical": canonical_tag.get("href", "").strip() if canonical_tag else "",
        "seo_robots": robots_tag.get("content", "").strip() if robots_tag else "",
        "seo_h1": h1_text
    }
