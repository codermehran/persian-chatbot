from django.http import HttpResponseBadRequest, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import ChatMessage, ChatSession
from .services import stream_response


def index(request):
    """List chat sessions and provide a button to create a new one."""

    if request.method == "POST":
        session = ChatSession.objects.create(title="گفتگوی جدید")
        return redirect(reverse("chat:chat", args=[session.pk]))

    sessions = ChatSession.objects.order_by("-updated_at", "-created_at")
    return render(request, "chat/index.html", {"sessions": sessions})


def chat_view(request, session_id: int):
    """Render a specific chat session with its message history."""

    session = get_object_or_404(ChatSession, pk=session_id)
    messages = session.messages.all()
    return render(
        request,
        "chat/session.html",
        {
            "session": session,
            "messages": messages,
        },
    )


@require_POST
def send_message_api(request, session_id: int):
    """Stream an assistant reply while persisting both user and assistant messages."""

    session = get_object_or_404(ChatSession, pk=session_id)
    user_message = request.POST.get("message", "").strip()
    if not user_message:
        return HttpResponseBadRequest("Message is required.")

    ChatMessage.objects.create(
        session=session,
        role=ChatMessage.Roles.USER,
        content=user_message,
    )

    history = list(session.messages.values("role", "content"))

    def stream():
        assistant_content = ""
        try:
            for token in stream_response(history, context=user_message):
                assistant_content += token
                yield token
        finally:
            ChatMessage.objects.create(
                session=session,
                role=ChatMessage.Roles.ASSISTANT,
                content=assistant_content,
            )

    return StreamingHttpResponse(stream(), content_type="text/plain; charset=utf-8")
