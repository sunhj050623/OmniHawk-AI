-- OpenHawk RSS database schema

CREATE TABLE IF NOT EXISTS rss_feeds (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    feed_url TEXT DEFAULT '',
    is_active INTEGER DEFAULT 1,
    last_fetch_time TEXT,
    last_fetch_status TEXT,
    item_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rss_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    feed_id TEXT NOT NULL,
    url TEXT NOT NULL,
    published_at TEXT,
    summary TEXT,
    author TEXT,
    paper_meta_json TEXT DEFAULT '',
    paper_insight_json TEXT DEFAULT '',
    first_crawl_time TEXT NOT NULL,
    last_crawl_time TEXT NOT NULL,
    crawl_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (feed_id) REFERENCES rss_feeds(id)
);

CREATE TABLE IF NOT EXISTS rss_crawl_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crawl_time TEXT NOT NULL UNIQUE,
    total_items INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rss_crawl_status (
    crawl_record_id INTEGER NOT NULL,
    feed_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('success', 'failed')),
    error_message TEXT,
    PRIMARY KEY (crawl_record_id, feed_id),
    FOREIGN KEY (crawl_record_id) REFERENCES rss_crawl_records(id),
    FOREIGN KEY (feed_id) REFERENCES rss_feeds(id)
);

CREATE TABLE IF NOT EXISTS rss_push_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    pushed INTEGER DEFAULT 0,
    push_time TEXT,
    ai_analyzed INTEGER DEFAULT 0,
    ai_analysis_time TEXT,
    ai_analysis_mode TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rss_feed ON rss_items(feed_id);
CREATE INDEX IF NOT EXISTS idx_rss_published ON rss_items(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_rss_crawl_time ON rss_items(last_crawl_time);
CREATE INDEX IF NOT EXISTS idx_rss_title ON rss_items(title);
CREATE UNIQUE INDEX IF NOT EXISTS idx_rss_url_feed ON rss_items(url, feed_id);
CREATE INDEX IF NOT EXISTS idx_rss_crawl_status_record ON rss_crawl_status(crawl_record_id);

