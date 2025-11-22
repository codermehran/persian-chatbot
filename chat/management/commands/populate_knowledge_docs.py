from django.core.management.base import BaseCommand

from chat.models import KnowledgeDoc


class Command(BaseCommand):
    help = "Populate sample knowledge documents for testing and development."

    SAMPLE_DOCS = [
        {
            "source": "getting_started",
            "text": "Welcome to the chatbot! This document explains basic usage and greetings.",
        },
        {
            "source": "faqs",
            "text": "Frequently asked questions about account setup, troubleshooting, and support.",
        },
        {
            "source": "persian_language_tips",
            "text": "Examples of Persian greetings, common phrases, and polite responses for conversations.",
        },
    ]

    def handle(self, *args, **options):
        created_count = 0
        for doc in self.SAMPLE_DOCS:
            _, created = KnowledgeDoc.objects.get_or_create(
                source=doc["source"], defaults={"text": doc["text"]}
            )
            created_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"KnowledgeDoc population complete. Added {created_count} new document(s)."
            )
        )
