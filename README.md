# Persian Chatbot

## Project Overview
A Django-based Persian-language chatbot that integrates OpenAI models with optional retrieval-augmented generation (RAG). The app provides a chat interface, supports streaming responses, and can optionally enrich prompts using vector search.

## Prerequisites
- Python 3.11+
- Recommended: a virtual environment (`python -m venv .venv` and activate it for your platform)

## Installation
1. Clone the repository and switch into the project directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Configuration
Create a `.env` file (see the sample instructions below) with the following variables:

| Variable | Description |
| --- | --- |
| `DJANGO_SECRET_KEY` | Secret key used by Django for cryptographic signing. |
| `DJANGO_DEBUG` | Set to `True` for development or `False` for production. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hostnames (e.g., `localhost,127.0.0.1`). |
| `OPENAI_API_KEY` | API key for accessing OpenAI services. |
| `OPENAI_API_BASE` | Custom base URL for OpenAI-compatible endpoints (leave blank for default). |
| `OPENAI_MODEL` | Model name to use for chat completions. |
| `RAG_ENABLED` | `true`/`false` flag to enable or disable retrieval-augmented generation. |
| `DB_ENGINE` | Django database engine (e.g., `django.db.backends.sqlite3`). |
| `DB_NAME` | Database name or path (e.g., `db.sqlite3`). |
| `DB_USER` | Database username (if applicable). |
| `DB_PASSWORD` | Database password (if applicable). |
| `DB_HOST` | Database host (if applicable). |
| `DB_PORT` | Database port (if applicable). |

### Creating the `.env` File
- Copy the sample environment file if provided, or create `.env` manually using the variables above.
- Ensure the `.env` file resides in the project root so Django can load configuration.

## Database Initialization
Run migrations and create a superuser:
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Running the Development Server
Start the Django development server:
```bash
python manage.py runserver
```

## Chat Flow and API Behavior
- Chat requests are handled through the main chatbot view, which can stream token-by-token responses when using the streaming endpoint.
- The streaming endpoint yields incremental tokens until the model response completes, providing a live typing effect in the UI.
- RAG can be toggled with the `RAG_ENABLED` environment variable; when enabled, the system augments prompts with retrieved context before querying the model.

## Frontend Assets and Templates
- Tailwind is loaded via CDN for quick styling in development; static assets resolve through Django's static paths when collected.
- Core templates live under `templates/` with supporting partials in the same directory hierarchy; check `templates/base.html` and related files for layout and chat interface views.
