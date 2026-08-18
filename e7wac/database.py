import sqlite3
import os
from .config import VERSION

def setup_db(db_name, root, netloc, mode, workers, max_pages, max_resources, respect_robots, delay):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # Metadata table
    c.execute("""CREATE TABLE IF NOT EXISTS scan_metadata (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        site_url TEXT, domain TEXT, start_time TEXT, version TEXT, mode TEXT,
        workers INTEGER, max_pages INTEGER, max_resources INTEGER,
        respect_robots INTEGER, delay REAL
    )""")
    
    # Ensure metadata exists
    c.execute("SELECT COUNT(*) FROM scan_metadata")
    if c.fetchone()[0] == 0:
        c.execute("""INSERT INTO scan_metadata (
            id, site_url, domain, start_time, version, mode, workers, max_pages, max_resources, respect_robots, delay
        ) VALUES (1, ?, ?, datetime('now'), ?, ?, ?, ?, ?, ?, ?)""", 
        (root, netloc, VERSION, mode, workers, max_pages, max_resources, 1 if respect_robots else 0, delay))
    
    c.execute("CREATE TABLE IF NOT EXISTS queue (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE)")
    c.execute("CREATE TABLE IF NOT EXISTS discovered_pages (url TEXT PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS checked_pages (url TEXT PRIMARY KEY)")
    c.execute("CREATE TABLE IF NOT EXISTS checked_resources (url TEXT, kind TEXT, PRIMARY KEY(url, kind))")
    c.execute("""CREATE TABLE IF NOT EXISTS results (
        page_url TEXT, resource_url TEXT, resource_type TEXT, initial_status INTEGER, final_status INTEGER,
        status_category TEXT, redirect_chain TEXT, final_url TEXT, content_type TEXT, response_time REAL, 
        error TEXT, classification TEXT, severity TEXT,
        seo_title TEXT, seo_desc TEXT, seo_canonical TEXT, seo_robots TEXT, seo_h1 TEXT
    )""")
    c.execute("CREATE TABLE IF NOT EXISTS meta_wp (typ TEXT PRIMARY KEY, count INTEGER)")
    conn.commit()
    return conn, c

def get_state(c):
    discovered = {r[0] for r in c.execute("SELECT url FROM discovered_pages").fetchall()}
    checked_pages = {r[0] for r in c.execute("SELECT url FROM checked_pages").fetchall()}
    checked_resources = {(r[0], r[1]) for r in c.execute("SELECT url, kind FROM checked_resources").fetchall()}
    
    from collections import deque
    queue_rows = c.execute("SELECT url FROM queue ORDER BY id ASC").fetchall()
    queue = deque([r[0] for r in queue_rows])
    
    return discovered, checked_pages, checked_resources, queue

def db_add_page(c, u, discovered_pages, queue, table="discovered_pages"):
    if table == "discovered_pages":
        c.execute("INSERT OR IGNORE INTO discovered_pages VALUES (?)", (u,))
    elif table == "queue":
        if u not in discovered_pages:
            discovered_pages.add(u)
            queue.append(u)
            c.execute("INSERT OR IGNORE INTO discovered_pages VALUES (?)", (u,))
            c.execute("INSERT OR IGNORE INTO queue (url) VALUES (?)", (u,))
