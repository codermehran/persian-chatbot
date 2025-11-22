from django.db import models


class ChatSession(models.Model):
    """Represents a conversation session between the user and the chatbot."""

    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - convenience display
        return self.title or f"Session {self.pk}"


class ChatMessage(models.Model):
    """A single message exchanged in a chat session."""

    class Roles(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        SYSTEM = "system", "System"

    session = models.ForeignKey(ChatSession, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=Roles.choices)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self) -> str:  # pragma: no cover - convenience display
        return f"{self.get_role_display()}: {self.content[:50]}"


class KnowledgeDoc(models.Model):
    """Stores knowledge base documents used to enrich chat responses."""

    text = models.TextField()
    embedding = models.JSONField(blank=True, null=True)
    source = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - convenience display
        return self.source or f"Document {self.pk}"
