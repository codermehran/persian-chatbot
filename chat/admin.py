from django.contrib import admin

from .models import ChatMessage, ChatSession, KnowledgeDoc


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at", "updated_at")
    search_fields = ("title",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "short_content", "created_at")
    search_fields = ("content", "session__title")
    list_filter = ("role",)

    @admin.display(description="Content")
    def short_content(self, obj: ChatMessage) -> str:
        return obj.content[:75] + ("..." if len(obj.content) > 75 else "")


@admin.register(KnowledgeDoc)
class KnowledgeDocAdmin(admin.ModelAdmin):
    list_display = ("id", "source", "created_at", "updated_at")
    search_fields = ("source", "text")
