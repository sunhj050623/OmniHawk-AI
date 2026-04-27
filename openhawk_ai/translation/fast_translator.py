# coding=utf-8
"""
Fast non-LLM text translator.

Providers:
- google: unofficial Google endpoint, no key required
- libretranslate: LibreTranslate-compatible API
"""

from __future__ import annotations

import os
import re
import time
from typing import Any, Dict, List, Optional

import requests


_LANGUAGE_CODE_ALIASES: Dict[str, str] = {
    "english": "en",
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "chinese": "zh-CN",
    "simplified chinese": "zh-CN",
    "zh": "zh-CN",
    "zh-cn": "zh-CN",
    "zh-hans": "zh-CN",
    "简体中文": "zh-CN",
    "中文": "zh-CN",
    "traditional chinese": "zh-TW",
    "zh-tw": "zh-TW",
    "zh-hant": "zh-TW",
    "繁体中文": "zh-TW",
    "japanese": "ja",
    "ja": "ja",
    "日本语": "ja",
    "日本語": "ja",
    "korean": "ko",
    "ko": "ko",
    "韩语": "ko",
    "한국어": "ko",
    "french": "fr",
    "fr": "fr",
    "german": "de",
    "de": "de",
    "spanish": "es",
    "es": "es",
    "portuguese": "pt",
    "pt": "pt",
    "italian": "it",
    "it": "it",
    "russian": "ru",
    "ru": "ru",
    "arabic": "ar",
    "ar": "ar",
    "hindi": "hi",
    "hi": "hi",
    "turkish": "tr",
    "tr": "tr",
    "dutch": "nl",
    "nl": "nl",
    "polish": "pl",
    "pl": "pl",
    "thai": "th",
    "th": "th",
    "vietnamese": "vi",
    "vi": "vi",
    "indonesian": "id",
    "id": "id",
}

_CODE_PATTERN = re.compile(r"^[a-z]{2,3}(?:-[a-z]{2,4})?$")
_ALLOWED_PROVIDERS = {"google", "libretranslate"}


def _normalize_lang_code(target_language: str) -> str:
    raw = str(target_language or "").strip()
    if not raw:
        return ""
    key = raw.lower().replace("_", "-")
    if key in _LANGUAGE_CODE_ALIASES:
        return _LANGUAGE_CODE_ALIASES[key]
    # Keep direct BCP47-like input such as "de", "es", "pt-BR".
    if _CODE_PATTERN.match(key):
        if len(key) > 3:
            head, tail = key.split("-", 1)
            return f"{head.lower()}-{tail.upper()}"
        return key.lower()
    return ""


def _chunk_text(text: str, max_chars: int = 1200) -> List[str]:
    content = str(text or "")
    if not content:
        return []
    if len(content) <= max_chars:
        return [content]

    chunks: List[str] = []
    buffer = ""
    for line in content.splitlines(keepends=True):
        if buffer and len(buffer) + len(line) > max_chars:
            chunks.append(buffer)
            buffer = line
        else:
            buffer += line
    if buffer:
        chunks.append(buffer)
    if chunks:
        return chunks

    # fallback: hard split
    return [content[i : i + max_chars] for i in range(0, len(content), max_chars)]


class FastTranslator:
    def __init__(
        self,
        *,
        provider: str = "google",
        fallback_providers: Optional[List[str]] = None,
        timeout: int = 8,
        max_retries: int = 1,
        libre_base_url: str = "",
        libre_api_key: str = "",
    ):
        self.provider = self._normalize_provider(provider)
        self.fallback_providers = self._parse_fallback_providers(fallback_providers)
        self.timeout = max(3, min(int(timeout or 8), 30))
        self.max_retries = max(0, min(int(max_retries or 0), 5))
        self.libre_base_url = str(libre_base_url or "").strip().rstrip("/")
        self.libre_api_key = str(libre_api_key or "").strip()

    @classmethod
    def from_settings(cls, settings: Optional[Dict[str, Any]] = None, *, provider: str = "google") -> "FastTranslator":
        conf = settings if isinstance(settings, dict) else {}
        provider_value = (
            str(conf.get("fast_translator_provider") or "").strip().lower()
            or str(os.environ.get("FAST_TRANSLATOR_PROVIDER", "") or "").strip().lower()
            or str(provider or "google").strip().lower()
        )
        timeout_value = (
            conf.get("fast_translator_timeout")
            or os.environ.get("FAST_TRANSLATOR_TIMEOUT")
            or 8
        )
        retry_value = (
            conf.get("fast_translator_max_retries")
            or os.environ.get("FAST_TRANSLATOR_MAX_RETRIES")
            or 1
        )
        libre_base = (
            str(conf.get("fast_translator_libre_url") or "").strip()
            or str(os.environ.get("FAST_TRANSLATOR_LIBRE_URL", "") or "").strip()
        )
        libre_key = (
            str(conf.get("fast_translator_libre_api_key") or "").strip()
            or str(os.environ.get("FAST_TRANSLATOR_LIBRE_API_KEY", "") or "").strip()
        )
        fallback_raw = (
            str(conf.get("fast_translator_fallback_providers") or "").strip()
            or str(os.environ.get("FAST_TRANSLATOR_FALLBACK_PROVIDERS", "") or "").strip()
        )
        fallback_providers = [part.strip() for part in fallback_raw.split(",") if part.strip()]
        return cls(
            provider=provider_value or "google",
            fallback_providers=fallback_providers,
            timeout=int(timeout_value),
            max_retries=int(retry_value),
            libre_base_url=libre_base,
            libre_api_key=libre_key,
        )

    @staticmethod
    def _normalize_provider(provider: str) -> str:
        value = str(provider or "").strip().lower()
        if value in _ALLOWED_PROVIDERS:
            return value
        return "google"

    @staticmethod
    def _parse_fallback_providers(providers: Optional[List[str]]) -> List[str]:
        values = providers if isinstance(providers, list) else []
        normalized: List[str] = []
        for provider in values:
            item = str(provider or "").strip().lower()
            if item in _ALLOWED_PROVIDERS and item not in normalized:
                normalized.append(item)
        return normalized

    def translate_text(self, text: str, *, target_language: str, source_language: str = "auto") -> str:
        source = str(text or "")
        if not source.strip():
            return ""
        target_code = _normalize_lang_code(target_language)
        if not target_code:
            return source
        source_code = _normalize_lang_code(source_language)
        if not source_code:
            source_code = "auto"

        chunks = _chunk_text(source, max_chars=1200)
        translated_chunks: List[str] = []
        for chunk in chunks:
            translated_chunks.append(
                self._translate_chunk(
                    chunk,
                    target_code=target_code,
                    source_code=source_code,
                )
            )
        merged = "".join(translated_chunks).strip()
        return merged or source

    def _translate_chunk(self, chunk: str, *, target_code: str, source_code: str) -> str:
        providers = [self.provider]
        for candidate in self.fallback_providers:
            if candidate != self.provider:
                providers.append(candidate)
        if self.provider != "google" and "google" not in providers:
            providers.append("google")

        last_error: Optional[Exception] = None
        for provider in providers:
            try:
                if provider == "libretranslate":
                    return self._translate_chunk_libre(chunk, target_code=target_code, source_code=source_code)
                return self._translate_chunk_google(chunk, target_code=target_code, source_code=source_code)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                continue

        if last_error:
            raise last_error
        return chunk

    def _translate_chunk_google(self, chunk: str, *, target_code: str, source_code: str) -> str:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": source_code or "auto",
            "tl": target_code,
            "dt": "t",
            "q": chunk,
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (OpenHawk-AI FastTranslator)",
        }
        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.get(url, params=params, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                segments = data[0] if isinstance(data, list) and data else []
                out = "".join(
                    str(seg[0])
                    for seg in segments
                    if isinstance(seg, list) and seg and seg[0] is not None
                )
                if out:
                    return out
                return chunk
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(0.2 * (attempt + 1))
                    continue
        if last_error:
            raise last_error
        return chunk

    def _translate_chunk_libre(self, chunk: str, *, target_code: str, source_code: str) -> str:
        base = self.libre_base_url or "https://translate.argosopentech.com"
        url = f"{base}/translate"
        payload: Dict[str, Any] = {
            "q": chunk,
            "source": source_code or "auto",
            "target": target_code,
            "format": "text",
        }
        if self.libre_api_key:
            payload["api_key"] = self.libre_api_key
        headers = {"Content-Type": "application/json"}

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                out = str(data.get("translatedText", "") or "").strip()
                return out or chunk
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(0.2 * (attempt + 1))
                    continue
        if last_error:
            raise last_error
        return chunk
