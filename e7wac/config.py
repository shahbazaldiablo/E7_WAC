VERSION = "0.8.0"
DEFAULT_URL = "https://eagle7.in"

USER_AGENT = f"Eagle7 Website Audit Crawler/{VERSION}"
TIMEOUT = 20
DELAY = 0.05
MAX_PAGES = 10000
MAX_RESOURCES = 50000
API_PER_PAGE = 100
MAX_WORKERS = 10

HEAVY_EXTENSIONS = {'.pdf', '.mp4', '.zip', '.gz', '.tar', '.rar', '.exe', '.dmg', '.iso', '.bin', '.apk', '.jpg', '.jpeg', '.png', '.gif', '.svg'}

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.svg', '.bmp', '.ico'}

STATUS_ORDER = ["200 OK", "3xx Redirects", "4xx Client Errors", "5xx Server Errors", "Connection Errors", "Other"]
