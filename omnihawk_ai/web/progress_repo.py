# coding=utf-8
"""
Official AI progress source ingestion for the web panel.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit


OFFICIAL_AI_PROGRESS_SOURCES: List[Dict[str, Any]] = [
    # Global official blogs / research feeds
    {
        "id": "openai_news",
        "name": "OpenAI News",
        "org": "OpenAI",
        "region": "global",
        "kind": "official_blog",
        "feed_type": "rss",
        "feed_url": "https://openai.com/news/rss.xml",
        "homepage": "https://openai.com/news/",
    },
    {
        "id": "google_ai_blog",
        "name": "Google AI Blog",
        "org": "Google",
        "region": "global",
        "kind": "official_blog",
        "feed_type": "rss",
        "feed_url": "https://blog.google/technology/ai/rss/",
        "homepage": "https://blog.google/technology/ai/",
    },
    {
        "id": "deepmind_blog",
        "name": "Google DeepMind Blog",
        "org": "Google DeepMind",
        "region": "global",
        "kind": "official_blog",
        "feed_type": "rss",
        "feed_url": "https://www.deepmind.com/blog/rss.xml",
        "homepage": "https://deepmind.google/discover/blog/",
    },
    {
        "id": "microsoft_research_feed",
        "name": "Microsoft Research Feed",
        "org": "Microsoft Research",
        "region": "global",
        "kind": "official_blog",
        "feed_type": "rss",
        "feed_url": "https://www.microsoft.com/en-us/research/feed/",
        "homepage": "https://www.microsoft.com/en-us/research/blog/",
    },
    {
        "id": "nvidia_blog_feed",
        "name": "NVIDIA Technical Blog",
        "org": "NVIDIA",
        "region": "global",
        "kind": "official_blog",
        "feed_type": "rss",
        "feed_url": "https://blogs.nvidia.com/feed/",
        "homepage": "https://blogs.nvidia.com/",
    },
    {
        "id": "huggingface_blog",
        "name": "Hugging Face Blog",
        "org": "Hugging Face",
        "region": "global",
        "kind": "official_blog",
        "feed_type": "rss",
        "feed_url": "https://huggingface.co/blog/feed.xml",
        "homepage": "https://huggingface.co/blog",
    },
    {
        "id": "anthropic_news",
        "name": "Anthropic News",
        "org": "Anthropic",
        "region": "global",
        "kind": "official_site",
        "feed_type": "sitemap",
        "sitemap_url": "https://www.anthropic.com/sitemap.xml",
        "homepage": "https://www.anthropic.com/news",
        # Prioritize model and Claude-product updates.
        "path_prefixes": ["/news/claude-", "/news/claude"],
    },
    # China official sources (prefer official blogs/docs over single-model release feeds)
    {
        "id": "qwen_blog",
        "name": "Qwen Blog",
        "org": "Alibaba / Qwen",
        "region": "cn",
        "kind": "official_blog",
        "feed_type": "rss",
        "feed_url": "https://qwenlm.github.io/blog/index.xml",
        "homepage": "https://qwen.ai/research",
    },
    {
        "id": "qwen36_updates",
        "name": "Qwen3.6 Updates",
        "org": "Alibaba / Qwen",
        "region": "cn",
        "kind": "official_blog",
        "feed_type": "atom",
        "feed_url": "https://github.com/QwenLM/Qwen3.6/commits/main.atom",
        "homepage": "https://github.com/QwenLM/Qwen3.6",
    },
    {
        "id": "deepseek_news",
        "name": "DeepSeek News",
        "org": "DeepSeek",
        "region": "cn",
        "kind": "official_site",
        "feed_type": "sitemap",
        "sitemap_url": "https://api-docs.deepseek.com/sitemap.xml",
        "homepage": "https://api-docs.deepseek.com/",
        "path_prefixes": ["/news/"],
    },
    {
        "id": "zai_release_notes",
        "name": "Z.AI Release Notes",
        "org": "Zhipu / Z.AI",
        "region": "cn",
        "kind": "official_site",
        "feed_type": "sitemap",
        "sitemap_url": "https://docs.z.ai/sitemap.xml",
        "homepage": "https://docs.z.ai/release-notes/new-released",
        "path_prefixes": ["/release-notes/"],
    },
    {
        "id": "lingyi_newsroom",
        "name": "01.AI Newsroom",
        "org": "01.AI",
        "region": "cn",
        "kind": "official_site",
        "feed_type": "sitemap",
        "sitemap_url": "https://www.lingyiwanwu.com/sitemap.xml",
        "homepage": "https://www.lingyiwanwu.com/newsroom",
        "path_prefixes": ["/newsroom", "/1-0", "/2-0", "/3-0", "/en1-0", "/en2-0", "/en3-0"],
    },
    {
        "id": "minimax_release_notes",
        "name": "MiniMax Release Notes",
        "org": "MiniMax",
        "region": "cn",
        "kind": "official_site",
        "feed_type": "sitemap",
        "sitemap_url": "https://platform.minimaxi.com/docs/sitemap.xml",
        "homepage": "https://platform.minimaxi.com/docs/release-notes/models",
        "path_prefixes": ["/docs/release-notes/"],
    },
    {
        "id": "ernie_blog",
        "name": "ERNIE Blog",
        "org": "Baidu / ERNIE",
        "region": "cn",
        "kind": "official_blog",
        "feed_type": "rss",
        "feed_url": "https://ernie.baidu.com/blog/zh/posts/index.xml",
        "homepage": "https://ernie.baidu.com/",
    },
    # Global capital-market / equities signals
    {
        "id": "yahoo_finance_ai_basket",
        "name": "Yahoo Finance AI Stocks",
        "org": "Yahoo Finance",
        "region": "global",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=NVDA,AMD,MSFT,GOOGL,META,AMZN,AVGO,TSM,ASML,ARM,9988.HK,0700.HK,005930.KS,6758.T&region=US&lang=en-US",
        "homepage": "https://finance.yahoo.com/",
        "ticker_allowlist": [
            "NVDA",
            "AMD",
            "MSFT",
            "GOOGL",
            "META",
            "AMZN",
            "AVGO",
            "TSM",
            "ASML",
            "ARM",
            "9988.HK",
            "0700.HK",
            "005930.KS",
            "6758.T",
        ],
        "entity_keywords": [
            "nvidia",
            "amd",
            "microsoft",
            "google",
            "alphabet",
            "meta",
            "amazon",
            "broadcom",
            "tsmc",
            "asml",
            "arm",
            "alibaba",
            "tencent",
            "samsung",
            "sony",
        ],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "yahoo_finance_ai_china_hk",
        "name": "Yahoo Finance AI Stocks (China/HK)",
        "org": "Yahoo Finance",
        "region": "cn",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=9988.HK,0700.HK,9618.HK,1810.HK,9888.HK&region=HK&lang=en-US",
        "homepage": "https://finance.yahoo.com/",
        "ticker_allowlist": ["9988.HK", "0700.HK", "9618.HK", "1810.HK", "9888.HK"],
        "entity_keywords": ["alibaba", "tencent", "jd", "xiaomi", "baidu", "ai"],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "yahoo_finance_ai_japan",
        "name": "Yahoo Finance AI Stocks (Japan)",
        "org": "Yahoo Finance",
        "region": "jp",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=6758.T,9984.T,8035.T,4063.T&region=JP&lang=en-US",
        "homepage": "https://finance.yahoo.com/",
        "ticker_allowlist": ["6758.T", "9984.T", "8035.T", "4063.T"],
        "entity_keywords": ["sony", "softbank", "tokyo electron", "shin-etsu", "japan", "ai"],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "yahoo_finance_ai_apac",
        "name": "Yahoo Finance AI Stocks (APAC)",
        "org": "Yahoo Finance",
        "region": "apac",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=005930.KS,000660.KS,2330.TW,2454.TW&region=KR&lang=en-US",
        "homepage": "https://finance.yahoo.com/",
        "ticker_allowlist": ["005930.KS", "000660.KS", "2330.TW", "2454.TW"],
        "entity_keywords": ["samsung", "sk hynix", "tsmc", "mediatek", "taiwan", "korea", "ai"],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "yahoo_finance_ai_europe",
        "name": "Yahoo Finance AI Stocks (Europe)",
        "org": "Yahoo Finance",
        "region": "eu",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=ASML.AS,SAP.DE,SIE.DE,STM.PA,IFX.DE&region=DE&lang=en-US",
        "homepage": "https://finance.yahoo.com/",
        "ticker_allowlist": ["ASML.AS", "SAP.DE", "SIE.DE", "STM.PA", "IFX.DE"],
        "entity_keywords": ["asml", "sap", "siemens", "stmicroelectronics", "infineon", "europe", "ai"],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "yahoo_finance_ai_hk_market",
        "name": "Yahoo Finance AI Stocks (Hong Kong Market)",
        "org": "Yahoo Finance",
        "region": "hk",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=0700.HK,9988.HK,9618.HK,3690.HK,1810.HK,9888.HK&region=HK&lang=en-US",
        "homepage": "https://finance.yahoo.com/",
        "ticker_allowlist": ["0700.HK", "9988.HK", "9618.HK", "3690.HK", "1810.HK", "9888.HK"],
        "entity_keywords": ["tencent", "alibaba", "jd", "meituan", "xiaomi", "baidu", "hong kong", "hk"],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "yahoo_finance_ai_korea_market",
        "name": "Yahoo Finance AI Stocks (Korea Market)",
        "org": "Yahoo Finance",
        "region": "kr",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=005930.KS,000660.KS,035420.KS,035720.KS&region=KR&lang=en-US",
        "homepage": "https://finance.yahoo.com/",
        "ticker_allowlist": ["005930.KS", "000660.KS", "035420.KS", "035720.KS"],
        "entity_keywords": ["samsung", "sk hynix", "naver", "kakao", "korea", "korean", "ai"],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "yahoo_finance_ai_uk_market",
        "name": "Yahoo Finance AI Stocks (UK Market)",
        "org": "Yahoo Finance",
        "region": "uk",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=ARM,DARK.L,REL.L,SPX.L,CNAPA.AS&region=GB&lang=en-US",
        "homepage": "https://finance.yahoo.com/",
        "ticker_allowlist": ["ARM", "DARK.L", "REL.L", "SPX.L", "CNAPA.AS"],
        "entity_keywords": ["arm holdings", "darktrace", "relx", "spirent", "uk", "united kingdom", "ai"],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "yahoo_finance_ai_france_market",
        "name": "Yahoo Finance AI Stocks (France Market)",
        "org": "Yahoo Finance",
        "region": "fr",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=CAP.PA,DSY.PA,ORA.PA,STM.PA,EXA.PA&region=FR&lang=en-US",
        "homepage": "https://finance.yahoo.com/",
        "ticker_allowlist": ["CAP.PA", "DSY.PA", "ORA.PA", "STM.PA", "EXA.PA"],
        "entity_keywords": ["capgemini", "dassault systemes", "orange", "stmicroelectronics", "france", "french", "ai"],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "cnbc_us_markets_ai",
        "name": "CNBC US Markets (AI Signals)",
        "org": "CNBC",
        "region": "us",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "homepage": "https://www.cnbc.com/markets/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "capex",
            "stock",
            "shares",
            "guidance",
            "data center",
        ],
        "max_age_days": 30,
    },
    {
        "id": "cnbc_europe_markets_ai",
        "name": "CNBC Europe Markets (AI Signals)",
        "org": "CNBC",
        "region": "eu",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.cnbc.com/id/19794221/device/rss/rss.html",
        "homepage": "https://www.cnbc.com/world/?region=world",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "stock",
            "shares",
            "market",
            "chip",
            "semiconductor",
        ],
        "max_age_days": 30,
    },
    {
        "id": "cnbc_asia_markets_ai",
        "name": "CNBC Asia Markets (AI Signals)",
        "org": "CNBC",
        "region": "apac",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.cnbc.com/id/19832390/device/rss/rss.html",
        "homepage": "https://www.cnbc.com/world/?region=world",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "stock",
            "shares",
            "chip",
            "semiconductor",
            "data center",
        ],
        "max_age_days": 30,
    },
    {
        "id": "google_news_ai_finance_hk",
        "name": "AI Capital Markets (Hong Kong)",
        "org": "Google News",
        "region": "hk",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=Hong+Kong+AI+stocks+earnings+guidance&hl=en-US&gl=HK&ceid=HK:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "guidance",
            "stock",
            "shares",
            "hong kong",
            "hk",
            "chip",
            "semiconductor",
        ],
        "max_age_days": 30,
    },
    {
        "id": "google_news_ai_finance_korea",
        "name": "AI Capital Markets (South Korea)",
        "org": "Google News",
        "region": "kr",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=South+Korea+AI+stocks+earnings+guidance&hl=en-US&gl=KR&ceid=KR:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "guidance",
            "stock",
            "shares",
            "korea",
            "samsung",
            "hynix",
            "chip",
            "semiconductor",
        ],
        "max_age_days": 30,
    },
    {
        "id": "google_news_ai_finance_uk",
        "name": "AI Capital Markets (United Kingdom)",
        "org": "Google News",
        "region": "uk",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=United+Kingdom+AI+stocks+earnings+guidance&hl=en-GB&gl=GB&ceid=GB:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "guidance",
            "stock",
            "shares",
            "uk",
            "united kingdom",
            "london stock exchange",
            "arm",
        ],
        "max_age_days": 30,
    },
    {
        "id": "google_news_ai_finance_france",
        "name": "AI Capital Markets (France)",
        "org": "Google News",
        "region": "fr",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=France+AI+stocks+earnings+guidance&hl=fr&gl=FR&ceid=FR:fr",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "guidance",
            "stock",
            "shares",
            "france",
            "francais",
            "paris",
            "cac 40",
        ],
        "max_age_days": 30,
    },
    {
        "id": "nasdaq_markets_ai_signals",
        "name": "Nasdaq Markets (AI Signals)",
        "org": "Nasdaq",
        "region": "us",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.nasdaq.com/feed/rssoutbound?category=Markets",
        "homepage": "https://www.nasdaq.com/market-activity",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "guidance",
            "stock",
            "shares",
            "capital expenditure",
            "data center",
            "semiconductor",
        ],
        "entity_keywords": [
            "nvidia",
            "amd",
            "microsoft",
            "alphabet",
            "meta",
            "amazon",
            "broadcom",
            "arm",
        ],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "nasdaq_technology_ai_signals",
        "name": "Nasdaq Technology (AI Signals)",
        "org": "Nasdaq",
        "region": "us",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.nasdaq.com/feed/rssoutbound?category=Technology",
        "homepage": "https://www.nasdaq.com/news-and-insights/topic/technology",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "guidance",
            "stock",
            "shares",
            "capex",
            "data center",
            "chip",
            "semiconductor",
        ],
        "entity_keywords": [
            "nvidia",
            "amd",
            "microsoft",
            "alphabet",
            "meta",
            "amazon",
            "broadcom",
            "arm",
        ],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "chinadaily_china_ai_finance",
        "name": "China Daily China RSS (AI Finance Signals)",
        "org": "China Daily",
        "region": "cn",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.chinadaily.com.cn/rss/china_rss.xml",
        "homepage": "https://www.chinadaily.com.cn/china",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "算力",
            "大模型",
            "芯片",
            "半导体",
            "财报",
            "股票",
            "融资",
            "投资",
            "并购",
        ],
        "entity_keywords": [
            "baidu",
            "alibaba",
            "tencent",
            "bytedance",
            "xiaomi",
            "sense time",
            "huawei",
            "中芯国际",
            "寒武纪",
            "科大讯飞",
        ],
        "max_age_days": 30,
    },
    {
        "id": "hkex_news_release_ai_signals",
        "name": "HKEX News Releases (AI Market Signals)",
        "org": "HKEX",
        "region": "hk",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.hkex.com.hk/Services/RSS-Feeds/News-Releases?sc_lang=en",
        "homepage": "https://www.hkex.com.hk/News/News-Release",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "listing",
            "earnings",
            "results",
            "stock",
            "shares",
            "capital",
            "technology",
        ],
        "entity_keywords": [
            "tencent",
            "alibaba",
            "baidu",
            "xiaomi",
            "jd",
            "meituan",
            "0700.hk",
            "9988.hk",
            "9618.hk",
            "3690.hk",
        ],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "jpx_markets_news_ai_signals",
        "name": "JPX Markets News (AI Capital Signals)",
        "org": "JPX",
        "region": "jp",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.jpx.co.jp/english/rss/markets_news.xml",
        "homepage": "https://www.jpx.co.jp/english/news/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "results",
            "stock",
            "shares",
            "semiconductor",
            "chip",
            "technology",
        ],
        "entity_keywords": [
            "sony",
            "softbank",
            "tokyo electron",
            "shin-etsu",
            "renesas",
            "6758.t",
            "9984.t",
            "8035.t",
            "4063.t",
            "6723.t",
        ],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "jpx_news_ai_signals",
        "name": "JPX News (AI Market Signals)",
        "org": "JPX",
        "region": "jp",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.jpx.co.jp/english/rss/jpx-news.xml",
        "homepage": "https://www.jpx.co.jp/english/news/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "market",
            "listing",
            "stock",
            "shares",
            "technology",
            "semiconductor",
        ],
        "entity_keywords": [
            "sony",
            "softbank",
            "tokyo electron",
            "renesas",
            "6758.t",
            "9984.t",
            "8035.t",
            "6723.t",
        ],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "hankyung_ai_finance_signals",
        "name": "Hankyung Markets/Tech (AI Signals)",
        "org": "Korea Economic Daily",
        "region": "kr",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.hankyung.com/feed/all-news",
        "homepage": "https://www.hankyung.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "guidance",
            "stock",
            "shares",
            "semiconductor",
            "chip",
            "samsung",
            "hynix",
        ],
        "entity_keywords": [
            "samsung",
            "sk hynix",
            "naver",
            "kakao",
            "005930.ks",
            "000660.ks",
            "035420.ks",
            "035720.ks",
        ],
        "max_age_days": 30,
    },
    {
        "id": "straitstimes_business_ai_signals",
        "name": "The Straits Times Business (AI Signals)",
        "org": "The Straits Times",
        "region": "apac",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.straitstimes.com/news/business/rss.xml",
        "homepage": "https://www.straitstimes.com/business",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "guidance",
            "stock",
            "shares",
            "capex",
            "data center",
            "semiconductor",
        ],
        "entity_keywords": [
            "nvidia",
            "tsmc",
            "samsung",
            "alibaba",
            "tencent",
            "sea ltd",
            "grab",
        ],
        "max_age_days": 30,
    },
    {
        "id": "businesstimes_sg_tech_ai_signals",
        "name": "The Business Times SG Technology (AI Signals)",
        "org": "The Business Times",
        "region": "apac",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.businesstimes.com.sg/rss/technology",
        "homepage": "https://www.businesstimes.com.sg/technology",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "stock",
            "shares",
            "capex",
            "funding",
            "data center",
            "semiconductor",
        ],
        "entity_keywords": [
            "nvidia",
            "tsmc",
            "samsung",
            "alibaba",
            "tencent",
            "sea ltd",
            "grab",
        ],
        "max_age_days": 30,
    },
    {
        "id": "euronext_news_ai_signals",
        "name": "Euronext News (AI Market Signals)",
        "org": "Euronext",
        "region": "eu",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.euronext.com/en/news/rss",
        "homepage": "https://www.euronext.com/en/news",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "earnings",
            "results",
            "stock",
            "shares",
            "technology",
            "semiconductor",
            "listing",
        ],
        "entity_keywords": [
            "asml",
            "sap",
            "siemens",
            "stmicroelectronics",
            "infineon",
            "capgemini",
            "dassault systemes",
        ],
        "strict_entity_match": True,
        "max_age_days": 30,
    },
    {
        "id": "fca_news_ai_finance_signals",
        "name": "UK FCA News (AI Market/Disclosure Signals)",
        "org": "FCA",
        "region": "uk",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://www.fca.org.uk/news/rss.xml",
        "homepage": "https://www.fca.org.uk/news",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "market",
            "disclosure",
            "listing",
            "stock",
            "shares",
            "capital market",
        ],
        "entity_keywords": [
            "arm",
            "darktrace",
            "relx",
            "london stock exchange",
            "uk market",
        ],
        "max_age_days": 30,
    },
    {
        "id": "amd_investor_press",
        "name": "AMD Investor Press Releases",
        "org": "AMD",
        "region": "global",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://ir.amd.com/news-events/press-releases/rss",
        "homepage": "https://ir.amd.com/news-events/press-releases",
        "max_age_days": 90,
    },
    {
        "id": "broadcom_investor_news",
        "name": "Broadcom Investor News Releases",
        "org": "Broadcom",
        "region": "global",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://investors.broadcom.com/rss/news-releases.xml",
        "homepage": "https://investors.broadcom.com/news-releases",
        "max_age_days": 90,
    },
    {
        "id": "nvidia_press_releases",
        "name": "NVIDIA Press Releases",
        "org": "NVIDIA",
        "region": "global",
        "kind": "market_finance",
        "feed_type": "rss",
        "feed_url": "https://nvidianews.nvidia.com/cats/press_release.xml",
        "homepage": "https://nvidianews.nvidia.com/",
        "max_age_days": 90,
    },
    # Global industry report / strategic intelligence sources
    {
        "id": "cbinsights_research",
        "name": "CB Insights Research",
        "org": "CB Insights",
        "region": "global",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www.cbinsights.com/research/feed/",
        "homepage": "https://www.cbinsights.com/research/",
        "max_age_days": 90,
    },
    {
        "id": "mit_techreview_ai",
        "name": "MIT Technology Review AI",
        "org": "MIT Technology Review",
        "region": "global",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
        "homepage": "https://www.technologyreview.com/topic/artificial-intelligence/",
        "max_age_days": 90,
    },
    {
        "id": "ieee_spectrum_ai",
        "name": "IEEE Spectrum AI",
        "org": "IEEE Spectrum",
        "region": "global",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://spectrum.ieee.org/rss/topic/artificial-intelligence",
        "homepage": "https://spectrum.ieee.org/artificial-intelligence",
        "max_age_days": 90,
    },
    {
        "id": "sequoia_feed",
        "name": "Sequoia Capital Insights",
        "org": "Sequoia Capital",
        "region": "global",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www.sequoiacap.com/feed/",
        "homepage": "https://www.sequoiacap.com/",
        "max_age_days": 90,
    },
    {
        "id": "forrester_blog_ai",
        "name": "Forrester Blogs (AI)",
        "org": "Forrester",
        "region": "global",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://go.forrester.com/blogs/feed/",
        "homepage": "https://go.forrester.com/blogs/",
        "required_keywords": [
            "artificial intelligence",
            "generative ai",
            "machine learning",
            "large language model",
            "llm",
            "report",
            "research",
            "forecast",
            "survey",
            "index",
            "insight",
        ],
        "max_age_days": 90,
    },
    {
        "id": "stanford_hai_sitemap",
        "name": "Stanford HAI News & AI Index",
        "org": "Stanford HAI",
        "region": "us",
        "kind": "industry_report",
        "feed_type": "sitemap",
        "sitemap_url": "https://hai.stanford.edu/sitemap.xml",
        "homepage": "https://hai.stanford.edu/news",
        "path_prefixes": ["/news/", "/ai-index/"],
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "report",
            "index",
            "benchmark",
            "survey",
            "analysis",
            "research",
        ],
        "max_age_days": 90,
    },
    {
        "id": "csis_ai_analysis",
        "name": "CSIS Analysis (AI)",
        "org": "CSIS",
        "region": "us",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www.csis.org/rss.xml",
        "homepage": "https://www.csis.org/topics/artificial-intelligence",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "report",
            "analysis",
            "research",
            "forecast",
            "industry",
        ],
        "max_age_days": 90,
    },
    {
        "id": "economist_scitech_ai",
        "name": "Economist Science & Technology (AI)",
        "org": "The Economist",
        "region": "global",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www.economist.com/science-and-technology/rss.xml",
        "homepage": "https://www.economist.com/science-and-technology",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "machine learning",
            "llm",
            "report",
            "analysis",
            "research",
            "survey",
            "outlook",
        ],
        "max_age_days": 90,
    },
    {
        "id": "mittr_global_feed_ai",
        "name": "MIT Technology Review (AI Signals)",
        "org": "MIT Technology Review",
        "region": "global",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www.technologyreview.com/feed/",
        "homepage": "https://www.technologyreview.com/",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "machine learning",
            "model",
            "report",
            "research",
            "analysis",
            "study",
            "index",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_ai_reports_us",
        "name": "AI Industry Reports (United States)",
        "org": "Google News",
        "region": "us",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+industry+report+United+States&hl=en-US&gl=US&ceid=US:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "forecast",
            "survey",
            "outlook",
            "industry",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_ai_reports_china",
        "name": "AI Industry Reports (China)",
        "org": "Google News",
        "region": "cn",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+industry+report+China&hl=en-US&gl=US&ceid=US:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "forecast",
            "survey",
            "outlook",
            "industry",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_ai_reports_japan",
        "name": "AI Industry Reports (Japan)",
        "org": "Google News",
        "region": "jp",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+industry+report+Japan&hl=en-US&gl=US&ceid=US:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "forecast",
            "survey",
            "outlook",
            "industry",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_ai_reports_apac",
        "name": "AI Industry Reports (APAC)",
        "org": "Google News",
        "region": "apac",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+industry+report+APAC&hl=en-US&gl=US&ceid=US:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "forecast",
            "survey",
            "outlook",
            "industry",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_ai_reports_europe",
        "name": "AI Industry Reports (Europe)",
        "org": "Google News",
        "region": "eu",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+industry+report+Europe&hl=en-US&gl=US&ceid=US:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "forecast",
            "survey",
            "outlook",
            "industry",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_ai_reports_hk",
        "name": "AI Industry Reports (Hong Kong)",
        "org": "Google News",
        "region": "hk",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+industry+report+Hong+Kong&hl=en-US&gl=HK&ceid=HK:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "forecast",
            "survey",
            "outlook",
            "industry",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_ai_reports_korea",
        "name": "AI Industry Reports (South Korea)",
        "org": "Google News",
        "region": "kr",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+industry+report+South+Korea&hl=en-US&gl=KR&ceid=KR:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "forecast",
            "survey",
            "outlook",
            "industry",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_ai_reports_uk",
        "name": "AI Industry Reports (United Kingdom)",
        "org": "Google News",
        "region": "uk",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+industry+report+United+Kingdom&hl=en-GB&gl=GB&ceid=GB:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "forecast",
            "survey",
            "outlook",
            "industry",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_ai_reports_france",
        "name": "AI Industry Reports (France)",
        "org": "Google News",
        "region": "fr",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+industry+report+France&hl=fr&gl=FR&ceid=FR:fr",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "forecast",
            "survey",
            "outlook",
            "industry",
        ],
        "max_age_days": 90,
    },
    {
        "id": "report_36kr_ai_industry",
        "name": "36Kr Feed (AI Industry Signals)",
        "org": "36Kr",
        "region": "cn",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://36kr.com/feed",
        "homepage": "https://36kr.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "llm",
            "model",
            "agent",
            "report",
            "analysis",
            "industry",
            "research",
        ],
        "max_age_days": 90,
    },
    {
        "id": "report_nhk_business_ai",
        "name": "NHK Business/Economy (AI Industry Signals)",
        "org": "NHK",
        "region": "jp",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www3.nhk.or.jp/rss/news/cat6.xml",
        "homepage": "https://www3.nhk.or.jp/news/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "llm",
            "model",
            "industry",
            "research",
            "analysis",
            "semiconductor",
            "chip",
        ],
        "max_age_days": 90,
    },
    {
        "id": "report_hankyung_ai",
        "name": "Hankyung (AI Industry Signals)",
        "org": "Korea Economic Daily",
        "region": "kr",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www.hankyung.com/feed/all-news",
        "homepage": "https://www.hankyung.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "llm",
            "model",
            "industry",
            "research",
            "analysis",
            "forecast",
            "survey",
        ],
        "max_age_days": 90,
    },
    {
        "id": "report_bruegel_ai",
        "name": "Bruegel Research (AI Policy/Industry)",
        "org": "Bruegel",
        "region": "eu",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www.bruegel.org/rss.xml",
        "homepage": "https://www.bruegel.org/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "policy",
            "industry",
            "productivity",
            "innovation",
        ],
        "max_age_days": 90,
    },
    {
        "id": "report_ifri_en_ai",
        "name": "IFRI Analysis (AI Signals, EN)",
        "org": "IFRI",
        "region": "eu",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www.ifri.org/en/rss.xml",
        "homepage": "https://www.ifri.org/en",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "report",
            "research",
            "analysis",
            "policy",
            "industry",
            "strategy",
            "governance",
        ],
        "max_age_days": 90,
    },
    {
        "id": "report_ifri_fr_ai",
        "name": "IFRI Analysis (AI Signals, FR)",
        "org": "IFRI",
        "region": "fr",
        "kind": "industry_report",
        "feed_type": "rss",
        "feed_url": "https://www.ifri.org/fr/rss.xml",
        "homepage": "https://www.ifri.org/fr",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "rapport",
            "etude",
            "analyse",
            "industrie",
            "recherche",
            "strategie",
            "innovation",
        ],
        "max_age_days": 90,
    },
    {
        "id": "report_govuk_all_ai",
        "name": "UK GOV Search Feed (AI Analysis/Reports)",
        "org": "UK Government",
        "region": "uk",
        "kind": "industry_report",
        "feed_type": "atom",
        "feed_url": "https://www.gov.uk/search/all.atom?keywords=artificial+intelligence",
        "homepage": "https://www.gov.uk/search/all?keywords=artificial+intelligence",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "analysis",
            "report",
            "research",
            "consultation",
            "strategy",
            "white paper",
            "guidance",
        ],
        "max_age_days": 90,
    },
    # Policy + safety (combined domain)
    {
        "id": "nist_news",
        "name": "NIST News",
        "org": "NIST",
        "region": "global",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://www.nist.gov/news-events/news/rss.xml",
        "homepage": "https://www.nist.gov/news-events/news",
        "max_age_days": 90,
    },
    {
        "id": "eu_commission_presscorner",
        "name": "EU Commission Press Corner",
        "org": "European Commission",
        "region": "eu",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://ec.europa.eu/commission/presscorner/api/rss?language=en",
        "homepage": "https://ec.europa.eu/commission/presscorner/home/en",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "regulation",
            "policy",
            "governance",
            "safety",
            "standard",
            "compliance",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "edpb_updates",
        "name": "EDPB News",
        "org": "European Data Protection Board",
        "region": "eu",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://www.edpb.europa.eu/rss.xml",
        "homepage": "https://www.edpb.europa.eu/news/news_en",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "data protection",
            "privacy",
            "compliance",
            "guideline",
            "opinion",
            "risk",
            "safety",
        ],
        "max_age_days": 90,
    },
    {
        "id": "govuk_ai_policy",
        "name": "UK GOV AI Policy Updates",
        "org": "UK Government",
        "region": "uk",
        "kind": "policy_safety",
        "feed_type": "atom",
        "feed_url": "https://www.gov.uk/search/news-and-communications.atom?keywords=ai+policy",
        "homepage": "https://www.gov.uk/search/news-and-communications?keywords=ai+policy",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "policy",
            "regulation",
            "governance",
            "safety",
            "guidance",
            "framework",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "govuk_ai_safety",
        "name": "UK GOV AI Safety Updates",
        "org": "UK Government",
        "region": "uk",
        "kind": "policy_safety",
        "feed_type": "atom",
        "feed_url": "https://www.gov.uk/search/news-and-communications.atom?keywords=ai+safety",
        "homepage": "https://www.gov.uk/search/news-and-communications?keywords=ai+safety",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "safety",
            "security",
            "evaluation",
            "governance",
            "guardrail",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "govuk_ai_regulation",
        "name": "UK GOV AI Regulation Updates",
        "org": "UK Government",
        "region": "uk",
        "kind": "policy_safety",
        "feed_type": "atom",
        "feed_url": "https://www.gov.uk/search/news-and-communications.atom?keywords=artificial+intelligence+regulation",
        "homepage": "https://www.gov.uk/search/news-and-communications?keywords=artificial+intelligence+regulation",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "regulation",
            "bill",
            "law",
            "policy",
            "compliance",
            "standard",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "whitehouse_presidential_actions_ai",
        "name": "White House Presidential Actions (AI)",
        "org": "The White House",
        "region": "us",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://www.whitehouse.gov/presidential-actions/feed/",
        "homepage": "https://www.whitehouse.gov/presidential-actions/",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "executive order",
            "policy",
            "safety",
            "security",
            "governance",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "sec_press_ai",
        "name": "SEC Press Releases (AI Policy/Market)",
        "org": "US SEC",
        "region": "us",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://www.sec.gov/news/pressreleases.rss",
        "homepage": "https://www.sec.gov/news/pressreleases",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "regulation",
            "compliance",
            "risk",
            "policy",
            "governance",
            "disclosure",
            "security",
        ],
        "max_age_days": 90,
    },
    {
        "id": "cnil_ai_news",
        "name": "CNIL News (AI & Data Protection)",
        "org": "CNIL",
        "region": "fr",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://www.cnil.fr/en/rss.xml",
        "homepage": "https://www.cnil.fr/en",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "data protection",
            "privacy",
            "regulation",
            "compliance",
            "governance",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "privacy_international_ai",
        "name": "Privacy International News (AI)",
        "org": "Privacy International",
        "region": "global",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://www.privacyinternational.org/rss.xml",
        "homepage": "https://www.privacyinternational.org/",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "policy",
            "regulation",
            "privacy",
            "surveillance",
            "governance",
            "risk",
            "safety",
        ],
        "max_age_days": 90,
    },
    {
        "id": "wipo_pressroom_ai",
        "name": "WIPO Pressroom (AI Policy/IP)",
        "org": "WIPO",
        "region": "global",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://www.wipo.int/pressroom/en/rss.xml",
        "homepage": "https://www.wipo.int/pressroom/en/",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "policy",
            "regulation",
            "governance",
            "copyright",
            "intellectual property",
            "standard",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "esma_news_ai",
        "name": "ESMA News (AI Policy/Market Risk)",
        "org": "European Securities and Markets Authority",
        "region": "eu",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://www.esma.europa.eu/press-news/esma-news/rss.xml",
        "homepage": "https://www.esma.europa.eu/press-news/esma-news",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "regulation",
            "policy",
            "risk",
            "governance",
            "compliance",
            "market",
            "supervision",
        ],
        "max_age_days": 90,
    },
    {
        "id": "imda_news_ai",
        "name": "IMDA News (AI Governance)",
        "org": "IMDA Singapore",
        "region": "apac",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://www.imda.gov.sg/rss/news-and-events/news",
        "homepage": "https://www.imda.gov.sg/",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "governance",
            "policy",
            "safety",
            "risk",
            "regulation",
            "framework",
            "guidelines",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_policy_china_gov",
        "name": "AI Policy Tracker (China Gov)",
        "org": "Google News / gov.cn",
        "region": "cn",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+policy+site:gov.cn&hl=en-US&gl=US&ceid=US:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "policy",
            "regulation",
            "governance",
            "guideline",
            "safety",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_policy_japan_gov",
        "name": "AI Policy Tracker (Japan Gov)",
        "org": "Google News / go.jp",
        "region": "jp",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+policy+site:go.jp&hl=en-US&gl=US&ceid=US:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "policy",
            "regulation",
            "governance",
            "guideline",
            "safety",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_policy_korea_gov",
        "name": "AI Policy Tracker (Korea Gov)",
        "org": "Google News / go.kr",
        "region": "kr",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+policy+site:go.kr&hl=en-US&gl=KR&ceid=KR:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "policy",
            "regulation",
            "governance",
            "guideline",
            "safety",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_policy_hk_gov",
        "name": "AI Policy Tracker (Hong Kong Gov)",
        "org": "Google News / gov.hk",
        "region": "hk",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+policy+site:gov.hk&hl=en-US&gl=HK&ceid=HK:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "policy",
            "regulation",
            "governance",
            "guideline",
            "safety",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_policy_france_gov",
        "name": "AI Policy Tracker (France Gov)",
        "org": "Google News / gouv.fr",
        "region": "fr",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+policy+site:gouv.fr&hl=fr&gl=FR&ceid=FR:fr",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "policy",
            "regulation",
            "governance",
            "guideline",
            "safety",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_policy_eu_institutions",
        "name": "AI Policy Tracker (EU Institutions)",
        "org": "Google News / europa.eu",
        "region": "eu",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+policy+site:europa.eu&hl=en-US&gl=US&ceid=US:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "policy",
            "regulation",
            "governance",
            "guideline",
            "safety",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "federal_register_ai_policy",
        "name": "US Federal Register (AI Policy)",
        "org": "Federal Register",
        "region": "us",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://www.federalregister.gov/api/v1/articles.rss?conditions%5Bterm%5D=artificial+intelligence",
        "homepage": "https://www.federalregister.gov/",
        "required_keywords": [
            "artificial intelligence",
            "ai",
            "rule",
            "regulation",
            "policy",
            "notice",
            "compliance",
            "governance",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_policy_india_gov",
        "name": "AI Policy Tracker (India Gov)",
        "org": "Google News / gov.in",
        "region": "apac",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+policy+site:gov.in&hl=en-US&gl=US&ceid=US:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "policy",
            "regulation",
            "governance",
            "guideline",
            "safety",
            "risk",
        ],
        "max_age_days": 90,
    },
    {
        "id": "google_news_policy_canada_gov",
        "name": "AI Policy Tracker (Canada Gov)",
        "org": "Google News / canada.ca",
        "region": "global",
        "kind": "policy_safety",
        "feed_type": "rss",
        "feed_url": "https://news.google.com/rss/search?q=AI+policy+site:canada.ca&hl=en-US&gl=US&ceid=US:en",
        "homepage": "https://news.google.com/",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "policy",
            "regulation",
            "governance",
            "guideline",
            "safety",
            "risk",
        ],
        "max_age_days": 90,
    },
    # GitHub open-source ecosystem (tool discovery signal, not release stream)
    {
        "id": "oschina_news_ai_oss",
        "name": "OSChina News (AI Open Source Signals)",
        "org": "OSChina",
        "region": "cn",
        "kind": "oss_signal",
        "feed_type": "rss",
        "feed_url": "https://www.oschina.net/news/rss",
        "homepage": "https://www.oschina.net/news",
        "required_keywords": [
            "ai",
            "artificial intelligence",
            "llm",
            "open source",
            "github",
            "gitee",
            "agent",
            "framework",
            "tool",
            "library",
        ],
        "max_age_days": 90,
    },
    {
        "id": "qiita_ai_oss",
        "name": "Qiita AI Tag (Open Source Signals)",
        "org": "Qiita",
        "region": "jp",
        "kind": "oss_signal",
        "feed_type": "atom",
        "feed_url": "https://qiita.com/tags/AI/feed",
        "homepage": "https://qiita.com/tags/AI",
        "required_keywords": [
            "ai",
            "llm",
            "open source",
            "github",
            "library",
            "framework",
            "tool",
            "agent",
        ],
        "max_age_days": 90,
    },
    {
        "id": "qiita_ml_oss",
        "name": "Qiita ML Tag (Open Source Signals)",
        "org": "Qiita",
        "region": "jp",
        "kind": "oss_signal",
        "feed_type": "atom",
        "feed_url": "https://qiita.com/tags/%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92/feed",
        "homepage": "https://qiita.com/tags/%E6%A9%9F%E6%A2%B0%E5%AD%A6%E7%BF%92",
        "required_keywords": [
            "ai",
            "llm",
            "open source",
            "github",
            "library",
            "framework",
            "tool",
            "agent",
        ],
        "max_age_days": 90,
    },
    {
        "id": "zenn_ai_oss",
        "name": "Zenn AI Topic (Open Source Signals)",
        "org": "Zenn",
        "region": "jp",
        "kind": "oss_signal",
        "feed_type": "rss",
        "feed_url": "https://zenn.dev/topics/ai/feed",
        "homepage": "https://zenn.dev/topics/ai",
        "required_keywords": [
            "ai",
            "llm",
            "open source",
            "github",
            "library",
            "framework",
            "tool",
            "agent",
        ],
        "max_age_days": 90,
    },
    {
        "id": "zenn_llm_oss",
        "name": "Zenn LLM Topic (Open Source Signals)",
        "org": "Zenn",
        "region": "jp",
        "kind": "oss_signal",
        "feed_type": "rss",
        "feed_url": "https://zenn.dev/topics/llm/feed",
        "homepage": "https://zenn.dev/topics/llm",
        "required_keywords": [
            "ai",
            "llm",
            "open source",
            "github",
            "library",
            "framework",
            "tool",
            "agent",
        ],
        "max_age_days": 90,
    },
    {
        "id": "reddit_localllama_oss",
        "name": "Reddit r/LocalLLaMA (OSS Signals)",
        "org": "Reddit",
        "region": "us",
        "kind": "oss_signal",
        "feed_type": "atom",
        "feed_url": "https://www.reddit.com/r/LocalLLaMA/.rss",
        "homepage": "https://www.reddit.com/r/LocalLLaMA/",
        "required_keywords": [
            "open source",
            "github",
            "llm",
            "model",
            "release",
            "repo",
            "agent",
            "tool",
            "framework",
        ],
        "max_age_days": 90,
    },
    {
        "id": "hnrss_ai_oss",
        "name": "HNRSS AI Query (OSS Signals)",
        "org": "Hacker News",
        "region": "us",
        "kind": "oss_signal",
        "feed_type": "rss",
        "feed_url": "https://hnrss.org/newest?q=AI",
        "homepage": "https://news.ycombinator.com/",
        "required_keywords": [
            "open source",
            "github",
            "repo",
            "ai",
            "llm",
            "agent",
            "framework",
            "library",
            "tool",
        ],
        "max_age_days": 90,
    },
    {
        "id": "github_trending_daily",
        "name": "GitHub Trending AI Tools (Daily)",
        "org": "GitHub Trending",
        "region": "global",
        "kind": "oss_signal",
        "feed_type": "github_trending",
        "feed_url": "https://github.com/trending?since=daily",
        "homepage": "https://github.com/trending?since=daily",
        "readme_gate": True,
        "readme_min_score": 5,
        "require_readme": True,
        "max_age_days": 90,
        "scan_limit": 120,
    },
    {
        "id": "github_trending_weekly",
        "name": "GitHub Trending AI Tools (Weekly)",
        "org": "GitHub Trending",
        "region": "global",
        "kind": "oss_signal",
        "feed_type": "github_trending",
        "feed_url": "https://github.com/trending?since=weekly",
        "homepage": "https://github.com/trending?since=weekly",
        "readme_gate": True,
        "readme_min_score": 5,
        "require_readme": True,
        "max_age_days": 90,
        "scan_limit": 140,
    },
    {
        "id": "github_trending_weekly_zh",
        "name": "GitHub Trending AI Tools (Weekly, Chinese)",
        "org": "GitHub Trending",
        "region": "cn",
        "kind": "oss_signal",
        "feed_type": "github_trending",
        "feed_url": "https://github.com/trending?since=weekly&spoken_language_code=zh",
        "homepage": "https://github.com/trending?since=weekly&spoken_language_code=zh",
        "readme_gate": True,
        "readme_min_score": 5,
        "require_readme": True,
        "max_age_days": 90,
        "scan_limit": 140,
    },
    {
        "id": "github_trending_weekly_ja",
        "name": "GitHub Trending AI Tools (Weekly, Japanese)",
        "org": "GitHub Trending",
        "region": "jp",
        "kind": "oss_signal",
        "feed_type": "github_trending",
        "feed_url": "https://github.com/trending?since=weekly&spoken_language_code=ja",
        "homepage": "https://github.com/trending?since=weekly&spoken_language_code=ja",
        "readme_gate": True,
        "readme_min_score": 5,
        "require_readme": True,
        "max_age_days": 90,
        "scan_limit": 140,
    },
    {
        "id": "github_trending_weekly_ko",
        "name": "GitHub Trending AI Tools (Weekly, Korean)",
        "org": "GitHub Trending",
        "region": "kr",
        "kind": "oss_signal",
        "feed_type": "github_trending",
        "feed_url": "https://github.com/trending?since=weekly&spoken_language_code=ko",
        "homepage": "https://github.com/trending?since=weekly&spoken_language_code=ko",
        "readme_gate": True,
        "readme_min_score": 5,
        "require_readme": True,
        "max_age_days": 90,
        "scan_limit": 140,
    },
    {
        "id": "github_trending_weekly_fr",
        "name": "GitHub Trending AI Tools (Weekly, French)",
        "org": "GitHub Trending",
        "region": "fr",
        "kind": "oss_signal",
        "feed_type": "github_trending",
        "feed_url": "https://github.com/trending?since=weekly&spoken_language_code=fr",
        "homepage": "https://github.com/trending?since=weekly&spoken_language_code=fr",
        "readme_gate": True,
        "readme_min_score": 5,
        "require_readme": True,
        "max_age_days": 90,
        "scan_limit": 140,
    },
    {
        "id": "github_trending_weekly_en",
        "name": "GitHub Trending AI Tools (Weekly, English)",
        "org": "GitHub Trending",
        "region": "uk",
        "kind": "oss_signal",
        "feed_type": "github_trending",
        "feed_url": "https://github.com/trending?since=weekly&spoken_language_code=en",
        "homepage": "https://github.com/trending?since=weekly&spoken_language_code=en",
        "readme_gate": True,
        "readme_min_score": 5,
        "require_readme": True,
        "max_age_days": 90,
        "scan_limit": 140,
    },
]


AI_RELEVANT_KEYWORDS = [
    "ai",
    "llm",
    "agent",
    "model",
    "reasoning",
    "multimodal",
    "alignment",
    "eval",
    "benchmark",
    "inference",
    "fine-tuning",
    "quantization",
    "rag",
    "transformer",
    "safety",
    "policy",
    "open-weight",
    "token",
    "预训练",
    "推理",
    "多模态",
    "智能体",
    "对齐",
    "基准",
    "评测",
    "开源",
    "模型",
]

AI_CORE_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "llm",
    "large language model",
    "foundation model",
    "agent",
    "model",
    "reasoning",
    "multimodal",
    "inference",
    "fine-tuning",
    "quantization",
    "rag",
    "transformer",
    "token",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _normalize_text(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _normalize_lang_key(value: Any) -> str:
    raw = str(value or "").strip().lower().replace("_", "-")
    if not raw:
        return ""
    alias = {
        "english": "en",
        "chinese": "zh",
        "traditional chinese": "zh-hant",
        "korean": "ko",
        "japanese": "ja",
        "french": "fr",
    }
    mapped = alias.get(raw)
    if mapped:
        return mapped
    safe = re.sub(r"[^a-z0-9\\-]+", "-", raw).strip("-")
    return safe


DEFAULT_SOURCE_MAX_AGE_DAYS = 90
SEEN_HISTORY_RETENTION_DAYS = 365
TRACKING_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "igshid",
    "mc_cid",
    "mc_eid",
    "spm",
    "ref",
}


def _parse_dt(value: str) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None

    dt: Optional[datetime] = None
    try:
        dt = parsedate_to_datetime(text)
    except Exception:
        dt = None

    if dt is None:
        v = text.replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(v)
        except Exception:
            dt = None

    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _canonicalize_url(url: str) -> str:
    raw = str(url or "").strip()
    if not raw:
        return ""
    try:
        parts = urlsplit(raw)
    except Exception:
        return raw
    host = parts.netloc.lower()
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    query_pairs = []
    for k, v in parse_qsl(parts.query, keep_blank_values=False):
        key = str(k or "").strip()
        if not key:
            continue
        if key.lower() in TRACKING_QUERY_KEYS or key.lower().startswith("utm_"):
            continue
        query_pairs.append((key, str(v or "").strip()))
    query_pairs.sort(key=lambda x: (x[0].lower(), x[1]))
    query = urlencode(query_pairs, doseq=True)
    return urlunsplit((parts.scheme.lower(), host, path, query, ""))


def _infer_date_from_url(url: str) -> str:
    text = str(url or "").strip().lower()
    if not text:
        return ""

    patterns = [
        r"(?:^|[^\d])(20\d{2})([01]\d)([0-3]\d)(?:[^\d]|$)",
        r"(?:^|[^\d])(\d{2})([01]\d)([0-3]\d)(?:[^\d]|$)",
    ]
    for idx, pattern in enumerate(patterns):
        matched = re.search(pattern, text)
        if not matched:
            continue
        try:
            if idx == 0:
                year = int(matched.group(1))
                month = int(matched.group(2))
                day = int(matched.group(3))
            else:
                yy = int(matched.group(1))
                year = 2000 + yy
                month = int(matched.group(2))
                day = int(matched.group(3))
            dt = datetime(year, month, day, tzinfo=timezone.utc)
            return dt.isoformat(timespec="seconds")
        except Exception:
            continue

    matched = re.search(r"(20\d{2})[-_/\.]([01]?\d)[-_/\.]([0-3]?\d)", text)
    if matched:
        try:
            dt = datetime(
                int(matched.group(1)),
                int(matched.group(2)),
                int(matched.group(3)),
                tzinfo=timezone.utc,
            )
            return dt.isoformat(timespec="seconds")
        except Exception:
            return ""
    return ""


MODEL_SIGNAL_KEYWORDS = [
    "qwen", "deepseek", "glm", "z.ai", "zhipu", "yi", "baichuan", "minimax", "internlm", "ernie",
    "model", "base", "instruct", "chat", "coder", "reasoning", "multimodal", "vision", "audio", "video",
    "open-weight", "open source", "weights", "checkpoint", "moe", "rl", "r1", "r2",
    "模型", "权重", "推理", "多模态", "视觉", "语音", "视频", "开源", "发布",
]

RELEASE_BLOCK_KEYWORDS = [
    "sdk", "client", "api client", "python", "typescript", "javascript", "java", "golang",
    "agent", "framework", "toolkit", "plugin", "binding", "wrapper", "dependency", "deps",
    "bugfix", "hotfix", "chore", "maintenance", "refactor", "ci", "lint", "docs only",
    "tooling", "autogen", "semantic kernel", "langchain", "transformers", "modelscope", "qwen-agent",
    "examples", "sample app", "demo app", "兼容性", "修复", "示例", "工具链", "插件",
]


FINANCE_MARKET_KEYWORDS = [
    "earnings",
    "earnings call",
    "guidance",
    "capex",
    "capital expenditure",
    "revenue",
    "gross margin",
    "operating income",
    "eps",
    "share buyback",
    "stock",
    "shares",
    "analyst",
    "data center",
    "ai infrastructure",
    "融资",
    "并购",
    "财报",
    "指引",
    "资本开支",
    "股价",
]

AI_EQUITY_SIGNAL_KEYWORDS = [
    "nvidia",
    "nvda",
    "amd",
    "microsoft",
    "msft",
    "google",
    "alphabet",
    "googl",
    "meta",
    "amazon",
    "amzn",
    "broadcom",
    "avgo",
    "tsmc",
    "tsm",
    "asml",
    "arm",
    "alibaba",
    "9988.hk",
    "9618.hk",
    "1810.hk",
    "3690.hk",
    "9888.hk",
    "tencent",
    "0700.hk",
    "samsung",
    "005930.ks",
    "sk hynix",
    "000660.ks",
    "naver",
    "035420.ks",
    "kakao",
    "035720.ks",
    "sony",
    "6758.t",
    "softbank",
    "9984.t",
    "tokyo electron",
    "8035.t",
    "shin-etsu",
    "4063.t",
    "renesas",
    "6723.t",
    "arm holdings",
    "darktrace",
    "dark.l",
    "relx",
    "rel.l",
    "spx.l",
    "capgemini",
    "cap.pa",
    "dassault systemes",
    "dsy.pa",
    "orange",
    "ora.pa",
    "france",
    "united kingdom",
    "hong kong",
    "south korea",
]

REPORT_SIGNAL_KEYWORDS = [
    "report",
    "research",
    "survey",
    "forecast",
    "market size",
    "adoption",
    "whitepaper",
    "insight",
    "outlook",
    "analysis",
    "study",
    "brief",
    "state of",
    "index",
    "roadmap",
    "trend",
    "报告",
    "研究",
    "白皮书",
    "预测",
]

POLICY_SAFETY_KEYWORDS = [
    "policy",
    "regulation",
    "regulatory",
    "governance",
    "compliance",
    "law",
    "act",
    "bill",
    "guideline",
    "guidelines",
    "framework",
    "directive",
    "executive order",
    "standard",
    "safety",
    "risk",
    "security",
    "privacy",
    "data protection",
    "copyright",
    "liability",
    "trustworthy ai",
    "guardrails",
    "guardrail",
    "监管",
    "合规",
    "治理",
    "标准",
    "安全",
    "风险",
]

LOW_QUALITY_BLOCK_KEYWORDS = [
    "cookie policy",
    "privacy policy",
    "terms of use",
    "javascript required",
    "enable javascript",
    "sign in",
    "login",
]

GITHUB_README_KEYWORDS_HIGH = [
    "large language model",
    "llm",
    "generative ai",
    "machine learning",
    "deep learning",
    "neural network",
    "multimodal",
    "transformer",
    "diffusion",
    "inference engine",
    "model serving",
]

GITHUB_README_KEYWORDS_MEDIUM = [
    "fine-tuning",
    "rag",
    "vector database",
    "tokenizer",
    "prompt",
    "embedding",
    "vision-language",
    "speech model",
    "rlhf",
    "benchmark",
]

GITHUB_README_MIN_SCORE = 3

GITHUB_RELEASE_NOISE_KEYWORDS = [
    "docs:",
    "doc:",
    "documentation",
    "readme",
    "typo",
    "chore",
    "lint",
    "dependency bump",
    "deps:",
    "ci:",
    "test fix",
]

OSS_DISCOVERY_KEYWORDS = [
    "agent",
    "framework",
    "toolkit",
    "sdk",
    "inference",
    "serving",
    "workflow",
    "automation",
    "open source",
    "repository",
    "library",
]


def _contains_keyword(content: str, keywords: List[str]) -> bool:
    lowered = str(content or "").lower()
    for raw in keywords:
        keyword = str(raw or "").strip().lower()
        if not keyword:
            continue
        if len(keyword) <= 3 and re.fullmatch(r"[a-z0-9]+", keyword):
            if re.search(rf"\b{re.escape(keyword)}\b", lowered):
                return True
            continue
        if keyword in lowered:
            return True
    return False


def _looks_like_version_title(title: str) -> bool:
    text = _normalize_text(title).lower()
    if not text:
        return False
    return bool(re.search(r"\bv?\d+(?:\.\d+){1,3}(?:-(?:rc|beta|alpha)\d*)?\b", text))


def _is_low_quality_entry(title: str, summary: str, kind: str = "") -> bool:
    title_text = _normalize_text(title).lower()
    summary_text = _normalize_text(summary).lower()
    kind_text = str(kind or "").strip().lower()
    if len(title_text) < 8:
        if kind_text == "github_release" and _looks_like_version_title(title_text):
            return False
        if kind_text == "oss_signal" and ("/" in title_text or len(title_text) >= 3):
            return False
        return True
    merged = f"{title_text} {summary_text}"
    return _contains_keyword(merged, LOW_QUALITY_BLOCK_KEYWORDS)


def _github_readme_ai_score(readme_text: str) -> int:
    merged = _normalize_text(readme_text).lower()
    if not merged:
        return 0
    score = 0
    for kw in GITHUB_README_KEYWORDS_HIGH:
        if kw in merged:
            score += 2
    for kw in GITHUB_README_KEYWORDS_MEDIUM:
        if kw in merged:
            score += 1
    return score


def _html_attr_unescape(value: str) -> str:
    return html.unescape(str(value or "")).strip()


def _parse_dt_iso(value: str) -> str:
    dt = _parse_dt(value)
    if dt is None:
        return ""
    return dt.isoformat(timespec="seconds")


def _has_model_signal(content: str) -> bool:
    lowered = str(content or "").lower()
    return any(k in lowered for k in MODEL_SIGNAL_KEYWORDS)


def _looks_like_tooling_release(content: str) -> bool:
    lowered = str(content or "").lower()
    return any(k in lowered for k in RELEASE_BLOCK_KEYWORDS)


def _is_ai_relevant(title: str, summary: str, tags: List[str], kind: str, source: Optional[Dict[str, Any]] = None) -> bool:
    source_hint = ""
    if isinstance(source, dict):
        source_hint = " ".join(
            [
                str(source.get("id", "") or ""),
                str(source.get("name", "") or ""),
                str(source.get("org", "") or ""),
            ]
        )
    core_content = " ".join([title, summary, " ".join(tags)]).lower()
    content_with_source = " ".join([core_content, source_hint]).lower()
    ai_hit = _has_model_signal(core_content) or _contains_keyword(core_content, AI_CORE_KEYWORDS)

    if isinstance(source, dict):
        region = str(source.get("region", "") or "").strip().lower()
        if region == "cn" and kind in {"official_blog", "official_site"}:
            return True

    if kind == "github_release":
        if _contains_keyword(core_content, GITHUB_RELEASE_NOISE_KEYWORDS) and not _looks_like_version_title(title):
            return False
        if _looks_like_version_title(title):
            return True
        return ai_hit or _contains_keyword(core_content, ["release", "launch"])

    if kind == "market_finance":
        finance_hit = _contains_keyword(core_content, FINANCE_MARKET_KEYWORDS)
        equity_hit = _contains_keyword(core_content, AI_EQUITY_SIGNAL_KEYWORDS)
        return finance_hit and (ai_hit or equity_hit)

    if kind == "industry_report":
        return ai_hit and _contains_keyword(core_content, REPORT_SIGNAL_KEYWORDS)

    if kind == "policy_safety":
        return ai_hit and _contains_keyword(core_content, POLICY_SAFETY_KEYWORDS)

    if kind == "oss_signal":
        # OSS discovery is primarily gated by README semantic checks.
        return True

    # For default sources, still allow weak source hints to reduce false negatives.
    return ai_hit or _contains_keyword(content_with_source, AI_CORE_KEYWORDS)


def _infer_event_type(title: str, summary: str, kind: str) -> str:
    content = f"{title} {summary}".lower()
    if kind == "github_release":
        if _contains_keyword(content, GITHUB_RELEASE_NOISE_KEYWORDS) and not _looks_like_version_title(title):
            return "update"
        if _looks_like_version_title(title):
            return "release"
        return "release" if _has_model_signal(content) and not _looks_like_tooling_release(content) else "update"
    if kind == "policy_safety":
        return "safety"
    if kind == "industry_report":
        return "report"
    if kind == "market_finance":
        return "report" if _contains_keyword(content, FINANCE_MARKET_KEYWORDS) else "update"
    if kind == "oss_signal":
        return "update"
    if any(k in content for k in ["benchmark", "leaderboard", "eval", "assessment"]):
        return "benchmark"
    if any(k in content for k in ["safety", "policy", "governance", "regulation", "compliance"]):
        return "safety"
    if any(k in content for k in ["report", "whitepaper", "technical report", "forecast", "survey"]):
        return "report"
    if any(k in content for k in ["release", "launch", "introduc", "open source"]):
        return "release"
    return "update"


def _passes_source_filters(item: Dict[str, Any], source: Optional[Dict[str, Any]]) -> bool:
    if not isinstance(source, dict):
        return True

    title = str(item.get("title", "") or "")
    summary = str(item.get("summary", "") or "")
    url = str(item.get("url", "") or "")
    tags = item.get("tags") if isinstance(item.get("tags"), list) else []
    merged = " ".join([title, summary, url, " ".join([str(x or "") for x in tags])]).lower()

    required_keywords = [str(x or "").strip() for x in source.get("required_keywords", []) if str(x or "").strip()]
    if required_keywords and not _contains_keyword(merged, required_keywords):
        return False

    blocked_keywords = [str(x or "").strip() for x in source.get("blocked_keywords", []) if str(x or "").strip()]
    if blocked_keywords and _contains_keyword(merged, blocked_keywords):
        return False

    kind_text = str(item.get("kind", "") or source.get("kind", "") or "").strip().lower()
    if kind_text == "market_finance":
        entity_keywords = [
            str(x or "").strip().lower()
            for x in source.get("entity_keywords", [])
            if str(x or "").strip()
        ]
        ticker_allowlist = [
            str(x or "").strip().lower()
            for x in source.get("ticker_allowlist", [])
            if str(x or "").strip()
        ]
        if entity_keywords or ticker_allowlist:
            entity_scope = merged
            if bool(source.get("strict_entity_match")):
                entity_scope = f"{title} {url}".lower()
            if not _contains_keyword(entity_scope, entity_keywords + ticker_allowlist):
                return False

    return True

def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1].lower()
    return tag.lower()


def _first_child_text(parent: ET.Element, names: List[str]) -> str:
    names_set = {x.lower() for x in names}
    for child in list(parent):
        if _local_name(child.tag) in names_set:
            return _normalize_text(child.text or "")
    return ""


def _all_child_texts(parent: ET.Element, names: List[str]) -> List[str]:
    names_set = {x.lower() for x in names}
    out: List[str] = []
    for child in list(parent):
        if _local_name(child.tag) in names_set:
            text = _normalize_text(child.text or child.attrib.get("term", ""))
            if text:
                out.append(text)
    return out


def _entry_link(entry: ET.Element) -> str:
    for child in list(entry):
        if _local_name(child.tag) != "link":
            continue
        href = str(child.attrib.get("href", "") or "").strip()
        rel = str(child.attrib.get("rel", "") or "").strip().lower()
        if href and (rel in {"", "alternate"}):
            return href
    for child in list(entry):
        if _local_name(child.tag) == "link":
            href = str(child.attrib.get("href", "") or "").strip()
            if href:
                return href
            text_link = _normalize_text(child.text or "")
            if text_link:
                return text_link
    return ""


def _absolutize_url(url: str, source: Dict[str, Any]) -> str:
    raw = str(url or "").strip()
    if not raw:
        return ""
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    base = str(source.get("homepage", "") or source.get("feed_url", "") or "").strip()
    if not base:
        return raw
    return urljoin(base, raw)


class AIProgressRepository:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.path = output_dir / "ai_progress_items.json"
        self.seen_path = output_dir / "ai_progress_seen.json"
        self._lock = threading.RLock()
        self.sources = [dict(x) for x in OFFICIAL_AI_PROGRESS_SOURCES]
        self.source_by_id = {str(x.get("id", "") or "").strip(): dict(x) for x in self.sources}
        self._github_readme_cache: Dict[str, bool] = {}

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        source_id = str(item.get("source_id", "") or "").strip()
        title = _normalize_text(item.get("title", ""))
        title_zh = _normalize_text(item.get("title_zh", ""))
        url = _canonicalize_url(str(item.get("url", "") or "").strip())
        published_at = _parse_dt_iso(str(item.get("published_at", "") or "").strip())
        if not published_at:
            published_at = _infer_date_from_url(url)
        summary = _normalize_text(item.get("summary", ""))[:6000]
        summary_zh = _normalize_text(item.get("summary_zh", ""))[:6000]
        llm_takeaway_zh = _normalize_text(item.get("llm_takeaway_zh", ""))[:600]
        raw_i18n = item.get("i18n") if isinstance(item.get("i18n"), dict) else {}
        i18n: Dict[str, Dict[str, str]] = {}
        if isinstance(raw_i18n, dict):
            for raw_lang, raw_payload in raw_i18n.items():
                lang_key = _normalize_lang_key(raw_lang)
                if not lang_key or not isinstance(raw_payload, dict):
                    continue
                entry_title = _normalize_text(raw_payload.get("title", ""))[:400]
                entry_summary = _normalize_text(raw_payload.get("summary", ""))[:6000]
                entry_takeaway = _normalize_text(raw_payload.get("llm_takeaway", ""))[:600]
                if not (entry_title or entry_summary or entry_takeaway):
                    continue
                i18n[lang_key] = {
                    "title": entry_title,
                    "summary": entry_summary,
                    "llm_takeaway": entry_takeaway,
                }
        tags_raw = item.get("tags") if isinstance(item.get("tags"), list) else []
        tags = [_normalize_text(x) for x in tags_raw if _normalize_text(x)]
        canonical = url or f"{source_id}:{title}:{published_at}"
        key = hashlib.sha1(canonical.encode("utf-8", errors="ignore")).hexdigest()[:20]
        return {
            "progress_key": key,
            "source_id": source_id,
            "source_name": str(item.get("source_name", "") or "").strip(),
            "org": str(item.get("org", "") or "").strip(),
            "region": str(item.get("region", "global") or "global").strip().lower(),
            "kind": str(item.get("kind", "official_blog") or "official_blog").strip().lower(),
            "event_type": str(item.get("event_type", "update") or "update").strip().lower(),
            "title": title,
            "title_zh": title_zh,
            "summary": summary,
            "summary_zh": summary_zh,
            "llm_takeaway_zh": llm_takeaway_zh,
            "i18n": i18n,
            "url": url,
            "published_at": published_at,
            "tags": tags,
            "fetched_at": _parse_dt_iso(str(item.get("fetched_at", "") or "")) or _utc_now_iso(),
        }

    def _max_age_days_for_source(self, source_meta: Dict[str, Any]) -> int:
        raw = source_meta.get("max_age_days", DEFAULT_SOURCE_MAX_AGE_DAYS) if isinstance(source_meta, dict) else DEFAULT_SOURCE_MAX_AGE_DAYS
        try:
            value = int(raw)
        except Exception:
            value = DEFAULT_SOURCE_MAX_AGE_DAYS
        return max(1, value)

    def _is_recent_item(self, item: Dict[str, Any], source_meta: Dict[str, Any]) -> bool:
        max_age_days = self._max_age_days_for_source(source_meta)
        published = str(item.get("published_at", "") or "").strip()
        dt = _parse_dt(published)
        if dt is None:
            return False
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        return dt >= cutoff

    @staticmethod
    def _history_signature(item: Dict[str, Any]) -> str:
        url = _canonicalize_url(str(item.get("url", "") or ""))
        published = str(item.get("published_at", "") or "")
        title = AIProgressRepository._dedupe_text(item.get("title", "") or item.get("title_zh", ""))
        source_id = str(item.get("source_id", "") or "").strip().lower()
        if url:
            payload = f"{source_id}|url|{url}"
        else:
            payload = f"{source_id}|title|{title}|{published[:10]}"
        return hashlib.sha1(payload.encode("utf-8", errors="ignore")).hexdigest()

    def _load_seen_index(self) -> Dict[str, Dict[str, Any]]:
        if not self.seen_path.exists():
            return {}
        try:
            data = json.loads(self.seen_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        out: Dict[str, Dict[str, Any]] = {}
        if isinstance(data, dict):
            items = data.get("items")
            if isinstance(items, dict):
                for key, value in items.items():
                    if not isinstance(key, str) or not isinstance(value, dict):
                        continue
                    out[key] = dict(value)
        return out

    def _save_seen_index(self, seen_index: Dict[str, Dict[str, Any]]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "items": seen_index,
            "updated_at": _utc_now_iso(),
        }
        self.seen_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _touch_seen_index(self, seen_index: Dict[str, Dict[str, Any]], signature: str, progress_key: str) -> None:
        now = _utc_now_iso()
        record = seen_index.get(signature)
        if not isinstance(record, dict):
            seen_index[signature] = {
                "first_seen": now,
                "last_seen": now,
                "count": 1,
                "progress_key": progress_key,
            }
            return
        count = int(record.get("count", 0) or 0) + 1
        record["count"] = count
        record["last_seen"] = now
        if not record.get("first_seen"):
            record["first_seen"] = now
        if progress_key:
            record["progress_key"] = progress_key

    def _prune_seen_index(self, seen_index: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=SEEN_HISTORY_RETENTION_DAYS)
        pruned: Dict[str, Dict[str, Any]] = {}
        for key, value in seen_index.items():
            if not isinstance(value, dict):
                continue
            anchor = _parse_dt(str(value.get("last_seen", "") or value.get("first_seen", "") or ""))
            if anchor is not None and anchor < cutoff:
                continue
            pruned[key] = value
        return pruned

    @staticmethod
    def _merge_existing_item(existing: Dict[str, Any], incoming: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(incoming)
        english_changed = (
            str(existing.get("title", "") or "") != str(incoming.get("title", "") or "")
            or str(existing.get("summary", "") or "") != str(incoming.get("summary", "") or "")
        )
        if not english_changed:
            for field in ("title_zh", "summary_zh", "llm_takeaway_zh"):
                preserved = _normalize_text(existing.get(field, ""))
                if preserved and not _normalize_text(merged.get(field, "")):
                    merged[field] = preserved
        return merged

    def _normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        items = data.get("items") if isinstance(data, dict) else []
        out: List[Dict[str, Any]] = []
        seen = set()
        if isinstance(items, list):
            for raw in items:
                if not isinstance(raw, dict):
                    continue
                normalized = self._normalize_item(raw)
                source_id = str(normalized.get("source_id", "") or "").strip()
                if source_id and source_id not in self.source_by_id:
                    continue
                source_meta = self.source_by_id.get(str(normalized.get("source_id", "") or "").strip(), {})
                if not _passes_source_filters(normalized, source_meta):
                    continue
                if not _is_ai_relevant(
                    normalized.get("title", ""),
                    normalized.get("summary", ""),
                    normalized.get("tags", []),
                    normalized.get("kind", ""),
                    source_meta,
                ):
                    continue
                normalized["event_type"] = _infer_event_type(
                    normalized.get("title", ""),
                    normalized.get("summary", ""),
                    normalized.get("kind", ""),
                )
                if not self._is_recent_item(normalized, source_meta):
                    continue
                key = normalized["progress_key"]
                if key in seen:
                    continue
                seen.add(key)
                out.append(normalized)
        out.sort(key=lambda x: (x.get("published_at", ""), x.get("fetched_at", "")), reverse=True)
        deduped_items, deduped_count = self._dedupe_items(out)
        return {"items": deduped_items[:4000], "updated_at": _utc_now_iso(), "deduped": deduped_count}

    @staticmethod
    def _dedupe_text(value: Any) -> str:
        text = _normalize_text(value).lower()
        text = re.sub(r"[\W_]+", " ", text, flags=re.UNICODE)
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def _extract_version_markers(cls, item: Dict[str, Any]) -> set[str]:
        merged = " ".join(
            [
                str(item.get("title", "") or ""),
                str(item.get("title_zh", "") or ""),
            ]
        )
        values = re.findall(r"\bv?\d+(?:\.\d+){0,3}\b", merged.lower())
        return {v.lstrip("v") for v in values if v}

    @classmethod
    def _title_similarity(cls, left: Dict[str, Any], right: Dict[str, Any]) -> float:
        pairs = [
            (left.get("title", ""), right.get("title", "")),
            (left.get("title_zh", ""), right.get("title_zh", "")),
            (left.get("title", ""), right.get("title_zh", "")),
            (left.get("title_zh", ""), right.get("title", "")),
        ]
        best = 0.0
        for raw_a, raw_b in pairs:
            a = cls._dedupe_text(raw_a)
            b = cls._dedupe_text(raw_b)
            if not a or not b:
                continue
            if a == b:
                return 1.0
            ratio = SequenceMatcher(None, a, b).ratio()
            shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
            containment = 0.0
            if len(shorter) >= 18 and shorter in longer:
                containment = len(shorter) / max(len(longer), 1)
            a_tokens = set(a.split())
            b_tokens = set(b.split())
            jaccard = 0.0
            if a_tokens and b_tokens:
                jaccard = len(a_tokens & b_tokens) / len(a_tokens | b_tokens)
            best = max(best, ratio, containment, jaccard)
        return best

    @staticmethod
    def _dedupe_bucket_keys(item: Dict[str, Any]) -> List[str]:
        keys: List[str] = []
        for prefix, raw in (
            ("source_id", item.get("source_id", "")),
            ("source_name", item.get("source_name", "")),
            ("org", item.get("org", "")),
        ):
            value = str(raw or "").strip().lower()
            if value:
                keys.append(f"{prefix}:{value}")
        return keys

    @staticmethod
    def _completeness_score(item: Dict[str, Any]) -> int:
        score = 0
        score += len(str(item.get("summary", "") or "").strip())
        score += len(str(item.get("summary_zh", "") or "").strip()) * 2
        score += len(str(item.get("llm_takeaway_zh", "") or "").strip()) * 3
        score += len(item.get("tags") or []) * 8
        return score

    @staticmethod
    def _source_preference(item: Dict[str, Any]) -> int:
        kind = str(item.get("kind", "") or "").strip().lower()
        if kind in {"official_blog", "official_site"}:
            return 4
        if kind == "policy_safety":
            return 3
        if kind == "industry_report":
            return 2
        if kind == "market_finance":
            return 1
        if kind == "oss_signal":
            return 1
        if kind == "github_release":
            return 0
        return 0

    @classmethod
    def _choose_preferred_item(cls, left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
        left_key = (
            cls._source_preference(left),
            str(left.get("published_at", "") or ""),
            cls._completeness_score(left),
            str(left.get("fetched_at", "") or ""),
        )
        right_key = (
            cls._source_preference(right),
            str(right.get("published_at", "") or ""),
            cls._completeness_score(right),
            str(right.get("fetched_at", "") or ""),
        )
        return left if left_key >= right_key else right

    @classmethod
    def _is_near_duplicate(cls, left: Dict[str, Any], right: Dict[str, Any]) -> bool:
        if not set(cls._dedupe_bucket_keys(left)) & set(cls._dedupe_bucket_keys(right)):
            return False
        left_versions = cls._extract_version_markers(left)
        right_versions = cls._extract_version_markers(right)
        if left_versions and right_versions and left_versions.isdisjoint(right_versions):
            return False
        return cls._title_similarity(left, right) >= 0.9

    @classmethod
    def _dedupe_items(cls, items: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        deduped: List[Dict[str, Any]] = []
        url_index: Dict[str, int] = {}
        bucket_index: Dict[str, List[int]] = {}
        deduped_count = 0

        def register_item(idx: int, row: Dict[str, Any]) -> None:
            normalized_url = str(row.get("url", "") or "").strip().lower()
            if normalized_url:
                url_index[normalized_url] = idx
            for key in cls._dedupe_bucket_keys(row):
                refs = bucket_index.setdefault(key, [])
                if idx not in refs:
                    refs.append(idx)

        for item in items:
            normalized_url = str(item.get("url", "") or "").strip().lower()
            if normalized_url and normalized_url in url_index:
                kept_idx = url_index[normalized_url]
                preferred = cls._choose_preferred_item(item, deduped[kept_idx])
                deduped[kept_idx] = preferred
                register_item(kept_idx, preferred)
                deduped_count += 1
                continue

            candidate_indexes: set[int] = set()
            for key in cls._dedupe_bucket_keys(item):
                candidate_indexes.update(bucket_index.get(key, []))

            matched_idx: Optional[int] = None
            for idx in sorted(candidate_indexes):
                if cls._is_near_duplicate(item, deduped[idx]):
                    matched_idx = idx
                    break

            if matched_idx is not None:
                preferred = cls._choose_preferred_item(item, deduped[matched_idx])
                deduped[matched_idx] = preferred
                register_item(matched_idx, preferred)
                deduped_count += 1
                continue

            new_idx = len(deduped)
            deduped.append(item)
            register_item(new_idx, item)

        return deduped, deduped_count

    def load(self) -> Dict[str, Any]:
        with self._lock:
            if not self.path.exists():
                return {"items": [], "updated_at": ""}
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return self._normalize(data)
            except Exception:
                pass
            return {"items": [], "updated_at": ""}

    def save(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            normalized = self._normalize(data or {})
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
            return normalized

    def list_sources(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": str(s.get("id", "")),
                "name": str(s.get("name", "")),
                "org": str(s.get("org", "")),
                "region": str(s.get("region", "global")),
                "kind": str(s.get("kind", "official_blog")),
                "feed_type": str(s.get("feed_type", "rss")),
                "feed_url": str(s.get("feed_url", "")),
                "sitemap_url": str(s.get("sitemap_url", "")),
                "homepage": str(s.get("homepage", "")),
                "max_age_days": self._max_age_days_for_source(s),
            }
            for s in self.sources
        ]

    @staticmethod
    def _item_priority_score(item: Dict[str, Any], source: Dict[str, Any]) -> int:
        title = str(item.get("title", "") or "")
        summary = str(item.get("summary", "") or "")
        tags = item.get("tags") if isinstance(item.get("tags"), list) else []
        merged = " ".join([title, summary, " ".join([str(x or "") for x in tags])])
        score = 0
        kind = str(item.get("kind", "") or "").strip().lower()

        if _has_model_signal(merged):
            score += 5

        event = str(item.get("event_type", "") or "")
        if event == "release":
            score += 4
        elif event in {"benchmark", "report", "safety"}:
            score += 2

        if kind == "market_finance":
            if _contains_keyword(merged, FINANCE_MARKET_KEYWORDS):
                score += 3
            if _contains_keyword(merged, AI_EQUITY_SIGNAL_KEYWORDS):
                score += 2
        elif kind == "industry_report":
            if _contains_keyword(merged, REPORT_SIGNAL_KEYWORDS):
                score += 3
        elif kind == "policy_safety":
            if _contains_keyword(merged, POLICY_SAFETY_KEYWORDS):
                score += 4
        elif kind == "oss_signal":
            if _contains_keyword(merged, OSS_DISCOVERY_KEYWORDS):
                score += 3
            if _contains_keyword(merged, ["repo:", "github-trending"]):
                score += 2
        elif kind == "github_release":
            if _looks_like_version_title(title):
                score += 3
            if _contains_keyword(merged, GITHUB_RELEASE_NOISE_KEYWORDS):
                score -= 2

        source_id = str(source.get("id", "") or "").strip().lower()
        if source_id in {"openai_news", "anthropic_news", "qwen36_updates"} and _has_model_signal(merged):
            score += 3

        return score

    def _select_items_for_source(
        self,
        items: List[Dict[str, Any]],
        source: Dict[str, Any],
        max_items: int,
    ) -> List[Dict[str, Any]]:
        if not items:
            return []
        safe_max = max(1, int(max_items or 1))
        ranked = sorted(
            items,
            key=lambda row: (
                self._item_priority_score(row, source),
                str(row.get("published_at", "") or ""),
                str(row.get("fetched_at", "") or ""),
            ),
            reverse=True,
        )
        return ranked[:safe_max]

    def _fetch_text(self, url: str) -> str:
        last_error: Optional[Exception] = None
        for attempt in range(3):
            try:
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "PaperScope-AIProgress/1.0 (+https://github.com)"},
                    method="GET",
                )
                with urllib.request.urlopen(request, timeout=12) as response:
                    raw = response.read()
                return raw.decode("utf-8", errors="replace")
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(0.6 * (attempt + 1))
                    continue
        if last_error is not None:
            raise last_error
        return ""

    @staticmethod
    def _extract_github_repo_from_url(url: str) -> str:
        text = str(url or "").strip()
        if not text:
            return ""
        matched = re.search(r"github\.com/([^/\s]+)/([^/\s#?]+)", text, re.IGNORECASE)
        if not matched:
            return ""
        owner = str(matched.group(1) or "").strip()
        repo = str(matched.group(2) or "").strip()
        repo = re.sub(r"\.git$", "", repo, flags=re.IGNORECASE)
        if not owner or not repo:
            return ""
        return f"{owner}/{repo}"

    def _resolve_github_repo(self, source: Dict[str, Any], item_url: str) -> str:
        for candidate in (
            str(item_url or "").strip(),
            str(source.get("homepage", "") or "").strip(),
            str(source.get("feed_url", "") or "").strip(),
        ):
            repo = self._extract_github_repo_from_url(candidate)
            if repo:
                return repo
        return ""

    def _fetch_github_repo_readme(self, repo: str) -> str:
        repo_text = str(repo or "").strip()
        if not repo_text:
            return ""

        # First try GitHub API raw README endpoint.
        api_url = f"https://api.github.com/repos/{repo_text}/readme"
        try:
            request = urllib.request.Request(
                api_url,
                headers={
                    "User-Agent": "PaperScope-AIProgress/1.0 (+https://github.com)",
                    "Accept": "application/vnd.github.raw+json",
                },
                method="GET",
            )
            with urllib.request.urlopen(request, timeout=8) as response:
                raw = response.read()
            text = raw.decode("utf-8", errors="replace")
            if text:
                return text
        except Exception:
            pass

        # Fallback to common raw paths.
        for branch in ("main", "master"):
            for filename in ("README.md", "README.rst", "README.txt"):
                raw_url = f"https://raw.githubusercontent.com/{repo_text}/{branch}/{filename}"
                try:
                    request = urllib.request.Request(
                        raw_url,
                        headers={"User-Agent": "PaperScope-AIProgress/1.0 (+https://github.com)"},
                        method="GET",
                    )
                    with urllib.request.urlopen(request, timeout=8) as response:
                        raw = response.read()
                    text = raw.decode("utf-8", errors="replace")
                    if text:
                        return text
                except Exception:
                    continue
        return ""

    def _is_github_repo_ai(
        self,
        repo: str,
        fallback_text: str = "",
        min_score: int = GITHUB_README_MIN_SCORE,
        require_readme: bool = False,
    ) -> bool:
        key = str(repo or "").strip().lower()
        if not key:
            return False
        try:
            min_score_int = max(1, int(min_score))
        except Exception:
            min_score_int = GITHUB_README_MIN_SCORE
        cache_key = f"{key}|{min_score_int}|{1 if require_readme else 0}"
        cached = self._github_readme_cache.get(cache_key)
        if isinstance(cached, bool):
            return cached

        readme = self._fetch_github_repo_readme(repo)
        if readme:
            score = _github_readme_ai_score(readme)
            verdict = score >= min_score_int
        else:
            if require_readme:
                verdict = False
            else:
                fallback = f"{repo} {fallback_text}".lower()
                verdict = any(
                    k in fallback
                    for k in ("ai", "ml", "llm", "model", "transformer", "pytorch", "vllm", "ollama")
                )

        self._github_readme_cache[cache_key] = bool(verdict)
        return bool(verdict)

    @staticmethod
    def _parse_sitemap_entries(root: ET.Element, ns: Dict[str, str]) -> List[Tuple[str, str]]:
        entries: List[Tuple[str, str]] = []
        for url_node in root.findall(".//sm:url", ns):
            loc_node = url_node.find("sm:loc", ns)
            if loc_node is None:
                continue
            url = str(loc_node.text or "").strip()
            if not url:
                continue
            lastmod_node = url_node.find("sm:lastmod", ns)
            lastmod = str(lastmod_node.text or "").strip() if lastmod_node is not None else ""
            entries.append((url, lastmod))
        return entries

    def _fetch_sitemap_urls(self, sitemap_url: str) -> List[Tuple[str, str]]:
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        xml_text = self._fetch_text(sitemap_url)
        root = ET.fromstring(xml_text)
        if _local_name(root.tag) == "sitemapindex":
            entries: List[Tuple[str, str]] = []
            for loc in root.findall(".//sm:loc", ns):
                nested = str(loc.text or "").strip()
                if not nested:
                    continue
                try:
                    nested_xml = self._fetch_text(nested)
                    nested_root = ET.fromstring(nested_xml)
                except Exception:
                    continue
                entries.extend(self._parse_sitemap_entries(nested_root, ns))
            return entries
        return self._parse_sitemap_entries(root, ns)

    def _extract_page_metadata(self, url: str) -> Tuple[str, str]:
        text = self._fetch_text(url)
        title_patterns = [
            r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']',
            r'<title[^>]*>(.*?)</title>',
        ]
        desc_patterns = [
            r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
            r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\'](.*?)["\']',
        ]
        title = ""
        summary = ""
        for pattern in title_patterns:
            matched = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if matched:
                title = _normalize_text(_html_attr_unescape(matched.group(1)))
                if title:
                    break
        for pattern in desc_patterns:
            matched = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if matched:
                summary = _normalize_text(_html_attr_unescape(matched.group(1)))
                if summary:
                    break
        return title, summary

    def _parse_sitemap_feed(self, source: Dict[str, Any], max_items: int) -> List[Dict[str, Any]]:
        sitemap_url = str(source.get("sitemap_url", "") or "").strip()
        if not sitemap_url:
            return []
        path_prefixes = [str(x).strip() for x in source.get("path_prefixes", []) if str(x).strip()]
        entries = self._fetch_sitemap_urls(sitemap_url)
        filtered_urls: List[Tuple[str, str]] = []
        for url, lastmod in entries:
            if not url:
                continue
            if path_prefixes and not any(prefix in url for prefix in path_prefixes):
                continue
            filtered_urls.append((url, lastmod))
        rows: List[Dict[str, Any]] = []
        scan_limit = max(max_items * 12, 120)
        for url, lastmod in filtered_urls[:scan_limit]:
            try:
                title, summary = self._extract_page_metadata(url)
            except Exception:
                continue
            if not title:
                continue
            published_at = _parse_dt_iso(lastmod) or _infer_date_from_url(url)
            rows.append(
                self._normalize_item(
                    {
                        "source_id": source.get("id", ""),
                        "source_name": source.get("name", ""),
                        "org": source.get("org", ""),
                        "region": source.get("region", "global"),
                        "kind": source.get("kind", "official_site"),
                        "event_type": _infer_event_type(title, summary, str(source.get("kind", ""))),
                        "title": title,
                        "summary": summary,
                        "url": url,
                        "published_at": published_at,
                        "tags": [],
                        "fetched_at": _utc_now_iso(),
                    }
                )
            )
        return self._select_items_for_source(rows, source, max_items)

    def _parse_github_trending_feed(self, source: Dict[str, Any], max_items: int) -> List[Dict[str, Any]]:
        feed_url = str(source.get("feed_url", "") or "").strip()
        if not feed_url:
            return []
        html_text = self._fetch_text(feed_url)
        blocks = re.findall(
            r"<article[^>]*class=[\"'][^\"']*Box-row[^\"']*[\"'][^>]*>(.*?)</article>",
            html_text,
            re.IGNORECASE | re.DOTALL,
        )
        if not blocks:
            return []

        rows: List[Dict[str, Any]] = []
        try:
            configured_scan_limit = int(source.get("scan_limit", 120) or 120)
        except Exception:
            configured_scan_limit = 120
        scan_limit = max(max_items * 8, configured_scan_limit)
        fetched_at = _utc_now_iso()

        for block in blocks[:scan_limit]:
            repo_match = re.search(
                r"<h2[^>]*>.*?<a[^>]*href=[\"']/([^\"'/\s]+)/([^\"'/\s#?]+)[\"']",
                block,
                re.IGNORECASE | re.DOTALL,
            )
            if not repo_match:
                continue
            owner = str(repo_match.group(1) or "").strip()
            repo_name = str(repo_match.group(2) or "").strip()
            if not owner or not repo_name:
                continue
            repo_full = f"{owner}/{repo_name}"
            repo_url = f"https://github.com/{repo_full}"

            desc_match = re.search(r"<p[^>]*>(.*?)</p>", block, re.IGNORECASE | re.DOTALL)
            summary = _normalize_text(desc_match.group(1) if desc_match else "")
            title = repo_full

            tags: List[str] = ["github-trending", f"repo:{repo_full}"]
            lang_match = re.search(
                r'itemprop=["\']programmingLanguage["\'][^>]*>\s*([^<]+)\s*<',
                block,
                re.IGNORECASE | re.DOTALL,
            )
            if lang_match:
                language = _normalize_text(lang_match.group(1))
                if language:
                    tags.append(f"lang:{language}")
            stars_today_match = re.search(r"([0-9][0-9,]*)\s+stars?\s+today", _normalize_text(block), re.IGNORECASE)
            if stars_today_match:
                stars_today = stars_today_match.group(1).replace(",", "")
                if stars_today:
                    tags.append(f"stars_today:{stars_today}")

            normalized = self._normalize_item(
                {
                    "source_id": source.get("id", ""),
                    "source_name": source.get("name", ""),
                    "org": source.get("org", ""),
                    "region": source.get("region", "global"),
                    "kind": source.get("kind", "oss_signal"),
                    "event_type": _infer_event_type(title, summary, str(source.get("kind", ""))),
                    "title": title,
                    "summary": summary,
                    "url": repo_url,
                    "published_at": fetched_at,
                    "tags": tags,
                    "fetched_at": fetched_at,
                }
            )

            kind_text = str(normalized.get("kind", "") or "").strip().lower()
            if _is_low_quality_entry(normalized.get("title", ""), normalized.get("summary", ""), kind_text):
                continue
            if not _passes_source_filters(normalized, source):
                continue

            if bool(source.get("readme_gate")) and not self._is_github_repo_ai(
                repo_full,
                fallback_text=" ".join(
                    [
                        str(source.get("name", "") or ""),
                        str(source.get("org", "") or ""),
                        title,
                        summary,
                    ]
                ),
                min_score=int(source.get("readme_min_score", GITHUB_README_MIN_SCORE) or GITHUB_README_MIN_SCORE),
                require_readme=bool(source.get("require_readme")),
            ):
                continue

            if not _is_ai_relevant(
                normalized["title"],
                normalized.get("summary", ""),
                normalized.get("tags", []),
                kind_text,
                source,
            ):
                continue
            rows.append(normalized)

        return self._select_items_for_source(rows, source, max_items)

    def _parse_feed(self, xml_text: str, source: Dict[str, Any], max_items: int) -> List[Dict[str, Any]]:
        if not xml_text:
            return []
        try:
            root = ET.fromstring(xml_text)
        except Exception:
            return []

        tag = _local_name(root.tag)
        out: List[Dict[str, Any]] = []

        def append_item(item: Dict[str, Any]) -> None:
            normalized = self._normalize_item(item)
            if not normalized.get("title") or not normalized.get("url"):
                return
            kind_text = str(normalized.get("kind", "") or "").strip().lower()
            if _is_low_quality_entry(
                normalized.get("title", ""),
                normalized.get("summary", ""),
                kind_text,
            ):
                return

            if not _passes_source_filters(normalized, source):
                return

            if not _is_ai_relevant(
                normalized["title"],
                normalized.get("summary", ""),
                normalized.get("tags", []),
                kind_text,
                source,
            ):
                return
            if kind_text in {"github_release", "oss_signal"} and bool(source.get("readme_gate")):
                repo = self._resolve_github_repo(source, str(normalized.get("url", "") or ""))
                if repo:
                    fallback_text = " ".join(
                        [
                            str(source.get("name", "") or ""),
                            str(source.get("org", "") or ""),
                            str(normalized.get("title", "") or ""),
                            str(normalized.get("summary", "") or ""),
                        ]
                    )
                    if not self._is_github_repo_ai(
                        repo,
                        fallback_text=fallback_text,
                        min_score=int(source.get("readme_min_score", GITHUB_README_MIN_SCORE) or GITHUB_README_MIN_SCORE),
                        require_readme=bool(source.get("require_readme")),
                    ):
                        return
                    tags = normalized.get("tags") if isinstance(normalized.get("tags"), list) else []
                    repo_tag = f"repo:{repo}"
                    if repo_tag not in tags:
                        tags = list(tags) + [repo_tag]
                    normalized["tags"] = tags
            out.append(normalized)

        scan_limit = max(max_items * 20, 160)

        if tag in {"rss", "rdf"}:
            channel = None
            for child in list(root):
                if _local_name(child.tag) == "channel":
                    channel = child
                    break
            if channel is None:
                channel = root
            scanned = 0
            for entry in list(channel):
                if _local_name(entry.tag) != "item":
                    continue
                scanned += 1
                if scanned > scan_limit:
                    break
                title = _first_child_text(entry, ["title"])
                link = _absolutize_url(_first_child_text(entry, ["link"]), source)
                summary = _first_child_text(entry, ["description", "summary", "content"])
                published = _first_child_text(entry, ["pubdate", "published", "updated", "date"])
                tags = _all_child_texts(entry, ["category", "tag"])
                append_item(
                    {
                        "source_id": source.get("id", ""),
                        "source_name": source.get("name", ""),
                        "org": source.get("org", ""),
                        "region": source.get("region", "global"),
                        "kind": source.get("kind", "official_blog"),
                        "event_type": _infer_event_type(title, summary, str(source.get("kind", ""))),
                        "title": title,
                        "summary": summary,
                        "url": link,
                        "published_at": published,
                        "tags": tags,
                        "fetched_at": _utc_now_iso(),
                    }
                )
            return self._select_items_for_source(out, source, max_items)

        if tag == "feed":
            scanned = 0
            for entry in list(root):
                if _local_name(entry.tag) != "entry":
                    continue
                scanned += 1
                if scanned > scan_limit:
                    break
                title = _first_child_text(entry, ["title"])
                link = _absolutize_url(_entry_link(entry), source)
                summary = _first_child_text(entry, ["summary", "content"])
                published = _first_child_text(entry, ["published", "updated", "date"])
                tags = _all_child_texts(entry, ["category", "tag"])
                append_item(
                    {
                        "source_id": source.get("id", ""),
                        "source_name": source.get("name", ""),
                        "org": source.get("org", ""),
                        "region": source.get("region", "global"),
                        "kind": source.get("kind", "official_blog"),
                        "event_type": _infer_event_type(title, summary, str(source.get("kind", ""))),
                        "title": title,
                        "summary": summary,
                        "url": link,
                        "published_at": published,
                        "tags": tags,
                        "fetched_at": _utc_now_iso(),
                    }
                )
            return self._select_items_for_source(out, source, max_items)

        return []

    def fetch(
        self,
        max_per_source: int = 20,
        source_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        per_source = max(1, min(int(max_per_source or 20), 120))
        target_ids = {str(x).strip() for x in (source_ids or []) if str(x).strip()}
        targets = [
            s for s in self.sources if not target_ids or str(s.get("id", "")) in target_ids
        ]

        scanned = 0
        recency_filtered = 0
        history_skipped = 0
        added = 0
        updated = 0
        added_keys: List[str] = []
        updated_keys: List[str] = []
        failed: List[Dict[str, str]] = []
        source_counts: Dict[str, int] = {}
        fetched_rows: List[Dict[str, Any]] = []

        def fetch_one(source: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]], Optional[str]]:
            source_id = str(source.get("id", "") or "")
            feed_type = str(source.get("feed_type", "") or "").strip().lower()
            feed_url = str(source.get("feed_url", "") or "").strip()
            if not source_id:
                return source_id, [], "missing source_id"
            try:
                if feed_type == "sitemap":
                    rows = self._parse_sitemap_feed(source, per_source)
                    return source_id, rows, None
                if feed_type == "github_trending":
                    rows = self._parse_github_trending_feed(source, per_source)
                    return source_id, rows, None
                if not feed_url:
                    return source_id, [], "missing feed_url"
                xml_text = self._fetch_text(feed_url)
                rows = self._parse_feed(xml_text, source, per_source)
                return source_id, rows, None
            except Exception as exc:
                return source_id, [], f"{type(exc).__name__}: {exc}"

        worker_count = min(6, max(2, len(targets)))
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = [executor.submit(fetch_one, source) for source in targets]
            for future in as_completed(futures):
                source_id, rows, error = future.result()
                if error:
                    failed.append({"source_id": source_id, "error": error})
                    continue
                source_counts[source_id] = len(rows)
                scanned += len(rows)
                fetched_rows.extend(rows)

        with self._lock:
            loaded = self.load()
            existing_items = loaded.get("items") if isinstance(loaded, dict) else []
            if not isinstance(existing_items, list):
                existing_items = []
            seen_index = self._load_seen_index()
            by_key: Dict[str, Dict[str, Any]] = {}
            for item in existing_items:
                if not isinstance(item, dict):
                    continue
                normalized = self._normalize_item(item)
                by_key[normalized["progress_key"]] = normalized

            for row in fetched_rows:
                source_meta = self.source_by_id.get(str(row.get("source_id", "") or "").strip(), {})
                if not self._is_recent_item(row, source_meta):
                    recency_filtered += 1
                    continue

                key = row["progress_key"]
                signature = self._history_signature(row)
                existing = by_key.get(key)
                if not existing and signature in seen_index:
                    history_skipped += 1
                    self._touch_seen_index(
                        seen_index,
                        signature,
                        str(seen_index.get(signature, {}).get("progress_key", "") or ""),
                    )
                    continue

                if existing is None:
                    by_key[key] = row
                    added += 1
                    added_keys.append(key)
                    self._touch_seen_index(seen_index, signature, key)
                else:
                    old_time = str(existing.get("published_at", "") or "")
                    new_time = str(row.get("published_at", "") or "")
                    if new_time >= old_time:
                        by_key[key] = self._merge_existing_item(existing, row)
                        updated += 1
                        updated_keys.append(key)
                        self._touch_seen_index(seen_index, signature, key)

            merged = {"items": list(by_key.values()), "updated_at": _utc_now_iso()}
            saved = self.save(merged)
            self._save_seen_index(self._prune_seen_index(seen_index))

        items = saved.get("items", []) if isinstance(saved, dict) else []
        return {
            "ok": True,
            "max_per_source": per_source,
            "source_count": len(targets),
            "source_item_counts": source_counts,
            "scanned": scanned,
            "recency_filtered": recency_filtered,
            "history_skipped": history_skipped,
            "added": added,
            "updated": updated,
            "added_keys": added_keys,
            "updated_keys": updated_keys,
            "failed": failed,
            "total": len(items) if isinstance(items, list) else 0,
            "updated_at": saved.get("updated_at", ""),
        }

    def list_items(
        self,
        limit: int = 120,
        q: str = "",
        source_id: str = "",
        region: str = "",
        kind: str = "",
        event_type: str = "",
        date_from: str = "",
        date_to: str = "",
        sort_by: str = "time",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        safe_limit = max(1, min(int(limit or 120), 500))
        q_text = _normalize_text(q).lower()
        source_id = str(source_id or "").strip()
        region = str(region or "").strip().lower()
        kind_text = str(kind or "").strip().lower()
        kind_set = {x.strip() for x in kind_text.split(",") if x.strip()} if kind_text else set()
        event_type = str(event_type or "").strip().lower()
        date_from = str(date_from or "").strip()
        date_to = str(date_to or "").strip()
        sort_by = str(sort_by or "time").strip().lower()
        sort_order = str(sort_order or "desc").strip().lower()
        if sort_by not in {"time", "source", "title"}:
            sort_by = "time"
        if sort_order not in {"asc", "desc"}:
            sort_order = "desc"

        loaded = self.load()
        items = loaded.get("items") if isinstance(loaded, dict) else []
        if not isinstance(items, list):
            items = []

        filtered: List[Dict[str, Any]] = []
        for raw in items:
            if not isinstance(raw, dict):
                continue
            item = self._normalize_item(raw)
            source_meta = self.source_by_id.get(str(item.get("source_id", "") or "").strip(), {})
            if not self._is_recent_item(item, source_meta):
                continue
            if source_id and str(item.get("source_id", "")) != source_id:
                continue
            if region and str(item.get("region", "")).lower() != region:
                continue
            if kind_set and str(item.get("kind", "")).lower() not in kind_set:
                continue
            if event_type and str(item.get("event_type", "")).lower() != event_type:
                continue
            published = str(item.get("published_at", "") or "")
            if date_from and published and published[:10] < date_from:
                continue
            if date_to and published and published[:10] > date_to:
                continue
            if q_text:
                merged = " ".join(
                    [
                        str(item.get("title", "")),
                        str(item.get("title_zh", "")),
                        str(item.get("summary", "")),
                        str(item.get("summary_zh", "")),
                        str(item.get("llm_takeaway_zh", "")),
                        str(item.get("org", "")),
                        " ".join(item.get("tags") or []),
                    ]
                ).lower()
                if q_text not in merged:
                    continue
            filtered.append(item)

        if sort_by == "source":
            filtered.sort(
                key=lambda x: (
                    str(x.get("org", "")),
                    str(x.get("published_at", "")),
                    str(x.get("title", "")),
                ),
                reverse=(sort_order == "desc"),
            )
        elif sort_by == "title":
            filtered.sort(
                key=lambda x: (str(x.get("title", "")), str(x.get("published_at", ""))),
                reverse=(sort_order == "desc"),
            )
        else:
            filtered.sort(
                key=lambda x: (str(x.get("published_at", "")), str(x.get("fetched_at", ""))),
                reverse=(sort_order == "desc"),
            )

        output = filtered[:safe_limit]
        region_stats: Dict[str, int] = {}
        for item in filtered:
            reg = str(item.get("region", "") or "global").strip().lower() or "global"
            region_stats[reg] = int(region_stats.get(reg, 0)) + 1

        return {
            "items": output,
            "count": len(output),
            "total_filtered": len(filtered),
            "limit": safe_limit,
            "updated_at": loaded.get("updated_at", ""),
            "stats": {
                "region": region_stats,
                "source_count": len({str(x.get("source_id", "")) for x in filtered if str(x.get("source_id", ""))}),
            },
        }

    def apply_translations(
        self,
        translations: Dict[str, Dict[str, str]],
    ) -> Dict[str, Any]:
        with self._lock:
            loaded = self.load()
            items = loaded.get("items") if isinstance(loaded, dict) else []
            if not isinstance(items, list):
                items = []
            changed = 0
            translated_keys: List[str] = []
            for idx, raw in enumerate(items):
                if not isinstance(raw, dict):
                    continue
                item = self._normalize_item(raw)
                key = str(item.get("progress_key", "") or "")
                patch = translations.get(key) if isinstance(translations, dict) else None
                if not key or not isinstance(patch, dict):
                    continue
                lang_key = _normalize_lang_key(
                    patch.get("output_language")
                    or patch.get("target_language")
                    or patch.get("language")
                    or patch.get("lang")
                    or ""
                )
                title_zh = _normalize_text(patch.get("title_zh", ""))
                summary_zh = _normalize_text(patch.get("summary_zh", ""))
                llm_takeaway_zh = _normalize_text(patch.get("llm_takeaway_zh", ""))
                title_any = _normalize_text(patch.get("title", ""))
                summary_any = _normalize_text(patch.get("summary", ""))
                llm_takeaway_any = _normalize_text(patch.get("llm_takeaway", ""))
                updated = False

                i18n_raw = item.get("i18n") if isinstance(item.get("i18n"), dict) else {}
                i18n_map = {str(k): dict(v) for k, v in i18n_raw.items() if isinstance(v, dict)}

                if title_zh and title_zh != str(item.get("title_zh", "")):
                    item["title_zh"] = title_zh
                    updated = True
                if summary_zh and summary_zh != str(item.get("summary_zh", "")):
                    item["summary_zh"] = summary_zh
                    updated = True
                if llm_takeaway_zh and llm_takeaway_zh != str(item.get("llm_takeaway_zh", "")):
                    item["llm_takeaway_zh"] = llm_takeaway_zh
                    updated = True

                if lang_key:
                    lang_entry = i18n_map.get(lang_key) if isinstance(i18n_map.get(lang_key), dict) else {}
                    normalized_entry = {
                        "title": title_any or title_zh or str(lang_entry.get("title", "") or ""),
                        "summary": summary_any or summary_zh or str(lang_entry.get("summary", "") or ""),
                        "llm_takeaway": (
                            llm_takeaway_any
                            or llm_takeaway_zh
                            or str(lang_entry.get("llm_takeaway", "") or "")
                        ),
                    }
                    if normalized_entry != lang_entry and any(normalized_entry.values()):
                        i18n_map[lang_key] = normalized_entry
                        item["i18n"] = i18n_map
                        updated = True

                if updated:
                    items[idx] = item
                    changed += 1
                    translated_keys.append(key)
            saved = self.save({"items": items, "updated_at": _utc_now_iso()})
            return {
                "ok": True,
                "changed": changed,
                "translated_keys": translated_keys,
                "total": len(saved.get("items", [])) if isinstance(saved.get("items"), list) else 0,
            }
