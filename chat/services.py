from collections.abc import Iterable
from typing import Any, Dict, List

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


def _build_system_prompt(snippets: List[str]) -> str:
    base_prompt = (
        "شما یک دستیار فارسی هستید که باید با لحن مودب و مختصر پاسخ دهید. "
        "در صورت وجود دانش زمینه‌ای از پایگاه دانش، آن را به‌صورت خلاصه در پاسخ استفاده کنید."
    )

    if not snippets:
        if settings.RAG_ENABLED:
            return (
                base_prompt
                + " منابع مرتبطی در پایگاه دانش یافت نشد، پس فقط بر اساس مکالمه پاسخ بدهید."
            )
        return base_prompt + " قابلیت RAG غیرفعال است، فقط از تاریخچه مکالمه استفاده کن."

    knowledge_block = "\n\n".join(snippets)
    return base_prompt + f" اطلاعات زیر از پایگاه دانش در دسترس است:\n\n{knowledge_block}"


def stream_response(history: List[Dict[str, str]], context: str | None = None) -> Iterable[str]:
    """Stream a chat completion while optionally enriching with RAG context."""

    snippets: List[str] = []
    if settings.RAG_ENABLED:
        query = context
        if not query:
            for message in reversed(history):
                if message.get("role") == "user" and message.get("content"):
                    query = message["content"]
                    break

        snippets = _collect_relevant_context(query)

    system_content = _build_system_prompt(snippets)

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
