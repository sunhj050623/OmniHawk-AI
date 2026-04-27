# coding=utf-8
"""
Paper analyzer for RSS arXiv items.
"""

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

from openhawk_ai.ai.client import AIClient
from openhawk_ai.ai.prompt_loader import load_prompt_template
from openhawk_ai.storage.base import RSSData, RSSItem


class PaperAnalyzer:
    """Use LLM to generate structured insight for arXiv RSS items."""

    def __init__(self, ai_config: Dict[str, Any], paper_config: Dict[str, Any]):
        self.ai_config = ai_config or {}
        self.paper_config = paper_config or {}

        self.enabled = bool(self.paper_config.get("ENABLED", False))
        self.analyze_all_new = bool(self.paper_config.get("ANALYZE_ALL_NEW", True))
        self.max_papers_per_run = int(self.paper_config.get("MAX_PAPERS_PER_RUN", 8) or 8)
        self.max_abstract_chars = int(self.paper_config.get("MAX_ABSTRACT_CHARS", 3000) or 3000)
        self.timeout = int(self.paper_config.get("TIMEOUT", self.ai_config.get("TIMEOUT", 120)) or 120)
        self.max_tokens = int(self.paper_config.get("MAX_TOKENS", 1200) or 1200)
        self.language = self.paper_config.get("LANGUAGE", "Chinese") or "Chinese"
        self.research_topic = str(self.paper_config.get("RESEARCH_TOPIC", "") or "").strip()
        self.primary_category = str(self.paper_config.get("PRIMARY_CATEGORY", "") or "").strip()
        self.subtopics = str(self.paper_config.get("SUBTOPICS", "") or "").strip()
        self.subtopic_keywords = self._split_keywords(self.subtopics)
        self.research_keywords = self._split_keywords(self.research_topic)

        self.client = AIClient(self.ai_config)
        prompt_file = self.paper_config.get("PROMPT_FILE", "paper_analysis_prompt.txt")
        self.system_prompt, self.user_prompt_template = load_prompt_template(prompt_file, label="Paper")

    def enrich_rss_data(self, rss_data: RSSData) -> int:
        """Analyze arXiv items and fill item.paper_insight."""
        if not self.enabled:
            return 0

        if not self.client.api_key:
            print("[Paper] AI API key is missing, skip paper analysis")
            return 0

        grouped_items: Dict[str, List[RSSItem]] = {}
        cached_by_signature: Dict[str, Dict[str, Any]] = {}
        for rss_list in rss_data.items.values():
            for item in rss_list:
                if not self._is_arxiv_item(item):
                    continue
                signature = self._paper_signature(item)
                grouped_items.setdefault(signature, []).append(item)
                if self._has_cached_insight(item):
                    cached_by_signature.setdefault(signature, dict(item.paper_insight))

        if not grouped_items:
            print("[Paper] no arXiv items to analyze")
            return 0

        in_batch_reused = 0
        dedup_skipped = 0
        scored_candidates: List[Tuple[int, float, RSSItem, List[RSSItem]]] = []
        for signature, grouped in grouped_items.items():
            inherited = cached_by_signature.get(signature)
            pending: List[RSSItem] = []
            if inherited:
                for item in grouped:
                    if self._has_cached_insight(item):
                        continue
                    item.paper_insight = dict(inherited)
                    in_batch_reused += 1
                continue

            for item in grouped:
                if self._has_cached_insight(item):
                    continue
                pending.append(item)

            if not pending:
                continue

            scored_group: List[Tuple[int, float, RSSItem]] = []
            for item in pending:
                pre_score = self._estimate_pre_score(item)
                published_ts = self._to_timestamp(item.published_at)
                scored_group.append((pre_score, published_ts, item))
            scored_group.sort(
                key=lambda x: (x[0], x[1], str(x[2].title or "")),
                reverse=True,
            )
            representative_score, representative_ts, representative = scored_group[0]
            duplicates = [row[2] for row in scored_group[1:]]
            dedup_skipped += len(duplicates)
            scored_candidates.append(
                (representative_score, representative_ts, representative, duplicates)
            )

        if in_batch_reused > 0:
            print(f"[Paper] reused {in_batch_reused} duplicate items from in-batch cached insight")

        if not scored_candidates:
            print("[Paper] no arXiv items to analyze")
            return 0

        scored_candidates.sort(
            key=lambda x: (x[0], x[1], str(x[2].title or "")),
            reverse=True,
        )

        if self.analyze_all_new:
            limited_candidates = scored_candidates
        else:
            limited_candidates = scored_candidates[: self.max_papers_per_run]
        if (not self.analyze_all_new) and len(scored_candidates) > len(limited_candidates):
            top_score = limited_candidates[0][0] if limited_candidates else 0
            bottom_score = limited_candidates[-1][0] if limited_candidates else 0
            print(
                f"[Paper] limit reached, analyze {len(limited_candidates)}/{len(scored_candidates)} items "
                f"(pre_score range: {top_score}-{bottom_score})"
            )

        if dedup_skipped > 0:
            print(f"[Paper] deduplicated {dedup_skipped} duplicate arXiv items before LLM analysis")

        success_count = 0
        duplicated_assigned = 0
        analysis_run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        for pre_score, _, item, duplicates in limited_candidates:
            insight = self._analyze_item(
                item,
                pre_score=pre_score,
                analysis_run_id=analysis_run_id,
            )
            if not insight:
                continue
            item.paper_insight = insight
            for duplicate in duplicates:
                duplicate.paper_insight = dict(insight)
                duplicated_assigned += 1
            success_count += 1

        if duplicated_assigned > 0:
            print(f"[Paper] copied analyzed insight to {duplicated_assigned} duplicate items")
        print(f"[Paper] analyzed {success_count} arXiv papers")
        return success_count

    def _is_arxiv_item(self, item: RSSItem) -> bool:
        meta = item.paper_meta or {}
        if str(meta.get("source", "")).lower() == "arxiv":
            return True
        return "arxiv.org" in (item.url or "").lower()

    def _has_cached_insight(self, item: RSSItem) -> bool:
        insight = item.paper_insight if isinstance(item.paper_insight, dict) else {}
        if not insight:
            return False
        for key in (
            "summary",
            "one_sentence_summary",
            "method",
            "conclusion",
            "innovation",
            "findings",
            "novelty",
        ):
            if str(insight.get(key, "") or "").strip():
                return True
        return False

    def _extract_arxiv_id(self, item: RSSItem) -> str:
        meta = item.paper_meta if isinstance(item.paper_meta, dict) else {}
        arxiv_id = str(meta.get("arxiv_id", "") or "").strip().lower()
        if arxiv_id:
            return arxiv_id
        text = str(item.url or "").strip().lower()
        if not text:
            return ""
        matched = re.search(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5})(?:v\d+)?", text)
        if matched:
            return str(matched.group(1) or "").strip().lower()
        return ""

    def _canonical_url(self, url: str) -> str:
        text = str(url or "").strip()
        if not text:
            return ""
        try:
            parsed = urlparse(text)
            netloc = str(parsed.netloc or "").lower()
            path = str(parsed.path or "").rstrip("/")
            normalized = parsed._replace(scheme=str(parsed.scheme or "").lower(), netloc=netloc, path=path, params="", query="", fragment="")
            return urlunparse(normalized)
        except Exception:
            return text.lower().rstrip("/")

    def _paper_signature(self, item: RSSItem) -> str:
        arxiv_id = self._extract_arxiv_id(item)
        if arxiv_id:
            return f"arxiv:{arxiv_id}"

        canonical_url = self._canonical_url(item.url or "")
        if canonical_url:
            return f"url:{canonical_url}"

        title = str(item.title or "").strip().lower()
        published = str(item.published_at or "").strip().lower()
        if title:
            return f"title:{title}|published:{published}"
        return f"fallback:{str(item.feed_id or '').strip().lower()}|{published}"

    def _split_keywords(self, text: str) -> List[str]:
        raw = [v.strip().lower() for v in re.split(r"[,;/|]", str(text or "")) if v.strip()]
        seen = set()
        out: List[str] = []
        for token in raw:
            if token in seen:
                continue
            seen.add(token)
            out.append(token)
        return out

    def _to_datetime(self, value: str) -> Optional[datetime]:
        text = str(value or "").strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except Exception:
            pass
        try:
            return datetime.strptime(text[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            return None

    def _to_timestamp(self, value: str) -> float:
        dt = self._to_datetime(value)
        if not dt:
            return 0.0
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()

    def _estimate_pre_score(self, item: RSSItem) -> int:
        meta = item.paper_meta or {}
        title = str(item.title or "").lower()
        abstract = str(meta.get("abstract") or item.summary or "").lower()
        primary = str(meta.get("primary_category") or "").strip()
        categories = meta.get("categories") or []
        if isinstance(categories, list):
            tags = [str(v).strip() for v in categories if str(v).strip()]
        elif isinstance(categories, str):
            tags = [v.strip() for v in categories.split(",") if v.strip()]
        else:
            tags = []

        score = 30
        if self.primary_category:
            if self.primary_category == primary or self.primary_category in tags:
                score += 20
            elif primary and self.primary_category.split(".")[0] == primary.split(".")[0]:
                score += 8
            else:
                score -= 6

        haystack = f"{title}\n{abstract}\n{' '.join(tags).lower()}"
        topic_terms = self.subtopic_keywords or self.research_keywords
        if topic_terms:
            topic_hits = sum(1 for topic in topic_terms if topic and topic in haystack)
            score += min(30, topic_hits * 7)

        title_signals = [
            "agent",
            "llm",
            "reason",
            "reasoning",
            "alignment",
            "multi-agent",
            "retrieval",
            "rag",
            "benchmark",
            "evaluation",
            "survey",
            "sota",
            "efficient",
            "multimodal",
        ]
        signal_hits = sum(1 for k in title_signals if k in title)
        score += min(15, signal_hits * 3)

        published_at = self._to_datetime(item.published_at or "")
        if published_at:
            now = datetime.now(timezone.utc)
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            age_days = max(0, int((now - published_at).total_seconds() // 86400))
            if age_days <= 2:
                score += 18
            elif age_days <= 7:
                score += 14
            elif age_days <= 14:
                score += 10
            elif age_days <= 30:
                score += 6
            else:
                score += 2

        if str(meta.get("doi", "") or "").strip():
            score += 2
        return max(0, min(100, int(score)))

    def _analyze_item(
        self,
        item: RSSItem,
        pre_score: int,
        analysis_run_id: str,
    ) -> Optional[Dict[str, Any]]:
        meta = item.paper_meta or {}
        abstract = (meta.get("abstract") or item.summary or "").strip()
        if self.max_abstract_chars > 0 and len(abstract) > self.max_abstract_chars:
            abstract = abstract[: self.max_abstract_chars]

        prompt = self._build_user_prompt(item, meta, abstract)
        messages: List[Dict[str, str]] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat(
                messages,
                timeout=self.timeout,
                max_tokens=self.max_tokens,
            )
        except Exception as exc:
            print(f"[Paper] analyze failed for '{item.title[:60]}': {type(exc).__name__}: {exc}")
            return None

        return self._parse_response(
            response,
            pre_score=pre_score,
            analysis_run_id=analysis_run_id,
        )

    def _build_user_prompt(self, item: RSSItem, meta: Dict[str, Any], abstract: str) -> str:
        template = self.user_prompt_template or (
            "Analyze this paper and return JSON with keys: summary, keywords, method, findings, novelty, limitations, use_cases, confidence.\n"
            "Title: {title}\n"
            "arXiv ID: {arxiv_id}\n"
            "Categories: {categories}\n"
            "Authors: {authors}\n"
            "Abstract: {abstract}\n"
            "Output language: {language}\n"
        )

        categories = meta.get("categories") or []
        if isinstance(categories, list):
            categories_text = ", ".join(str(v) for v in categories if v)
        else:
            categories_text = str(categories)

        authors = meta.get("authors") or []
        if isinstance(authors, list):
            authors_text = ", ".join(str(v) for v in authors if v)
        else:
            authors_text = str(authors)

        prompt = template
        prompt = prompt.replace("{title}", item.title or "")
        prompt = prompt.replace("{url}", item.url or "")
        prompt = prompt.replace("{arxiv_id}", str(meta.get("arxiv_id", "")))
        prompt = prompt.replace("{categories}", categories_text)
        prompt = prompt.replace("{authors}", authors_text)
        prompt = prompt.replace("{abstract}", abstract)
        prompt = prompt.replace("{language}", self.language)
        prompt = prompt.replace("{paper_meta_json}", json.dumps(meta, ensure_ascii=False))
        prompt = prompt.replace("{research_topic}", self.research_topic)
        prompt = prompt.replace("{primary_category}", self.primary_category)
        prompt = prompt.replace("{subtopics}", self.subtopics)
        if self.research_topic:
            prompt += f"\nFocus research direction: {self.research_topic}\n"
        if self.primary_category:
            prompt += f"Preferred primary category: {self.primary_category}\n"
        if self.subtopics:
            prompt += f"Preferred subtopics: {self.subtopics}\n"
        return prompt

    def _parse_response(
        self,
        response: str,
        pre_score: int,
        analysis_run_id: str,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        json_payload = self._extract_json(response)
        if not json_payload:
            return {
                "summary": (response or "").strip()[:1200],
                "keywords": [],
                "fallback": True,
                "analyzed_at": now,
                "analysis_run_id": analysis_run_id,
                "pre_score": pre_score,
                "recommendation_score": pre_score,
            }

        try:
            data = json.loads(json_payload)
        except json.JSONDecodeError:
            return {
                "summary": (response or "").strip()[:1200],
                "keywords": [],
                "fallback": True,
                "analyzed_at": now,
                "analysis_run_id": analysis_run_id,
                "pre_score": pre_score,
                "recommendation_score": pre_score,
            }

        if not isinstance(data, dict):
            return {
                "summary": (response or "").strip()[:1200],
                "keywords": [],
                "fallback": True,
                "analyzed_at": now,
                "analysis_run_id": analysis_run_id,
                "pre_score": pre_score,
                "recommendation_score": pre_score,
            }

        keywords = data.get("keywords", [])
        if isinstance(keywords, str):
            keywords = [v.strip() for v in keywords.split(",") if v.strip()]
        elif isinstance(keywords, list):
            keywords = [str(v).strip() for v in keywords if str(v).strip()]
        else:
            keywords = []

        summary_text = str(data.get("summary", "")).strip()
        one_sentence_summary = str(
            data.get("one_sentence_summary", "")
            or data.get("summary_1line", "")
        ).strip()
        if not one_sentence_summary and summary_text:
            one_sentence_summary = summary_text.split("。")[0].strip()
            if one_sentence_summary and not one_sentence_summary.endswith("。"):
                one_sentence_summary += "。"

        conclusion = str(
            data.get("conclusion", "")
            or data.get("findings", "")
            or data.get("main_findings", "")
        ).strip()
        innovation = str(
            data.get("innovation", "")
            or data.get("novelty", "")
        ).strip()
        method = str(data.get("method", data.get("methods", ""))).strip()

        coverage = 0
        if one_sentence_summary:
            coverage += 10
        if method:
            coverage += 8
        if conclusion:
            coverage += 8
        if innovation:
            coverage += 8
        if keywords:
            coverage += min(8, len(keywords) * 2)

        confidence_raw = str(data.get("confidence", "")).strip()
        confidence_num = 0
        matched = re.search(r"(\d{1,3})", confidence_raw)
        if matched:
            try:
                confidence_num = max(0, min(100, int(matched.group(1))))
            except Exception:
                confidence_num = 0
        confidence_bonus = int(confidence_num * 0.12)
        recommendation_score = int(round(pre_score * 0.72 + coverage + confidence_bonus))
        recommendation_score = max(0, min(100, recommendation_score))

        normalized = {
            "one_sentence_summary": one_sentence_summary,
            "summary": summary_text,
            "keywords": keywords,
            "method": method,
            "conclusion": conclusion,
            "innovation": innovation,
            # keep backward-compatible fields for existing report renderer
            "findings": conclusion,
            "novelty": innovation,
            "limitations": str(data.get("limitations", "")).strip(),
            "use_cases": str(data.get("use_cases", data.get("applications", ""))).strip(),
            "confidence": confidence_raw,
            "analyzed_at": now,
            "analysis_run_id": analysis_run_id,
            "pre_score": pre_score,
            "recommendation_score": recommendation_score,
            "analysis_basis": "标题、分类、摘要（非全文）+ LLM 结构化解析",
        }

        return {k: v for k, v in normalized.items() if v not in ("", [], None)}

    def _extract_json(self, text: str) -> str:
        if not text:
            return ""

        fenced = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
        if fenced:
            return fenced.group(1).strip()

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1].strip()

        return ""
