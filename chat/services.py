from collections.abc import Iterable
import logging
from typing import Any, Dict, List

import requests
from django.conf import settings
from django.db.models import Q
from openai import OpenAI

from .models import KnowledgeDoc


def get_client() -> OpenAI:
    """Return an OpenAI client configured from Django settings."""

    return OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_BASE)


def _collect_relevant_context(query: str | None) -> List[str]:
    """Fetch simple knowledge snippets based on keyword matching."""

    if not settings.RAG_ENABLED or not query:
        return []

    terms = [term.strip() for term in query.split() if term.strip()]
    if not terms:
        return []

    q_objects = Q()
    for term in terms:
        q_objects |= Q(text__icontains=term)

    docs = KnowledgeDoc.objects.filter(q_objects)[:3]
    return [doc.text for doc in docs]


def _search_web(query: str | None) -> List[str]:
    """Call Tavily Search to retrieve fresh web snippets for the assistant."""

    if not settings.TAVILY_ENABLED or not query:
        return []

    if not settings.TAVILY_API_KEY:
        logging.warning("TAVILY_ENABLED is True but no TAVILY_API_KEY was provided.")
        return []

    payload = {
        "query": query,
        "search_depth": settings.TAVILY_SEARCH_DEPTH,
        "max_results": settings.TAVILY_MAX_RESULTS,
        "include_answer": False,
        "include_raw_content": False,
        "topic": "general",
    }

    headers = {"Authorization": f"Bearer {settings.TAVILY_API_KEY}"}

    try:
        response = requests.post(
            "https://api.tavily.com/search", json=payload, headers=headers, timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:  # pragma: no cover - network guarded
        logging.exception("Tavily search request failed: %s", exc)
        return []

    snippets = []
    for result in data.get("results", []):
        title = result.get("title") or result.get("url") or "نتیجه وب"
        content = result.get("content") or ""
        if content:
            snippets.append(f"{title}: {content}")
        else:
            snippets.append(title)

    return snippets[: settings.TAVILY_MAX_RESULTS]


def _build_system_prompt(knowledge_snippets: List[str], web_snippets: List[str]) -> str:
    base_prompt = (
        "شما یک دستیار فارسی هستید که باید با لحن مودب و مختصر پاسخ دهید. "
        "در صورت وجود دانش زمینه‌ای از پایگاه دانش یا وب، آن را به‌صورت خلاصه در پاسخ استفاده کنید."
    )

    blocks: list[str] = []

    if knowledge_snippets:
        blocks.append(
            "اطلاعات زیر از پایگاه دانش در دسترس است:\n\n" + "\n\n".join(knowledge_snippets)
        )
    elif settings.RAG_ENABLED:
        blocks.append("منبعی در پایگاه دانش یافت نشد؛ در صورت نیاز از سایر منابع استفاده کن.")
    else:
        blocks.append("قابلیت RAG غیرفعال است، فقط از تاریخچه مکالمه استفاده کن.")

    if web_snippets:
        blocks.append(
            "نتایج جست‌وجوی وب برای پرسش کاربر:\n\n" + "\n\n".join(web_snippets)
        )
    elif settings.TAVILY_ENABLED:
        blocks.append("جست‌وجوی وب نتیجه‌ای برنگرداند یا انجام نشد.")

    return base_prompt + "\n\n" + "\n\n".join(blocks)


def stream_response(history: List[Dict[str, str]], context: str | None = None) -> Iterable[str]:
    """Stream a chat completion while optionally enriching with RAG context."""

    knowledge_snippets: List[str] = []
    web_snippets: List[str] = []
    query = context
    if not query:
        for message in reversed(history):
            if message.get("role") == "user" and message.get("content"):
                query = message["content"]
                break

    if settings.RAG_ENABLED:
        knowledge_snippets = _collect_relevant_context(query)

    if settings.TAVILY_ENABLED:
        web_snippets = _search_web(query)

    system_content = _build_system_prompt(knowledge_snippets, web_snippets)

    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_content}, *history]

    client = get_client()
    stream = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
