from __future__ import annotations
import os
from typing import Any
from urllib.parse import urlparse
import httpx
from dotenv import load_dotenv

load_dotenv()
SERPER_SEARCH_URL = os.getenv("SERPER_URL")

class SerperClient:
    _SOCIAL_DOMAINS: dict[str, str] = {
        "tiktok": "tiktok.com",
        "instagram": "instagram.com",
        "facebook": "facebook.com",
        "linkedIn": "linkedin.com",
    }
    _ATS_DOMAINS: tuple[str, ...] = (
        "greenhouse.io",
        "lever.co",
        "ashbyhq.com",
        "workable.com",
    )

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise RuntimeError("KEY is not configured")

    def _headers(self) -> dict[str, str]:
        return {"X-API-KEY": self.api_key, "Content-Type": "application/json"}

    @staticmethod
    def _clean_result(item: dict[str, Any]) -> dict[str, str] | None:
        title = str(item.get("title") or "").strip()
        url = str(item.get("link") or "").strip()
        description = str(item.get("snippet") or "").strip()
        parsed_url = urlparse(url)
        if not url or parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            return None
        return {"title": title, "url": url, "description": description}

    async def search_async(self, query: str, num_results: int = 10) -> list[dict[str, str]]:
        payload = {"q": query, "num": num_results}
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(SERPER_SEARCH_URL, json=payload, headers=self._headers())
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Serper API request failed: {exc}") from exc
        results: list[dict[str, str]] = []
        for item in data.get("organic", []):
            if not isinstance(item, dict):
                continue
            cleaned = self._clean_result(item)
            if cleaned:
                results.append(cleaned)
        return results

    def search(self, query: str, num_results: int = 10) -> list[dict[str, str]]:
        payload = {"q": query, "num": num_results}
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(SERPER_SEARCH_URL, json=payload, headers=self._headers())
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Serper API request failed: {exc}") from exc
        results: list[dict[str, str]] = []
        for item in data.get("organic", []):
            if not isinstance(item, dict):
                continue
            cleaned = self._clean_result(item)
            if cleaned:
                results.append(cleaned)
        return results

    async def search_social(self, platform: str, keyword: str, num_results: int = 10) -> list[dict[str, str]]:
        normalized_platform = platform.strip().lower()
        domain = self._SOCIAL_DOMAINS.get(normalized_platform)
        if not domain:
            raise ValueError(f"Unsupported Serper social platform: {platform}")
        query = f"site:{domain} {keyword}"
        results = await self.search_async(query, num_results)
        return [
            {
                "platform": normalized_platform,
                "title": result["title"],
                "url": result["url"],
                "description": result["description"],
            }
            for result in results
        ]

    async def search_opportunities(self, keyword: str, num_results: int = 10) -> list[dict[str, str]]:
        domains = " OR ".join(f"site:{domain}" for domain in self._ATS_DOMAINS)
        query = f"{domains} {keyword} (job OR internship OR scholarship) (apply OR application OR hiring)"
        results = await self.search_async(query, num_results)
        return [
            {
                "title": result["title"],
                "url": result["url"],
                "description": result["description"],
            }
            for result in results
        ]